# Apache License
# Version 2.0, January 2004
# http://www.apache.org/licenses/
# reference https://github.com/facebookresearch/detectron2/blob/main/detectron2/modeling/backbone/vit.py
# https://github.com/open-mmlab/mmdetection/tree/main/projects/ViTDet/vitdet

import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from timm.models.layers import DropPath, Mlp
import math
from functools import partial
from collections import OrderedDict
import mmengine
from mmengine.runner.checkpoint import CheckpointLoader, load_state_dict
from ._mmlab_utils import load_mmlab_checkpoint
from ._prithvi_utils import init_prithvi
from einops import rearrange
import numpy as np


def get_rel_pos(q_size, k_size, rel_pos):
    """
    Get relative positional embeddings according to the relative positions of
        query and key sizes.
    Args:
        q_size (int): size of query q.
        k_size (int): size of key k.
        rel_pos (Tensor): relative position embeddings (L, C).

    Returns:
        Extracted positional embeddings according to relative positions.
    """
    max_rel_dist = int(2 * max(q_size, k_size) - 1)
    # Interpolate rel pos if needed.
    if rel_pos.shape[0] != max_rel_dist:
        # Interpolate rel pos.
        rel_pos_resized = F.interpolate(
            rel_pos.reshape(1, rel_pos.shape[0], -1).permute(0, 2, 1),
            size=max_rel_dist,
            mode="linear",
        )
        rel_pos_resized = rel_pos_resized.reshape(-1, max_rel_dist).permute(1, 0)
    else:
        rel_pos_resized = rel_pos

    # Scale the coords with short length if shapes for q and k are different.
    q_coords = torch.arange(q_size)[:, None] * max(k_size / q_size, 1.0)
    k_coords = torch.arange(k_size)[None, :] * max(q_size / k_size, 1.0)
    relative_coords = (q_coords - k_coords) + (k_size - 1) * max(q_size / k_size, 1.0)

    return rel_pos_resized[relative_coords.long()]


def add_decomposed_rel_pos(attn, q, rel_pos_h, rel_pos_w, q_size, k_size):
    """
    Calculate decomposed Relative Positional Embeddings.
    Args:
        attn (Tensor): attention map.
        q (Tensor): query q in the attention layer with shape (B, q_h * q_w, C).
        rel_pos_h (Tensor): relative position embeddings (Lh, C) for height axis.
        rel_pos_w (Tensor): relative position embeddings (Lw, C) for width axis.
        q_size (Tuple): spatial sequence size of query q with (q_h, q_w).
        k_size (Tuple): spatial sequence size of key k with (k_h, k_w).

    Returns:
        attn (Tensor): attention map with added relative positional embeddings.
    """
    q_h, q_w = q_size
    k_h, k_w = k_size
    Rh = get_rel_pos(q_h, k_h, rel_pos_h)
    Rw = get_rel_pos(q_w, k_w, rel_pos_w)

    B, _, dim = q.shape
    r_q = q.reshape(B, q_h, q_w, dim)
    rel_h = torch.einsum("bhwc,hkc->bhwk", r_q, Rh)
    rel_w = torch.einsum("bhwc,wkc->bhwk", r_q, Rw)

    attn = (
        attn.view(B, q_h, q_w, k_h, k_w)
        + rel_h[:, :, :, :, None]
        + rel_w[:, :, :, None, :]
    ).view(B, q_h * q_w, k_h * k_w)

    return attn


