from ._vitdet import ViT, BackboneFastai
import timm
import types
import logging
import warnings
from torch import nn
from collections import OrderedDict
from torchvision.ops.feature_pyramid_network import (
    FeaturePyramidNetwork,
    LastLevelMaxPool,
)

wavelengths_required_cfg = dict(
    dofa_base=dict(
        backbone_name="dofa_base1",
        patch_size=16,
        embed_dim=768,
        depth=12,
        num_heads=12,
        drop_path_rate=0.0,
        pretrained_path="https://hf.co/torchgeo/dofa/resolve/b8db318b64a90b9e085ec04ba8851233c5893666/dofa_base_patch16_224-a0275954.pth",
    ),
    dofa_large=dict(
        backbone_name="dofa_large",
        patch_size=16,
        embed_dim=1024,
        depth=24,
        num_heads=16,
        drop_path_rate=0.0,
        window_block_indexes=(
            list(range(0, 7))
            + list(range(8, 15))
            + list(range(16, 23))
            + list(range(24, 31))
        ),
        pretrained_path="https://hf.co/torchgeo/dofa/resolve/b8db318b64a90b9e085ec04ba8851233c5893666/dofa_large_patch16_224-0ff904d3.pth",
    ),
)

vit_foundation_model_config = dict(
    prithvi=dict(
        backbone_name="prithvi",
        patch_size=16,
        embed_dim=768,
        depth=12,
        num_heads=12,
        pretrained_path="https://huggingface.co/ibm-nasa-geospatial/Prithvi-100M/resolve/main/Prithvi_100M.pt",
    ),
    **wavelengths_required_cfg
)

vit_config = dict(
    vit_tiny=dict(
        backbone_name="vit_tiny",
        patch_size=16,
        embed_dim=192,
        depth=12,
        num_heads=3,
        pretrained_path="https://dl.fbaipublicfiles.com/deit/deit_tiny_patch16_224-a1311bcf.pth",
    ),
    vit_small=dict(
        backbone_name="vit_small",
        patch_size=16,
        embed_dim=384,
        depth=12,
        num_heads=6,
        pretrained_path="https://dl.fbaipublicfiles.com/deit/deit_small_patch16_224-cd65a155.pth",
    ),
    vit_base=dict(
        backbone_name="vit_base",
        patch_size=16,
        embed_dim=768,
        depth=12,
        num_heads=12,
        pretrain_img_size=384,
        pretrained_path="https://dl.fbaipublicfiles.com/deit/deit_base_patch16_384-8de9b5d1.pth",
    ),
    vit_large=dict(
        backbone_name="vit_large",
        patch_size=32,
        embed_dim=1024,
        depth=24,
        num_heads=16,
        pretrain_img_size=384,
        window_block_indexes=(
            list(range(0, 7))
            + list(range(8, 15))
            + list(range(16, 23))
            + list(range(24, 31))
        ),
        pretrained_path="https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-vitjx/jx_vit_large_p32_384-9b920ba8.pth",
    ),
    **vit_foundation_model_config
)

swin_config = dict(
    swin_tiny="swin_tiny_patch4_window7_224",
    swin_small="swin_small_patch4_window7_224",
    swin_base="swin_base_patch4_window12_384_in22k",
    swin_large="swin_large_patch4_window12_384_in22k",
)

transformer_backbone_downstream = list(swin_config.keys()) + list(vit_config.keys())
wavelengths_required_models = list(wavelengths_required_cfg.keys())


def forward_SwinTransformer(self, x):

    x = self.patch_embed(x)
    if self.absolute_pos_embed is not None:
        x = x + self.absolute_pos_embed
    x = self.pos_drop(x)
    out = []
    for layer in self.layers:
        for blk in layer.blocks:
            x = blk(x)
        out.append(
            x.transpose(1, 2).reshape(
                -1, layer.dim, layer.input_resolution[0], layer.input_resolution[1]
            )
        )
        if layer.downsample is not None:
            x = layer.downsample(x)

    return out


class FPNBackbone(nn.Module):
    def __init__(self, backbone, in_chans):
        super().__init__()
        self.backbone = backbone
        in_chans = 128
        layer_num_channels = [in_chans * 2**i for i in range(4)]
        self.fpn = FeaturePyramidNetwork(
            in_channels_list=layer_num_channels,
            out_channels=256,
            extra_blocks=LastLevelMaxPool(),
        )
        self.out_channels = 256

    def forward(self, x):
        backbone_features = self.backbone(x)
        out = OrderedDict()
        for k, v in enumerate(backbone_features):
            out[str(k)] = v
        x = self.fpn(out)
        return x


def custom_backbone(
    backbone_name, pretrained=True, is_fpn=False, img_size=224, in_chans=3, **kwargs
):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logging.disable(logging.WARNING)
        if backbone_name in vit_config.keys():
            backbone_cfg = vit_config[backbone_name]
            merged_cfg = dict(backbone_cfg, **kwargs)
            backbone = ViT(img_size, in_chans, pretrained=pretrained, **merged_cfg)
            if kwargs.get("is_clf", False):
                from ._timm_utils import TransformerClassifierHead

                classifier = nn.Sequential(
                    backbone, TransformerClassifierHead(backbone.head)
                )
                classifier._is_vitdet = True
                return classifier
            backbone_fpn = BackboneFastai(backbone=backbone, is_fpn=is_fpn)
            backbone_fpn.__name__ = backbone_name

        elif backbone_name in swin_config.keys():
            backbone_cfg = swin_config[backbone_name]
            backbone = timm.create_model(
                backbone_cfg,
                pretrained=pretrained,
                in_chans=in_chans,
                img_size=img_size,
            )
            backbone.forward = types.MethodType(forward_SwinTransformer, backbone)
            return backbone
        logging.disable(0)

    return backbone_fpn
