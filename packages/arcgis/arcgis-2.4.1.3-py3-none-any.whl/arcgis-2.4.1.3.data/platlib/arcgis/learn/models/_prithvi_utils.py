# Copyright 2023 NASA, IBM

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# --------------------------------------------------------
# References:
# https://github.com/NASA-IMPACT/hls-foundation-os
# timm: https://github.com/rwightman/pytorch-image-models/tree/master/timm
# --------------------------------------------------------

import torch
import torch.nn as nn
from functools import partial
from timm.models.layers import to_2tuple
from timm.models.vision_transformer import VisionTransformer
from collections import OrderedDict
from mmengine.runner.checkpoint import load_state_dict
import logging

pretrained_path = "https://huggingface.co/ibm-nasa-geospatial/Prithvi-100M/resolve/main/Prithvi_100M.pt"


def init_prithvi(model, pretrained_path):
    raw_stdict = torch.hub.load_state_dict_from_url(
        pretrained_path, map_location=torch.device("cpu")
    )
    if "state_dict" in raw_stdict.keys():
        raw_stdict = raw_stdict["state_dict"]
    new_stdict = OrderedDict()
    for k, v in raw_stdict.items():
        if "encoder" in k:
            k = k.replace("encoder.", "")
            new_stdict[k] = v

    load_state_dict(model, new_stdict, False, logging.getLogger())


class PatchEmbed(nn.Module):
    """Frames of 2D Images to Patch Embedding
    The 3D version of timm.models.vision_transformer.PatchEmbed
    """

    def __init__(
        self,
        img_size=224,
        in_chans=3,
        num_frames=1,
        tubelet_size=1,
        patch_size=16,
        embed_dim=768,
    ):
        super().__init__()
        img_size = to_2tuple(img_size)
        patch_size = to_2tuple(patch_size)
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_frames = num_frames
        self.in_chans = in_chans
        self.tubelet_size = tubelet_size
        self.grid_size = (
            num_frames // tubelet_size,
            img_size[0] // patch_size[0],
            img_size[1] // patch_size[1],
        )
        self.num_patches = self.grid_size[0] * self.grid_size[1] * self.grid_size[2]

        self.proj = nn.Conv3d(
            in_chans,
            embed_dim,
            kernel_size=(tubelet_size, patch_size[0], patch_size[1]),
            stride=(tubelet_size, patch_size[0], patch_size[1]),
        )
        self.norm = nn.Identity()

    def forward(self, x):
        B, C, H, W = x.shape
        num_frames = C // self.in_chans
        assert (
            self.num_frames == num_frames
        ), f"Number of band ({C}) is not compatible with ({self.num_frames})."
        x = x.reshape((B, self.in_chans, self.num_frames, H, W))
        x = self.proj(x)
        x = x.flatten(2).transpose(1, 2)  # B,C,T,H,W -> B,C,L -> B,L,C
        x = self.norm(x)
        return x


class PrithviBackbone(VisionTransformer):
    def __init__(
        self,
        img_size=224,
        in_chans=3,
        num_frames=1,
        tubelet_size=1,
        depth=12,
        num_heads=12,
        pretrained=True,
    ):
        PatchEmbed3d = partial(
            PatchEmbed, num_frames=num_frames, tubelet_size=tubelet_size
        )
        # Timm vit_base_patch16_224 architecture
        super().__init__(
            img_size=img_size,
            patch_size=16,
            in_chans=in_chans,
            embed_dim=768,
            depth=depth,
            num_heads=num_heads,
            mlp_ratio=4,
            embed_layer=PatchEmbed3d,
        )
        self._is_prithvi = True
        self.__delattr__("head")
        if pretrained:
            init_prithvi(self, pretrained_path)

    def forward(self, x):
        x = self.patch_embed(x)
        cls_token = self.cls_token.expand(x.shape[0], -1, -1)
        x = torch.cat((cls_token, x), dim=1)
        x = self.pos_drop(x + self.pos_embed)
        x = self.blocks(x)
        x = self.norm(x)

        return x


class Norm2d(nn.Module):
    def __init__(self, embed_dim: int):
        super().__init__()
        self.ln = nn.LayerNorm(embed_dim, eps=1e-6)

    def forward(self, x):
        x = x.permute(0, 2, 3, 1)
        x = self.ln(x)
        x = x.permute(0, 3, 1, 2).contiguous()
        return x


def prithvi_upsample(in_chans, out_chans, kernel_size, stride):
    return nn.Sequential(
        nn.ConvTranspose2d(
            in_chans,
            out_chans,
            kernel_size=kernel_size,
            stride=stride,
        ),
        Norm2d(out_chans),
        nn.GELU(),
        nn.ConvTranspose2d(
            out_chans,
            out_chans,
            kernel_size=kernel_size,
            stride=stride,
        ),
    )


class PrithviNeck(nn.Module):
    def __init__(
        self,
        embed_dim,
        output_embed_dim,
        input_hw,
        kernel_size=2,
        stride=2,
    ):
        super().__init__()
        self.input_hw = input_hw
        self.fpn1 = prithvi_upsample(embed_dim, output_embed_dim, kernel_size, stride)
        self.fpn2 = prithvi_upsample(
            output_embed_dim, output_embed_dim, kernel_size, stride
        )

    def forward(self, x):
        # drop class token
        x = x[:, 1:, :]
        x = x.permute(0, 2, 1).reshape(
            x.shape[0], -1, self.input_hw[0], self.input_hw[0]
        )
        x = self.fpn1(x)
        x = self.fpn2(x)

        return tuple([x])


def register_prithvi():
    from mmseg.registry import MODELS

    try:
        MODELS.register_module("PrithviBackbone", module=PrithviBackbone)
        MODELS.register_module("PrithviNeck", module=PrithviNeck)
    except:
        pass