def window_partition(x, window_size):
    """
    Partition into non-overlapping windows with padding if needed.
    Args:
        x (tensor): input tokens with [B, H, W, C].
        window_size (int): window size.

    Returns:
        windows: windows after partition with [B * num_windows, window_size, window_size, C].
        (Hp, Wp): padded height and width before partition
    """
    B, H, W, C = x.shape

    pad_h = (window_size - H % window_size) % window_size
    pad_w = (window_size - W % window_size) % window_size
    if pad_h > 0 or pad_w > 0:
        x = F.pad(x, (0, 0, 0, pad_w, 0, pad_h))
    Hp, Wp = H + pad_h, W + pad_w

    x = x.view(B, Hp // window_size, window_size, Wp // window_size, window_size, C)
    windows = (
        x.permute(0, 1, 3, 2, 4, 5).contiguous().view(-1, window_size, window_size, C)
    )
    return windows, (Hp, Wp)


def window_unpartition(windows, window_size, pad_hw, hw):
    """
    Window unpartition into original sequences and removing padding.
    Args:
        x (tensor): input tokens with [B * num_windows, window_size, window_size, C].
        window_size (int): window size.
        pad_hw (Tuple): padded height and width (Hp, Wp).
        hw (Tuple): original height and width (H, W) before padding.

    Returns:
        x: unpartitioned sequences with [B, H, W, C].
    """
    Hp, Wp = pad_hw
    H, W = hw
    B = windows.shape[0] // (Hp * Wp // window_size // window_size)
    x = windows.view(
        B, Hp // window_size, Wp // window_size, window_size, window_size, -1
    )
    x = x.permute(0, 1, 3, 2, 4, 5).contiguous().view(B, Hp, Wp, -1)

    if Hp > H or Wp > W:
        x = x[:, :H, :W, :].contiguous()
    return x


def get_abs_pos(abs_pos, has_cls_token, hw, is_plain_vit=True):
    """
    Calculate absolute positional embeddings. If needed, resize embeddings and remove cls_token
        dimension for the original embeddings.
    Args:
        abs_pos (Tensor): absolute positional embeddings with (1, num_position, C).
        has_cls_token (bool): If true, has 1 embedding in abs_pos for cls token.
        hw (Tuple): size of input image tokens.

    Returns:
        Absolute positional embeddings after processing with shape (1, H, W, C)
    """
    h, w = hw
    if has_cls_token:
        abs_pos = abs_pos[:, 1:]
    xy_num = abs_pos.shape[1]
    size = int(math.sqrt(xy_num))
    assert size * size == xy_num

    if size != h or size != w:
        abs_pos = F.interpolate(
            abs_pos.reshape(1, size, size, -1).permute(0, 3, 1, 2),
            size=(h, w),
            mode="bicubic",
            align_corners=False,
        ).permute(0, 2, 3, 1)
    else:
        abs_pos = abs_pos.reshape(1, h, w, -1)

    if is_plain_vit:
        return abs_pos.reshape(1, h * w, -1)
    else:
        return abs_pos


def load_checkpoint_custom(filename, map_location=None, logger=None):
    ckpt = CheckpointLoader.load_checkpoint(filename, map_location, logger)
    if "model" in ckpt.keys():
        ckpt = ckpt["model"]
    if "ema" in ckpt.keys():
        ckpt = ckpt["ema"]["module"]
    return ckpt


mmengine.runner.checkpoint._load_checkpoint = load_checkpoint_custom


class Attention(nn.Module):
    """Multi-head Attention block with relative position embeddings."""

    def __init__(
        self,
        dim,
        num_heads=8,
        qkv_bias=True,
        use_rel_pos=False,
        rel_pos_zero_init=True,
        input_size=None,
    ):
        """
        Args:
            dim (int): Number of input channels.
            num_heads (int): Number of attention heads.
            qkv_bias (bool:  If True, add a learnable bias to query, key, value.
            rel_pos (bool): If True, add relative positional embeddings to the attention map.
            rel_pos_zero_init (bool): If True, zero initialize relative positional parameters.
            input_size (int or None): Input resolution for calculating the relative positional
                parameter size.
        """
        super().__init__()
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = head_dim**-0.5

        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.proj = nn.Linear(dim, dim)

        self.use_rel_pos = use_rel_pos
        if self.use_rel_pos:
            # initialize relative positional embeddings
            self.rel_pos_h = nn.Parameter(torch.zeros(2 * input_size[0] - 1, head_dim))
            self.rel_pos_w = nn.Parameter(torch.zeros(2 * input_size[1] - 1, head_dim))

            if not rel_pos_zero_init:
                nn.init.trunc_normal_(self.rel_pos_h, std=0.02)
                nn.init.trunc_normal_(self.rel_pos_w, std=0.02)

    def forward(self, x):
        if self.use_rel_pos:
            return self.forward_2D(x)
        else:
            B, N, C = x.shape
            qkv = (
                self.qkv(x)
                .reshape(B, N, 3, self.num_heads, C // self.num_heads)
                .permute(2, 0, 3, 1, 4)
            )
            q, k, v = qkv[0], qkv[1], qkv[2]
            x = F.scaled_dot_product_attention(q, k, v, dropout_p=0.0)
            x = rearrange(x, "b h n d -> b n (h d)")
            x = self.proj(x)
            return x

    def forward_2D(self, x):
        B, H, W, _ = x.shape
        # qkv with shape (3, B, nHead, H * W, C)
        qkv = (
            self.qkv(x).reshape(B, H * W, 3, self.num_heads, -1).permute(2, 0, 3, 1, 4)
        )
        # q, k, v with shape (B * nHead, H * W, C)
        q, k, v = qkv.reshape(3, B * self.num_heads, H * W, -1).unbind(0)

        attn = (q * self.scale) @ k.transpose(-2, -1)

        if self.use_rel_pos:
            attn = add_decomposed_rel_pos(
                attn, q, self.rel_pos_h, self.rel_pos_w, (H, W), (H, W)
            )

        attn = attn.softmax(dim=-1)
        x = (
            (attn @ v)
            .view(B, self.num_heads, H, W, -1)
            .permute(0, 2, 3, 1, 4)
            .reshape(B, H, W, -1)
        )
        x = self.proj(x)

        return x


class Block(nn.Module):
    """Transformer blocks with support of window attention"""

    def __init__(
        self,
        dim,
        num_heads,
        mlp_ratio=4.0,
        qkv_bias=True,
        drop_path=0.0,
        norm_layer=nn.LayerNorm,
        act_layer=nn.GELU,
        use_rel_pos=False,
        rel_pos_zero_init=True,
        window_size=0,
        input_size=None,
    ):
        super().__init__()
        self.norm1 = norm_layer(dim)
        self.attn = Attention(
            dim,
            num_heads=num_heads,
            qkv_bias=qkv_bias,
            use_rel_pos=use_rel_pos,
            rel_pos_zero_init=rel_pos_zero_init,
            input_size=input_size if window_size == 0 else (window_size, window_size),
        )

        self.drop_path = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()
        self.norm2 = norm_layer(dim)
        self.mlp = Mlp(
            in_features=dim, hidden_features=int(dim * mlp_ratio), act_layer=act_layer
        )

        self.window_size = window_size

    def forward(self, x):
        shortcut = x
        x = self.norm1(x)
        # Window partition
        if self.window_size > 0:
            H, W = x.shape[1], x.shape[2]
            x, pad_hw = window_partition(x, self.window_size)

        x = self.attn(x)
        # Reverse window partition
        if self.window_size > 0:
            x = window_unpartition(x, self.window_size, pad_hw, (H, W))

        x = shortcut + self.drop_path(x)
        x = x + self.drop_path(self.mlp(self.norm2(x)))

        return x


class PatchEmbed(nn.Module):
    """
    Image to Patch Embedding.
    """

    def __init__(
        self,
        kernel_size=(16, 16),
        stride=(16, 16),
        padding=(0, 0),
        in_chans=3,
        embed_dim=768,
        flatten=False,
    ):
        super().__init__()
        self.flatten = flatten
        self.proj = nn.Conv2d(
            in_chans, embed_dim, kernel_size=kernel_size, stride=stride, padding=padding
        )

    def forward(self, x):
        x = self.proj(x)
        patch_height, patch_width = x.shape[-2:]
        if self.flatten:
            x = x.flatten(2).transpose(1, 2)  # BCHW -> BNC
        else:
            x = x.permute(0, 2, 3, 1)  # BCHW -> BHWC

        return x, patch_height, patch_width


class ViT(nn.Module):
    """
    This module implements Vision Transformer (ViT) backbone in :paper:`vitdet`.
    "Exploring Plain Vision Transformer Backbones for Object Detection",
    https://arxiv.org/abs/2203.16527
    """

    def __init__(
        self,
        img_size,
        in_chans=3,
        patch_size=16,
        embed_dim=768,
        depth=12,
        num_heads=12,
        mlp_ratio=4.0,
        qkv_bias=True,
        drop_path_rate=0.1,
        norm_layer=partial(nn.LayerNorm, eps=1e-6),
        act_layer=nn.GELU,
        use_abs_pos=True,
        use_rel_pos=True,
        rel_pos_zero_init=True,
        window_size=14,
        window_block_indexes=None,
        pretrain_img_size=224,
        pretrain_use_cls_token=True,
        pretrained_path=None,
        pretrained=True,
        backbone_name=None,
        **kwargs,
    ):
        """
        Args:
            img_size (int): Input image size.
            patch_size (int): Patch size.
            in_chans (int): Number of input image channels.
            embed_dim (int): Patch embedding dimension.
            depth (int): Depth of ViT.
            num_heads (int): Number of attention heads in each ViT block.
            mlp_ratio (float): Ratio of mlp hidden dim to embedding dim.
            qkv_bias (bool): If True, add a learnable bias to query, key, value.
            drop_path_rate (float): Stochastic depth rate.
            norm_layer (nn.Module): Normalization layer.
            act_layer (nn.Module): Activation layer.
            use_abs_pos (bool): If True, use absolute positional embeddings.
            use_rel_pos (bool): If True, add relative positional embeddings to the attention map.
            rel_pos_zero_init (bool): If True, zero initialize relative positional parameters.
            window_size (int): Window size for window attention blocks.
            window_block_indexes (list): Indexes for blocks using window attention.
            pretrain_img_size (int): input image size for pretraining models.
            pretrain_use_cls_token (bool): If True, pretrainig models use class token.
        """
        super().__init__()
        self._is_vitdet = True
        self.pretrain_use_cls_token = pretrain_use_cls_token
        self.is_plain_vit = kwargs.get("is_plain_vit", None)
        self.is_clf = kwargs.get("is_clf", None)
        self.patch_size = patch_size
        if window_block_indexes is None:
            # 2, 5, 8 11 for global attention
            window_block_indexes = [0, 1, 3, 4, 6, 7, 9, 10]

        self.qa_idx = None
        self._band_names = kwargs.get("band_names", None)
        self.wavelengths = kwargs.get("wavelengths", None)

        if self._band_names is not None:
            cleaned_bandnames = [
                band_name.lower().replace("_", "").replace(" ", "")
                for band_name in self._band_names
            ]
            if "qa" in cleaned_bandnames:
                self.qa_idx = cleaned_bandnames.index("qa")
                self.wavelengths = (
                    self.wavelengths[: self.qa_idx]
                    + self.wavelengths[self.qa_idx + 1 :]
                )

        if "dofa" in backbone_name:
            from ._dofa_utils import DOFAEmbedding

            self.patch_embed = DOFAEmbedding(
                dynamic_embed_dim=128,
                kernel_size=16,
                embed_dim=embed_dim,
                wavelengths=self.wavelengths,
                flatten=True if self.is_plain_vit else False,
            )
        else:
            self.patch_embed = PatchEmbed(
                kernel_size=(patch_size, patch_size),
                stride=(patch_size, patch_size),
                in_chans=in_chans,
                embed_dim=embed_dim,
                flatten=True if self.is_plain_vit else False,
            )

        if self.is_plain_vit:
            # to keep plain vit
            window_block_indexes = []
            use_rel_pos = False
            self._grid_size = img_size // patch_size
            self._num_tokens = 1 if self.is_clf else 0
            self.pretrain_use_cls_token = True if self.is_clf else False
            num_patches = (self._grid_size) ** 2
            num_patches = num_patches + self._num_tokens
            self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, embed_dim))
        elif use_abs_pos:
            # Initialize absolute positional embedding with pretrain image size.
            num_patches = (pretrain_img_size // patch_size) * (
                pretrain_img_size // patch_size
            )
            num_positions = (num_patches + 1) if pretrain_use_cls_token else num_patches
            self.pos_embed = nn.Parameter(torch.zeros(1, num_positions, embed_dim))
        else:
            self.pos_embed = None

        # stochastic depth decay rule
        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]

        self.blocks = nn.ModuleList(
            [
                Block(
                    dim=embed_dim,
                    num_heads=num_heads,
                    mlp_ratio=mlp_ratio,
                    qkv_bias=qkv_bias,
                    drop_path=dpr[i],
                    norm_layer=norm_layer,
                    act_layer=act_layer,
                    use_rel_pos=use_rel_pos,
                    rel_pos_zero_init=rel_pos_zero_init,
                    window_size=window_size if i in window_block_indexes else 0,
                    input_size=(img_size // patch_size, img_size // patch_size),
                )
                for i in range(depth)
            ]
        )

        if self.is_clf:
            self.norm = norm_layer(embed_dim)
            self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
            self.head = nn.Linear(embed_dim, kwargs.get("num_classes"))

        # last layer output shape
        self.output_shape = dict(channels=embed_dim, stride=patch_size)
        if self.pos_embed is not None:
            nn.init.trunc_normal_(self.pos_embed, std=0.02)

        if pretrained:
            logging.disable(logging.WARNING)
            if backbone_name == "prithvi":
                init_prithvi(self, pretrained_path)
            elif self.is_plain_vit:
                self._init_plain_pretrained(pretrained_path)
            else:
                load_mmlab_checkpoint(self, pretrained_path)
            logging.disable(0)
        else:
            self.apply(self._init_weights)

    def _init_plain_pretrained(self, pretrained_path):
        state_dict = load_checkpoint_custom(
            pretrained_path,
            map_location=torch.device("cpu"),
            logger=logging.getLogger(),
        )
        for k, v in state_dict.items():
            if k == "pos_embed" and v.shape != self.pos_embed.shape:
                # get feature size(height, width)
                pretrained_grid_size = int(np.sqrt(v.shape[1]))
                # get number of tokens
                num_tokens = v.shape[1] - pretrained_grid_size**2
                posemb_tok, posemb_grid = v[:, :num_tokens], v[0, num_tokens:]
                posemb_grid = posemb_grid.reshape(
                    1, pretrained_grid_size, pretrained_grid_size, -1
                ).permute(0, 3, 1, 2)
                posemb_grid = F.interpolate(
                    posemb_grid,
                    size=(self._grid_size, self._grid_size),
                    mode="bilinear",
                )
                posemb_grid = posemb_grid.permute(0, 2, 3, 1).reshape(
                    1, self._grid_size**2, -1
                )
                posemb_tok = posemb_tok[:, : self._num_tokens, :]
                posemb = torch.cat([posemb_tok, posemb_grid], dim=1)
                state_dict[k] = posemb

        load_state_dict(self, state_dict, False, logging.getLogger())

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.trunc_normal_(m.weight, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def forward(self, x):
        if self.qa_idx is not None:
            x = torch.cat([x[:, : self.qa_idx], x[:, self.qa_idx + 1 :]], dim=1)
        if x.shape[-2] < self.patch_size or x.shape[-1] < self.patch_size:
            h = max(x.shape[-2], self.patch_size * 2)
            w = max(x.shape[-1], self.patch_size * 2)
            x = F.interpolate(x, (h, w), mode="bilinear", align_corners=False)
        x, patch_height, patch_width = self.patch_embed(x)

        if self.pos_embed is not None:
            x = x + get_abs_pos(
                self.pos_embed,
                self.pretrain_use_cls_token,
                (patch_height, patch_width),
                self.is_plain_vit,
            )

        if self.is_clf:
            cls_token = self.cls_token + self.pos_embed[:, :1, :]
            cls_tokens = cls_token.expand(x.shape[0], -1, -1)
            x = torch.cat((cls_tokens, x), dim=1)

        no_of_block = len(self.blocks)
        for idx, blk in enumerate(self.blocks):
            x = blk(x)
            if self.is_clf and (idx == no_of_block - 3):
                x_grad_cam = x

        if self.is_clf:
            x = self.norm(x)
            return x_grad_cam, x[:, 0]

        if self.is_plain_vit:
            batch_size, _, hidden_dim = x.shape
            x = x.permute(0, 2, 1).reshape(
                batch_size, hidden_dim, patch_height, patch_width
            )
        else:
            x = x.permute(0, 3, 1, 2)

        return x


class LayerNorm2D(nn.Module):
    """
    A LayerNorm variant, popularized by Transformers, that performs point-wise mean and
    variance normalization over the channel dimension for inputs that have shape
    (batch_size, channels, height, width).
    https://github.com/facebookresearch/ConvNeXt/blob/d1fa8f6fef0a165b27399986cc2bdacc92777e40/models/convnext.py#L119
    """

    def __init__(self, normalized_shape, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))
        self.eps = eps
        self.normalized_shape = (normalized_shape,)

    def forward(self, x):
        u = x.mean(1, keepdim=True)
        s = (x - u).pow(2).mean(1, keepdim=True)
        x = (x - u) / torch.sqrt(s + self.eps)
        x = self.weight[:, None, None] * x + self.bias[:, None, None]
        return x


class ViTUpsample(nn.Module):
    def __init__(self, backbone):
        super().__init__()
        self.backbone = backbone
        in_chans = backbone.output_shape["channels"]
        self.scale_factors = 4.0
        out_stride = backbone.output_shape["stride"] // self.scale_factors
        self.output_shape = dict(channels=in_chans, stride=out_stride)
        upsameple_layers = [
            nn.ConvTranspose2d(in_chans, in_chans, kernel_size=2, stride=2),
            LayerNorm2D(in_chans),
            nn.GELU(),
            nn.ConvTranspose2d(in_chans, in_chans, kernel_size=2, stride=2),
            nn.Conv2d(in_chans, in_chans, kernel_size=1, bias=False),
            LayerNorm2D(in_chans),
            nn.Conv2d(in_chans, in_chans, kernel_size=3, padding=1, bias=False),
            LayerNorm2D(in_chans),
        ]
        self.upsample = nn.Sequential(*upsameple_layers)

    def forward(self, x):
        return self.upsample(self.backbone(x))


class SimpleFeaturePyramid(nn.Module):
    """
    This module implements SimpleFeaturePyramid in :paper:`vitdet`.
    It creates pyramid features built on top of the input feature map.
    """

    def __init__(
        self,
        backbone,
        out_channels=256,
        scale_factors=(4.0, 2.0, 1.0, 0.5),
        top_block=nn.MaxPool2d(kernel_size=1, stride=2, padding=0),
    ):
        """
        Args:
            backbone: module representing the subnetwork backbone.
            out_channels (int): number of channels in the output feature maps.
            scale_factors (list[float]): list of scaling factors to upsample or downsample
                the input features for creating pyramid features.
            top_block (nn.Module or None): if provided, an extra operation will
                be performed on the output of the last (smallest resolution)
                pyramid output, and the result will extend the result list. The top_block
                further downsamples the feature map.
        """
        super().__init__()
        self.backbone = backbone
        self.out_channels = out_channels
        self.scale_factors = scale_factors
        dim = backbone.output_shape["channels"]
        self.fpn_stages = nn.ModuleList()
        self.stage_names = list(range(len(scale_factors)))
        for scale in scale_factors:
            out_dim = dim
            if scale == 4.0:
                layers = [
                    nn.ConvTranspose2d(dim, dim // 2, kernel_size=2, stride=2),
                    LayerNorm2D(dim // 2),
                    nn.GELU(),
                    nn.ConvTranspose2d(dim // 2, dim // 4, kernel_size=2, stride=2),
                ]
                out_dim = dim // 4
            elif scale == 2.0:
                layers = [nn.ConvTranspose2d(dim, dim // 2, kernel_size=2, stride=2)]
                out_dim = dim // 2
            elif scale == 1.0:
                layers = []
            elif scale == 0.5:
                layers = [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                raise NotImplementedError(f"scale_factor={scale} is not supported yet.")

            layers.extend(
                [
                    nn.Conv2d(out_dim, out_channels, kernel_size=1, bias=False),
                    LayerNorm2D(out_channels),
                    nn.Conv2d(
                        out_channels, out_channels, kernel_size=3, padding=1, bias=False
                    ),
                    LayerNorm2D(out_channels),
                ]
            )
            layers = nn.Sequential(*layers)
            self.fpn_stages.append(layers)

        self.top_block = top_block
        if top_block is not None:
            self.stage_names.append("pool")

    def forward(self, x):
        """
        Args:
            x: Tensor of shape (N,C,H,W).

        Returns:
            dict[str->Tensor]:mapping from feature map name to pyramid feature map tensor
            in high to low resolution order.
        """
        features = self.backbone(x)
        results = []
        for stage in self.fpn_stages:
            results.append(stage(features))

        if self.top_block is not None:
            results.append(self.top_block(results[-1]))

        return OrderedDict([(str(k), v) for k, v in zip(self.stage_names, results)])


class BackboneFastai(nn.Module):
    def __init__(self, backbone, is_fpn=False):
        super().__init__()
        if is_fpn:
            self.backbone_fpn = SimpleFeaturePyramid(backbone=backbone)
        else:
            self.backbone_fpn = ViTUpsample(backbone=backbone)
        if hasattr(backbone, "_is_vitdet"):
            self.backbone_fpn._is_vitdet = backbone._is_vitdet
            self._is_vitdet = backbone._is_vitdet

        # create dummy layer to set cut=1 in create_body of fastai
        self.dummy = nn.MaxPool2d(kernel_size=2)

    def forward(self, x):
        return self.backbone_fpn(x)
