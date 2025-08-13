# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from functools import lru_cache

import numpy as np
import cv2
import torch
from torch import nn
import torch.nn as nn
from timm.models.vision_transformer import Block, trunc_normal_
import numpy as np
import math
import torch.nn.functional as F
from timm.models.layers.helpers import to_2tuple


# --------------------------------------------------------
# 2D sine-cosine position embedding
# References:
# Transformer: https://github.com/tensorflow/models/blob/master/official/nlp/transformer/model_utils.py
# MoCo v3: https://github.com/facebookresearch/moco-v3
# --------------------------------------------------------

from torch import nn as nn

from timm.models.layers.helpers import to_2tuple


class PatchEmbed(nn.Module):
    """2D Image to Patch Embedding"""

    def __init__(
        self,
        img_size=224,
        patch_size=16,
        in_chans=3,
        embed_dim=768,
        norm_layer=None,
        flatten=True,
    ):
        super().__init__()
        img_size = to_2tuple(img_size)
        patch_size = to_2tuple(patch_size)
        self.img_size = img_size
        self.patch_size = patch_size
        self.grid_size = (img_size[0] // patch_size[0], img_size[1] // patch_size[1])
        self.num_patches = self.grid_size[0] * self.grid_size[1]
        self.flatten = flatten

        self.proj = nn.Conv2d(
            in_chans, embed_dim, kernel_size=patch_size, stride=patch_size
        )
        self.norm = norm_layer(embed_dim) if norm_layer else nn.Identity()

    def forward(self, x):
        B, C, H, W = x.shape
        assert (
            H == self.img_size[0] and W == self.img_size[1]
        ), f"Input image size ({H}*{W}) doesn't match model ({self.img_size[0]}*{self.img_size[1]})."
        x = self.proj(x)
        # print("proj", x)
        if self.flatten:
            x = x.flatten(2).transpose(1, 2)  # BCHW -> BNC
        x = self.norm(x)
        return x


def get_2d_sincos_pos_embed(embed_dim, grid_size_h, grid_size_w, cls_token=False):
    """
    grid_size: int of the grid height and width
    return:
    pos_embed: [grid_size*grid_size, embed_dim] or [1+grid_size*grid_size, embed_dim] (w/ or w/o cls_token)
    """
    grid_h = np.arange(grid_size_h, dtype=np.float32)
    grid_w = np.arange(grid_size_w, dtype=np.float32)
    grid = np.meshgrid(grid_w, grid_h)  # here w goes first
    grid = np.stack(grid, axis=0)

    grid = grid.reshape([2, 1, grid_size_h, grid_size_w])
    pos_embed = get_2d_sincos_pos_embed_from_grid(embed_dim, grid)
    if cls_token:
        pos_embed = np.concatenate([np.zeros([1, embed_dim]), pos_embed], axis=0)
    return pos_embed


def get_2d_sincos_pos_embed_from_grid(embed_dim, grid):
    assert embed_dim % 2 == 0

    # use half of dimensions to encode grid_h
    emb_h = get_1d_sincos_pos_embed_from_grid(embed_dim // 2, grid[0])  # (H*W, D/2)
    emb_w = get_1d_sincos_pos_embed_from_grid(embed_dim // 2, grid[1])  # (H*W, D/2)

    emb = np.concatenate([emb_h, emb_w], axis=1)  # (H*W, D)
    return emb


def get_1d_sincos_pos_embed_from_grid(embed_dim, pos):
    """
    embed_dim: output dimension for each position
    pos: a list of positions to be encoded: size (M,)
    out: (M, D)
    """
    assert embed_dim % 2 == 0
    omega = np.arange(embed_dim // 2, dtype=np.float64)
    omega /= embed_dim / 2.0
    omega = 1.0 / 10000**omega  # (D/2,)

    pos = pos.reshape(-1)  # (M,)
    out = np.einsum("m,d->md", pos, omega)  # (M, D/2), outer product

    emb_sin = np.sin(out)  # (M, D/2)
    emb_cos = np.cos(out)  # (M, D/2)

    emb = np.concatenate([emb_sin, emb_cos], axis=1)  # (M, D)
    return emb


# --------------------------------------------------------
# Interpolate position embeddings for high-resolution
# References:
# DeiT: https://github.com/facebookresearch/deit
# --------------------------------------------------------
def interpolate_pos_embed(model, checkpoint_model, new_size=(64, 128)):
    if "net.pos_embed" in checkpoint_model:
        pos_embed_checkpoint = checkpoint_model["net.pos_embed"]
        embedding_size = pos_embed_checkpoint.shape[-1]
        orig_num_patches = pos_embed_checkpoint.shape[-2]
        patch_size = model.patch_size
        w_h_ratio = 2
        orig_h = int((orig_num_patches // w_h_ratio) ** 0.5)
        orig_w = w_h_ratio * orig_h
        orig_size = (orig_h, orig_w)
        new_size = (new_size[0] // patch_size, new_size[1] // patch_size)
        if orig_size[0] != new_size[0]:
            print(
                "Interpolate PEs from %dx%d to %dx%d"
                % (orig_size[0], orig_size[1], new_size[0], new_size[1])
            )
            pos_tokens = pos_embed_checkpoint.reshape(
                -1, orig_size[0], orig_size[1], embedding_size
            ).permute(0, 3, 1, 2)
            new_pos_tokens = torch.nn.functional.interpolate(
                pos_tokens,
                size=(new_size[0], new_size[1]),
                mode="bicubic",
                align_corners=False,
            )
            new_pos_tokens = new_pos_tokens.permute(0, 2, 3, 1).flatten(1, 2)
            checkpoint_model["net.pos_embed"] = new_pos_tokens


def interpolate_channel_embed(checkpoint_model, new_len):
    if "net.channel_embed" in checkpoint_model:
        channel_embed_checkpoint = checkpoint_model["net.channel_embed"]
        old_len = channel_embed_checkpoint.shape[1]
        if new_len <= old_len:
            checkpoint_model["net.channel_embed"] = channel_embed_checkpoint[
                :, :new_len
            ]


def _get_conv2d_weights(
    in_channels,
    out_channels,
    kernel_size,
):
    weight = torch.empty(out_channels, in_channels, *kernel_size)
    return weight


def _get_conv2d_biases(out_channels):
    bias = torch.empty(out_channels)
    return bias


class ParallelVarPatchEmbed(nn.Module):
    """Variable to Patch Embedding with multiple variables in a single kernel. Key idea is to use Grouped Convolutions.

    Args:
        max_vars (int): Maximum number of variables
        img_size (int): Image size
        patch_size (int): Patch size
        embed_dim (int): Embedding dimension
        norm_layer (nn.Module, optional): Normalization layer. Defaults to None.
        flatten (bool, optional): Flatten the output. Defaults to True.
    """

    def __init__(
        self,
        max_vars: int,
        img_size,
        patch_size,
        embed_dim,
        norm_layer=None,
        flatten=True,
    ):
        super().__init__()
        self.max_vars = max_vars
        self.img_size = to_2tuple(img_size)
        self.patch_size = to_2tuple(patch_size)
        self.grid_size = (
            img_size[0] // self.patch_size[0],
            img_size[1] // self.patch_size[1],
        )
        self.num_patches = self.grid_size[0] * self.grid_size[1]
        self.flatten = flatten

        grouped_weights = torch.stack(
            [
                _get_conv2d_weights(1, embed_dim, self.patch_size)
                for _ in range(max_vars)
            ],
            dim=0,
        )
        self.proj_weights = nn.Parameter(grouped_weights)
        grouped_biases = torch.stack(
            [_get_conv2d_biases(embed_dim) for _ in range(max_vars)], dim=0
        )
        self.proj_biases = nn.Parameter(grouped_biases)
        self.norm = norm_layer(embed_dim) if norm_layer else nn.Identity()
        self.reset_parameters()

    def reset_parameters(self):
        for idx in range(self.max_vars):
            nn.init.kaiming_uniform_(self.proj_weights[idx], a=math.sqrt(5))
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.proj_weights[idx])
            if fan_in != 0:
                bound = 1 / math.sqrt(fan_in)
                nn.init.uniform_(self.proj_biases[idx], -bound, bound)

    def forward(self, x, vars=None):
        B, C, H, W = x.shape
        if vars is None:
            vars = range(self.max_vars)
        weights = self.proj_weights[vars].flatten(0, 1)
        biases = self.proj_biases[vars].flatten(0, 1)

        groups = len(vars)
        proj = F.conv2d(x, weights, biases, groups=groups, stride=self.patch_size)
        if self.flatten:
            proj = proj.reshape(B, groups, -1, *proj.shape[-2:])
            proj = proj.flatten(3).transpose(2, 3)

        proj = self.norm(proj)
        return proj


class climaX(nn.Module):
    """Implements the ClimaX model as described in the paper,
    https://arxiv.org/abs/2301.10343

    Args:
        default_vars (list): list of default variables to be used for training
        img_size (list): image size of the input data
        patch_size (int): patch size of the input data
        embed_dim (int): embedding dimension
        depth (int): number of transformer layers
        decoder_depth (int): number of decoder layers
        num_heads (int): number of attention heads
        mlp_ratio (float): ratio of mlp hidden dimension to embedding dimension
        drop_path (float): stochastic depth rate
        drop_rate (float): dropout rate
        parallel_patch_embed (bool): whether to use parallel patch embedding
    """

    def __init__(self, default_vars, out_variables, img_size, **kwargs):
        super().__init__()

        patch_size = kwargs.get("patch_size", 4)
        embed_dim = kwargs.get("embed_dim", 1024)
        depth = kwargs.get("depth", 8)
        decoder_depth = kwargs.get("decoder_depth", 2)
        num_heads = kwargs.get("num_heads", 16)
        mlp_ratio = kwargs.get("mlp_ratio", 4.0)
        drop_path = kwargs.get("drop_path", 0.1)
        drop_rate = kwargs.get("drop_rate", 0.1)
        parallel_patch_embed = kwargs.get("parallel_patch_embed", True)

        # TODO: remove time_history parameter
        self.img_size = img_size
        self.patch_size = patch_size
        self.default_vars = default_vars
        self.out_variables = out_variables
        self.parallel_patch_embed = parallel_patch_embed
        # variable tokenization: separate embedding layer for each input variable
        if self.parallel_patch_embed:
            self.token_embeds = ParallelVarPatchEmbed(
                len(default_vars), img_size, patch_size, embed_dim
            )
            self.num_patches = self.token_embeds.num_patches
        else:
            self.token_embeds = nn.ModuleList(
                [
                    PatchEmbed(img_size, patch_size, 1, embed_dim)
                    for i in range(len(default_vars))
                ]
            )
            self.num_patches = self.token_embeds[0].num_patches

        # variable embedding to denote which variable each token belongs to
        # helps in aggregating variables
        self.var_embed, self.var_map = self.create_var_embedding(embed_dim)

        # variable aggregation: a learnable query and a single-layer cross attention
        self.var_query = nn.Parameter(torch.zeros(1, 1, embed_dim), requires_grad=True)
        self.var_agg = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)

        # positional embedding and lead time embedding
        self.pos_embed = nn.Parameter(
            torch.zeros(1, self.num_patches, embed_dim), requires_grad=True
        )
        self.lead_time_embed = nn.Linear(1, embed_dim)

        # --------------------------------------------------------------------------

        # ViT backbone
        self.pos_drop = nn.Dropout(p=drop_rate)
        dpr = [
            x.item() for x in torch.linspace(0, drop_path, depth)
        ]  # stochastic depth decay rule
        self.blocks = nn.ModuleList(
            [
                Block(
                    embed_dim,
                    num_heads,
                    mlp_ratio,
                    qkv_bias=True,
                    drop_path=dpr[i],
                    norm_layer=nn.LayerNorm,
                    drop=drop_rate,
                )
                for i in range(depth)
            ]
        )
        self.norm = nn.LayerNorm(embed_dim)

        # --------------------------------------------------------------------------

        # prediction head
        self.head = nn.ModuleList()
        for _ in range(decoder_depth):
            self.head.append(nn.Linear(embed_dim, embed_dim))
            self.head.append(nn.GELU())
        self.head.append(nn.Linear(embed_dim, len(self.default_vars) * patch_size**2))
        self.head = nn.Sequential(*self.head)

        # --------------------------------------------------------------------------

        self.initialize_weights()

    def initialize_weights(self):
        # initialize pos_emb and var_emb
        pos_embed = get_2d_sincos_pos_embed(
            self.pos_embed.shape[-1],
            int(self.img_size[0] / self.patch_size),
            int(self.img_size[1] / self.patch_size),
            cls_token=False,
        )
        self.pos_embed.data.copy_(torch.from_numpy(pos_embed).float().unsqueeze(0))

        var_embed = get_1d_sincos_pos_embed_from_grid(
            self.var_embed.shape[-1], np.arange(len(self.default_vars))
        )
        self.var_embed.data.copy_(torch.from_numpy(var_embed).float().unsqueeze(0))

        # token embedding layer
        if self.parallel_patch_embed:
            for i in range(len(self.token_embeds.proj_weights)):
                w = self.token_embeds.proj_weights[i].data
                trunc_normal_(w.view([w.shape[0], -1]), std=0.02)
        else:
            for i in range(len(self.token_embeds)):
                w = self.token_embeds[i].proj.weight.data
                trunc_normal_(w.view([w.shape[0], -1]), std=0.02)

        # initialize nn.Linear and nn.LayerNorm
        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def create_var_embedding(self, dim):
        var_embed = nn.Parameter(
            torch.zeros(1, len(self.default_vars), dim), requires_grad=True
        )
        # TODO: create a mapping from var --> idx
        var_map = {}
        idx = 0
        for var in self.default_vars:
            var_map[var] = idx
            idx += 1
        return var_embed, var_map

    @lru_cache(maxsize=None)
    def get_var_ids(self, vars, device):
        ids = np.array([self.var_map[var] for var in vars])
        return torch.from_numpy(ids).to(device)

    def get_var_emb(self, var_emb, vars):
        ids = self.get_var_ids(vars, var_emb.device)
        return var_emb[:, ids, :]

    def unpatchify(self, x: torch.Tensor, h=None, w=None):
        """
        x: (B, L, V * patch_size**2)
        return imgs: (B, V, H, W)
        """
        p = self.patch_size
        c = len(self.default_vars)
        h = self.img_size[0] // p if h is None else h // p
        w = self.img_size[1] // p if w is None else w // p
        assert h * w == x.shape[1]

        x = x.reshape(shape=(x.shape[0], h, w, p, p, c))
        x = torch.einsum("nhwpqc->nchpwq", x)
        imgs = x.reshape(shape=(x.shape[0], c, h * p, w * p))
        return imgs

    def aggregate_variables(self, x: torch.Tensor):
        """
        x: B, V, L, D
        """
        b, _, l, _ = x.shape
        x = torch.einsum("bvld->blvd", x)
        x = x.flatten(0, 1)  # BxL, V, D

        var_query = self.var_query.repeat_interleave(x.shape[0], dim=0)
        x, _ = self.var_agg(var_query, x, x)  # BxL, D
        x = x.squeeze()

        x = x.unflatten(dim=0, sizes=(b, l))  # B, L, D
        return x

    def forward_encoder(self, x: torch.Tensor, lead_times: torch.Tensor, variables):
        # x: `[B, V, H, W]` shape.

        if isinstance(variables, list):
            variables = tuple(variables)

        # tokenize each variable separately
        embeds = []
        var_ids = self.get_var_ids(variables, x.device)

        if self.parallel_patch_embed:
            x = self.token_embeds(x, var_ids)  # B, V, L, D
        else:
            for i in range(len(var_ids)):
                id = var_ids[i]
                embeds.append(self.token_embeds[id](x[:, i : i + 1]))
            x = torch.stack(embeds, dim=1)  # B, V, L, D

        # add variable embedding
        var_embed = self.get_var_emb(self.var_embed, variables)
        x = x + var_embed.unsqueeze(2)  # B, V, L, D

        # variable aggregation
        x = self.aggregate_variables(x)  # B, L, D

        # add pos embedding
        x = x + self.pos_embed

        # add lead time embedding
        lead_time_emb = self.lead_time_embed(lead_times.unsqueeze(-1))  # B, D
        lead_time_emb = lead_time_emb.unsqueeze(1)
        x = x + lead_time_emb  # B, L, D

        x = self.pos_drop(x)

        # apply Transformer blocks
        for blk in self.blocks:
            x = blk(x)
        x = self.norm(x)

        return x

    def forward(self, x, lead_times, lat, _, clim):
        """Forward pass through the model.

        Args:
            x: `[B, Vi, H, W]` shape. Input weather/climate variables
            y: `[B, Vo, H, W]` shape. Target weather/climate variables
            lead_times: `[B]` shape. Forecasting lead times of each element of the batch.

        Returns:
            loss (list): Different metrics.
            preds (torch.Tensor): `[B, Vo, H, W]` shape. Predicted weather/climate variables.
        """

        variables, out_variables = self.default_vars, self.out_variables

        out_transformers = self.forward_encoder(x, lead_times, variables)  # B, L, D

        preds = self.head(out_transformers)  # B, L, V*p*p

        preds = self.unpatchify(preds)

        preds = F.interpolate(preds, size=(x.shape[2], x.shape[3]), mode="bicubic")

        return [preds, out_variables, lat]


class lat_weighted_mse(nn.Module):
    """Latitude weighted mean squared error

    Allows to weight the loss by the cosine of the latitude to account for gridding differences at equator vs. poles.

    Args:
        y: [B, V, H, W]
        pred: [B, V, H, W]
        vars: list of variable names
        lat: H
    """

    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, pred_meta, y):
        preds, out_var, lat = pred_meta
        out_var_ids = self.model.get_var_ids(tuple(out_var), preds.device)
        pred = preds[:, out_var_ids]
        lat = lat[0, :]

        error = (pred - y) ** 2  # [N, C, H, W]

        # lattitude weights
        w_lat = np.cos(np.deg2rad(lat.cpu().numpy()))
        w_lat = w_lat / w_lat.mean()  # (H, )
        w_lat = (
            torch.from_numpy(w_lat)
            .unsqueeze(0)
            .unsqueeze(-1)
            .to(dtype=error.dtype, device=error.device)
        )  # (1, H, 1)

        loss_dict = {}
        for i, var in enumerate(out_var):
            if var != "lattitude":
                loss_dict[var] = (error[:, i] * w_lat).mean()
        loss = (error * w_lat.unsqueeze(1)).mean(dim=1).mean()

        return loss  # loss_dict["loss"]
