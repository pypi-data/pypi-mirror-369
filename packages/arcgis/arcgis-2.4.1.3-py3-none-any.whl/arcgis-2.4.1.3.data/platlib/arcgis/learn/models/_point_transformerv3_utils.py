# MIT License

# Copyright (c) 2023 Pointcept

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# Base on https://github.com/Pointcept/PointTransformerV3

from addict import Dict
import math
import torch
import torch.nn as nn
import spconv.pytorch as spconv
import torch_scatter
from timm.models.layers import DropPath, Mlp
from collections import OrderedDict
from .._utils.pointcloud_serialization import PointBatchPreprocess as Point
from .._utils.pointcloud_serialization import offset2bincount
from .._utils.pointcloud_data import pad_tensor


class PointModule(nn.Module):
    r"""PointModule
    placeholder, all module subclass from this will take Point in PointSequential.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PointSequential(PointModule):
    r"""A sequential container.
    Modules will be added to it in the order they are passed in the constructor.
    Alternatively, an ordered dict of modules can also be passed in.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        if len(args) == 1 and isinstance(args[0], OrderedDict):
            for key, module in args[0].items():
                self.add_module(key, module)
        else:
            for idx, module in enumerate(args):
                self.add_module(str(idx), module)
        for name, module in kwargs.items():
            if name in self._modules:
                raise ValueError("name exists.")
            self.add_module(name, module)

    def __getitem__(self, idx):
        if not (-len(self) <= idx < len(self)):
            raise IndexError("index {} is out of range".format(idx))
        if idx < 0:
            idx += len(self)
        it = iter(self._modules.values())
        for i in range(idx):
            next(it)
        return next(it)

    def __len__(self):
        return len(self._modules)

    def add(self, module, name=None):
        if name is None:
            name = str(len(self._modules))
            if name in self._modules:
                raise KeyError("name exists")
        self.add_module(name, module)

    def forward(self, input):
        for k, module in self._modules.items():
            # Point module
            if isinstance(module, PointModule):
                input = module(input)
            # Spconv module
            elif spconv.modules.is_spconv_module(module):
                if isinstance(input, Point):
                    input.sparse_conv_feat = module(input.sparse_conv_feat)
                    input.feat = input.sparse_conv_feat.features
                else:
                    input = module(input)
            # PyTorch module
            else:
                if isinstance(input, Point):
                    input.feat = module(input.feat)
                    if "sparse_conv_feat" in input.keys():
                        input.sparse_conv_feat = input.sparse_conv_feat.replace_feature(
                            input.feat
                        )
                elif isinstance(input, spconv.SparseConvTensor):
                    if input.indices.shape[0] != 0:
                        input = input.replace_feature(module(input.features))
                else:
                    input = module(input)
        return input


class RPE(torch.nn.Module):
    def __init__(self, patch_size, num_heads):
        super().__init__()
        self.patch_size = patch_size
        self.num_heads = num_heads
        self.pos_bnd = int((4 * patch_size) ** (1 / 3) * 2)
        self.rpe_num = 2 * self.pos_bnd + 1
        self.rpe_table = torch.nn.Parameter(torch.zeros(3 * self.rpe_num, num_heads))
        torch.nn.init.trunc_normal_(self.rpe_table, std=0.02)

    def forward(self, coord):
        idx = (
            coord.clamp(-self.pos_bnd, self.pos_bnd)  # clamp into bnd
            + self.pos_bnd  # relative position to positive index
            + torch.arange(3, device=coord.device) * self.rpe_num  # x, y, z stride
        )
        out = self.rpe_table.index_select(0, idx.reshape(-1))
        out = out.view(idx.shape + (-1,)).sum(3)
        out = out.permute(0, 3, 1, 2)  # (N, K, K, H) -> (N, H, K, K)
        return out


class SerializedAttention(PointModule):
    def __init__(
        self,
        channels,
        num_heads,
        patch_size,
        qkv_bias=True,
        attn_drop=0.0,
        proj_drop=0.0,
        order_index=0,
        enable_rpe=False,
        enable_flash=True,
    ):
        super().__init__()
        self.channels = channels
        self.num_heads = num_heads
        self.scale = (channels // num_heads) ** -0.5
        self.order_index = order_index
        self.enable_rpe = enable_rpe
        self.enable_flash = enable_flash

        # patch size will auto set to the min number of patch_size_max
        # and number of points in a batch during training
        self.patch_size_max = patch_size
        self.patch_size = 0
        self.attn_drop = torch.nn.Dropout(attn_drop)

        self.qkv = torch.nn.Linear(channels, channels * 3, bias=qkv_bias)
        self.proj = torch.nn.Linear(channels, channels)
        self.proj_drop = torch.nn.Dropout(proj_drop)
        self.softmax = torch.nn.Softmax(dim=-1)
        self.rpe = RPE(patch_size, num_heads) if self.enable_rpe else None

    @torch.no_grad()
    def get_rel_pos(self, point, order):
        K = self.patch_size
        rel_pos_key = f"rel_pos_{self.order_index}"
        if rel_pos_key not in point.keys():
            grid_coord = point.grid_coord[order]
            grid_coord = grid_coord.reshape(-1, K, 3)
            point[rel_pos_key] = grid_coord.unsqueeze(2) - grid_coord.unsqueeze(1)
        return point[rel_pos_key]

    @torch.no_grad()
    def get_padding_and_inverse(self, point):
        pad_key = "pad"
        unpad_key = "unpad"
        if pad_key not in point.keys() or unpad_key not in point.keys():
            offset = point.offset
            bincount = offset2bincount(offset)
            bincount_pad = (
                torch.div(
                    bincount + self.patch_size - 1,
                    self.patch_size,
                    rounding_mode="trunc",
                )
                * self.patch_size
            )
            # only pad point when num of points larger than patch_size
            mask_pad = bincount > self.patch_size
            bincount_pad = ~mask_pad * bincount + mask_pad * bincount_pad
            _offset = nn.functional.pad(offset, (1, 0))
            _offset_pad = nn.functional.pad(torch.cumsum(bincount_pad, dim=0), (1, 0))
            pad = torch.arange(_offset_pad[-1], device=offset.device)
            unpad = torch.arange(_offset[-1], device=offset.device)
            for i in range(len(offset)):
                unpad[_offset[i] : _offset[i + 1]] += _offset_pad[i] - _offset[i]
                if bincount[i] != bincount_pad[i]:
                    pad[
                        _offset_pad[i + 1]
                        - self.patch_size
                        + (bincount[i] % self.patch_size) : _offset_pad[i + 1]
                    ] = pad[
                        _offset_pad[i + 1]
                        - 2 * self.patch_size
                        + (bincount[i] % self.patch_size) : _offset_pad[i + 1]
                        - self.patch_size
                    ]
                pad[_offset_pad[i] : _offset_pad[i + 1]] -= _offset_pad[i] - _offset[i]
            point[pad_key] = pad
            point[unpad_key] = unpad
        return point[pad_key], point[unpad_key]

    def forward(self, point):

        self.patch_size = min(
            offset2bincount(point.offset).min().tolist(), self.patch_size_max
        )

        H = self.num_heads
        K = self.patch_size
        C = self.channels

        pad, unpad = self.get_padding_and_inverse(point)

        order = point.serialized_order[self.order_index][pad]
        inverse = unpad[point.serialized_inverse[self.order_index]]

        # padding and reshape feat and batch for serialized point patch
        qkv = self.qkv(point.feat)[order]

        # encode and reshape qkv: (N', K, 3, H, C') => (3, N', H, K, C')
        q, k, v = qkv.reshape(-1, K, 3, H, C // H).permute(2, 0, 3, 1, 4).unbind(dim=0)
        if self.enable_flash:
            feat = (
                nn.functional.scaled_dot_product_attention(q.half(), k.half(), v.half())
                .transpose(1, 2)
                .reshape(-1, C)
                .float()
            )
        else:
            attn = (q * self.scale) @ k.transpose(-2, -1)  # (N', H, K, K)
            if self.enable_rpe:
                attn = attn + self.rpe(self.get_rel_pos(point, order))
            attn = self.softmax(attn)
            attn = self.attn_drop(attn).to(qkv.dtype)
            feat = (attn @ v).transpose(1, 2).reshape(-1, C)
        feat = feat[inverse]

        # ffn
        feat = self.proj(feat)
        feat = self.proj_drop(feat)
        point.feat = feat
        return point


class Block(PointModule):
    def __init__(
        self,
        channels,
        num_heads,
        patch_size=48,
        mlp_ratio=4.0,
        qkv_bias=True,
        attn_drop=0.0,
        proj_drop=0.0,
        drop_path=0.0,
        norm_layer=nn.LayerNorm,
        act_layer=nn.GELU,
        order_index=0,
        cpe_indice_key=None,
        enable_rpe=False,
        enable_flash=True,
    ):
        super().__init__()
        self.channels = channels

        self.cpe = PointSequential(
            spconv.SubMConv3d(
                channels,
                channels,
                kernel_size=3,
                bias=True,
                indice_key=cpe_indice_key,
            ),
            nn.Linear(channels, channels),
            norm_layer(channels),
        )

        self.norm1 = PointSequential(norm_layer(channels))
        self.attn = SerializedAttention(
            channels=channels,
            patch_size=patch_size,
            num_heads=num_heads,
            qkv_bias=qkv_bias,
            attn_drop=attn_drop,
            proj_drop=proj_drop,
            order_index=order_index,
            enable_rpe=enable_rpe,
            enable_flash=enable_flash,
        )
        self.norm2 = PointSequential(norm_layer(channels))
        self.mlp = PointSequential(
            Mlp(
                in_features=channels,
                hidden_features=int(channels * mlp_ratio),
                out_features=channels,
                act_layer=act_layer,
                drop=proj_drop,
            )
        )
        self.drop_path = PointSequential(
            DropPath(drop_path) if drop_path > 0.0 else nn.Identity()
        )

    def forward(self, point: Point):
        shortcut = point.feat
        point = self.cpe(point)
        point.feat = shortcut + point.feat
        shortcut = point.feat
        point = self.norm1(point)
        point = self.drop_path(self.attn(point))
        point.feat = shortcut + point.feat
        shortcut = point.feat
        point = self.norm2(point)
        point = self.drop_path(self.mlp(point))
        point.feat = shortcut + point.feat
        point.sparse_conv_feat = point.sparse_conv_feat.replace_feature(point.feat)
        return point


class DetectionPooling(PointModule):
    def __init__(
        self,
        in_channels,
        out_channels,
        stride=2,
        **kwargs,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.order = kwargs.get("order", None)
        if stride == 1:
            sparse_layer = spconv.SubMConv3d
        else:
            sparse_layer = spconv.SparseConv3d
        self.proj = PointSequential(
            sparse_layer(
                in_channels,
                out_channels,
                kernel_size=3,
                stride=stride,
                padding=1,
                bias=False,
                indice_key=kwargs.get("indice_key", None),
            ),
            nn.BatchNorm1d(out_channels, eps=1e-3, momentum=0.01),
            nn.GELU(),
        )

    def forward(self, point: Point):
        point = self.proj(point)
        # features will be at random location for each batch
        batch = point.sparse_conv_feat.indices[:, 0]
        # sort batch and get thier idx for sorting the features
        batch, batch_idx = torch.sort(batch)
        features = point.sparse_conv_feat.features[batch_idx]
        grid_coord = point.sparse_conv_feat.indices[:, [1, 2, 3]][batch_idx]
        sparse_shape = point.sparse_conv_feat.spatial_shape
        point_dict = Dict(
            feat=features, grid_coord=grid_coord, batch=batch, sparse_shape=sparse_shape
        )
        point = Point(point_dict)
        point.serialization(order=self.order)
        point.sparsify()
        return point


class SerializedPooling(PointModule):
    def __init__(
        self,
        in_channels,
        out_channels,
        stride=2,
        **kwargs,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.is_detection = kwargs.get("is_detection", False)

        assert stride == 2 ** (math.ceil(stride) - 1).bit_length()  # 2, 4, 8
        self.stride = stride

        self.proj = nn.Linear(in_channels, out_channels)
        self.norm = PointSequential(
            nn.BatchNorm1d(out_channels, eps=1e-3, momentum=0.01)
        )
        self.act = PointSequential(nn.GELU())

    def forward(self, point: Point):
        pooling_depth = (math.ceil(self.stride) - 1).bit_length()
        if pooling_depth > point.serialized_depth:
            pooling_depth = 0

        code = point.serialized_code >> pooling_depth * 3
        _, cluster, counts = torch.unique(
            code[0],
            sorted=True,
            return_inverse=True,
            return_counts=True,
        )
        # indices of point sorted by cluster, for torch_scatter.segment_csr
        _, indices = torch.sort(cluster)
        # index pointer for sorted point, for torch_scatter.segment_csr
        idx_ptr = torch.cat([counts.new_zeros(1), torch.cumsum(counts, dim=0)])
        # head_indices of each cluster, for reduce attr e.g. code, batch
        head_indices = indices[idx_ptr[:-1]]
        # generate down code, order, inverse
        code = code[:, head_indices]
        order = torch.argsort(code)
        inverse = torch.zeros_like(order).scatter_(
            dim=1,
            index=order,
            src=torch.arange(0, code.shape[1], device=order.device).repeat(
                code.shape[0], 1
            ),
        )

        # randomly shuffle orders of serialized code in each attention layers
        perm = torch.randperm(code.shape[0])
        code = code[perm]
        order = order[perm]
        inverse = inverse[perm]

        # collect information
        point_dict = Dict(
            feat=torch_scatter.segment_csr(
                self.proj(point.feat)[indices], idx_ptr, reduce="max"
            ),
            coord=torch_scatter.segment_csr(
                point.coord[indices], idx_ptr, reduce="mean"
            ),
            grid_coord=point.grid_coord[head_indices] >> pooling_depth,
            serialized_code=code,
            serialized_order=order,
            serialized_inverse=inverse,
            serialized_depth=point.serialized_depth - pooling_depth,
            batch=point.batch[head_indices],
        )

        point_dict["pooling_inverse"] = cluster
        point_dict["pooling_parent"] = point
        point = Point(point_dict)
        point = self.norm(point)
        point = self.act(point)
        if self.is_detection:
            point.sparsify(pad=0)
        else:
            point.sparsify()
        return point


class SerializedUnpooling(PointModule):
    def __init__(
        self,
        in_channels,
        skip_channels,
        out_channels,
    ):
        super().__init__()
        self.proj = PointSequential(
            nn.Linear(in_channels, out_channels),
            nn.BatchNorm1d(out_channels, eps=1e-3, momentum=0.01),
            nn.GELU(),
        )
        self.proj_skip = PointSequential(
            nn.Linear(skip_channels, out_channels),
            nn.BatchNorm1d(out_channels, eps=1e-3, momentum=0.01),
            nn.GELU(),
        )

    def forward(self, point):
        parent = point.pop("pooling_parent")
        inverse = point.pop("pooling_inverse")
        point = self.proj(point)
        parent = self.proj_skip(parent)
        parent.feat = parent.feat + point.feat[inverse]
        return parent


class Embedding(PointModule):
    def __init__(
        self,
        in_channels,
        embed_channels,
    ):
        super().__init__()
        self.stem = PointSequential(
            spconv.SubMConv3d(
                in_channels,
                embed_channels,
                kernel_size=5,
                padding=1,
                bias=False,
                indice_key="stem",
            ),
            nn.BatchNorm1d(embed_channels, eps=1e-3, momentum=0.01),
            nn.GELU(),
        )

    def forward(self, point: Point):
        point = self.stem(point)
        return point


class PTV3Backbone(PointModule):
    def __init__(
        self,
        in_channels=6,
        enc_depths=(2, 2, 2, 6, 2),
        enc_channels=(32, 64, 128, 256, 512),
        enc_num_head=(2, 4, 8, 16, 32),
        dec_depths=(2, 2, 2, 2),
        dec_channels=(64, 64, 128, 256),
        dec_num_head=(4, 4, 8, 16),
        sub_sampling_ratio=2,
        seq_len=1024,
        **kwargs,
    ):
        super().__init__()
        self.num_stages = len(enc_depths)
        self.order = ["z", "z-trans", "hilbert", "hilbert-trans"]
        self.cls_mode = kwargs.get("cls_mode", False)
        self.out_channels = dec_channels[0]

        self.embedding = Embedding(
            in_channels=in_channels,
            embed_channels=enc_channels[0],
        )

        # encoder
        enc_drop_path = [x.item() for x in torch.linspace(0, 0.3, sum(enc_depths))]
        if kwargs.get("detection_pooling", False):
            pooling_layer = DetectionPooling
        else:
            pooling_layer = SerializedPooling
        self.enc = PointSequential()
        for s in range(self.num_stages):
            enc_drop_path_ = enc_drop_path[
                sum(enc_depths[:s]) : sum(enc_depths[: s + 1])
            ]
            enc = PointSequential()
            if s > 0:
                enc.add(
                    pooling_layer(
                        in_channels=enc_channels[s - 1],
                        out_channels=enc_channels[s],
                        stride=sub_sampling_ratio,
                        indice_key=f"downsample{s}",
                        order=self.order,
                        is_detection=kwargs.get("is_detection", False),
                    ),
                    name="down",
                )
            for i in range(enc_depths[s]):
                enc.add(
                    Block(
                        channels=enc_channels[s],
                        num_heads=enc_num_head[s],
                        patch_size=seq_len,
                        drop_path=enc_drop_path_[i],
                        order_index=i % len(self.order),
                        cpe_indice_key=f"stage{s}",
                        enable_rpe=kwargs.get("enable_rpe", False),
                        enable_flash=kwargs.get("enable_flash", True),
                    ),
                    name=f"block{i}",
                )
            if len(enc) != 0:
                self.enc.add(module=enc, name=f"enc{s}")

        # decoder
        if not self.cls_mode:
            dec_drop_path = [x.item() for x in torch.linspace(0, 0.3, sum(dec_depths))]
            self.dec = PointSequential()
            dec_channels = list(dec_channels) + [enc_channels[-1]]
            for s in reversed(range(self.num_stages - 1)):
                dec_drop_path_ = dec_drop_path[
                    sum(dec_depths[:s]) : sum(dec_depths[: s + 1])
                ]
                dec_drop_path_.reverse()
                dec = PointSequential()
                dec.add(
                    SerializedUnpooling(
                        in_channels=dec_channels[s + 1],
                        skip_channels=enc_channels[s],
                        out_channels=dec_channels[s],
                    ),
                    name="up",
                )
                for i in range(dec_depths[s]):
                    dec.add(
                        Block(
                            channels=dec_channels[s],
                            num_heads=dec_num_head[s],
                            patch_size=seq_len,
                            drop_path=dec_drop_path_[i],
                            order_index=i % len(self.order),
                            cpe_indice_key=f"stage{s}",
                            enable_rpe=kwargs.get("enable_rpe", False),
                            enable_flash=kwargs.get("enable_flash", True),
                        ),
                        name=f"block{i}",
                    )
                self.dec.add(module=dec, name=f"dec{s}")

    def forward(self, data_dict):

        point = Point(data_dict)
        point.serialization(order=self.order)
        point.sparsify()

        point = self.embedding(point)
        point = self.enc(point)
        if not self.cls_mode:
            point = self.dec(point)
        return point


class PointTransformerV3Seg(nn.Module):
    def __init__(self, in_channels, num_classes, max_points, **kwargs):
        super().__init__()
        self.backbone = PTV3Backbone(
            in_channels=in_channels,
            sub_sampling_ratio=kwargs.get("sub_sampling_ratio", 2),
            seq_len=kwargs.get("seq_len", 1024),
            enable_flash=kwargs.get("enable_torch_attention", True),
            enable_rpe=kwargs.get("enable_rpe", False),
        )
        self.seg_head = nn.Linear(self.backbone.out_channels, num_classes)
        self.max_points = max_points

    def forward(self, input_dict):
        output = dict(targets=input_dict.get("segment"))
        point = Point(input_dict)
        point = self.backbone(point)

        seg_logits = self.seg_head(point.feat)
        if not self.training:
            return self.target_reshape(seg_logits, input_dict["offset"])
        output["seg_logits"] = seg_logits
        return output

    def target_reshape(self, targets, offset):
        device = targets.device
        offset = [0] + offset.tolist()
        reshap_targets = []
        for idx in range(len(offset) - 1):
            reshap_targets.append(
                pad_tensor(
                    targets[offset[idx] : offset[idx + 1]].detach().cpu(),
                    max_points=self.max_points,
                )[0]
            )
        return torch.stack(reshap_targets).to(device)
