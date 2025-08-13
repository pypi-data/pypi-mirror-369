import timm
from timm.models.resnet import (
    BasicBlock,
    Bottleneck,
    ResNet,
)
from timm.models.helpers import build_model_with_cfg
from timm.models.vision_transformer import VisionTransformer
from timm.models.vision_transformer import (
    checkpoint_filter_fn as vit_checkpoint_filter_fn,
)
from timm.models.resnet import default_cfgs as resnet_default_cfgs
from timm.models.vision_transformer import default_cfgs as vit_default_cfgs
from timm.models.registry import register_model


# extended configs for timm resnet models
def _res_cfg(url="", **kwargs):
    return {
        "url": url,
        "num_classes": 1000,
        "input_size": (3, 224, 224),
        "pool_size": (7, 7),
        "crop_pct": 0.875,
        "interpolation": "bilinear",
        "mean": timm.data.IMAGENET_DEFAULT_MEAN,
        "std": timm.data.IMAGENET_DEFAULT_STD,
        "classifier": "fc",
        **kwargs,
    }


hf_resnet_cfgs = {
    # ResNet18 and ResNet50 variants
    "resnet18_landsat_tm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_tm_toa_moco-1c691b4f.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_tm_toa_moco-1c691b4f.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_landsat_tm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_tm_toa_simclr-d2d38ace.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_tm_toa_simclr-d2d38ace.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_landsat_etm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_toa_moco-bb88689c.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_toa_moco-bb88689c.pth",
        input_size=(9, 224, 224),
    ),
    "resnet18_landsat_etm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_toa_simclr-4d813f79.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_toa_simclr-4d813f79.pth",
        input_size=(9, 224, 224),
    ),
    "resnet18_landsat_etm_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_sr_moco-4f078acd.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_sr_moco-4f078acd.pth",
        input_size=(6, 224, 224),
    ),
    "resnet18_landsat_etm_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_sr_simclr-8e8543b4.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_sr_simclr-8e8543b4.pth",
        input_size=(6, 224, 224),
    ),
    "resnet18_landsat_oli_tirs_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_tirs_toa_moco-a3002f51.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_tirs_toa_moco-a3002f51.pth",
        input_size=(11, 224, 224),
    ),
    "resnet18_landsat_oli_tirs_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_tirs_toa_simclr-b0635cc6.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_tirs_toa_simclr-b0635cc6.pth",
        input_size=(11, 224, 224),
    ),
    "resnet18_landsat_oli_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_sr_moco-660e82ed.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_sr_moco-660e82ed.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_landsat_oli_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_sr_simclr-7bced5be.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_sr_simclr-7bced5be.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_sentinel2_all_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet18_sentinel2_all_moco/resolve/5b8cddc9a14f3844350b7f40b85bcd32aed75918/resnet18_sentinel2_all_moco-59bfdff9.pth",
        hf_hub="torchgeo/resnet18_sentinel2_all_moco",
        filename="resnet18_sentinel2_all_moco-59bfdff9.pth",
        input_size=(13, 224, 224),
    ),
    "resnet18_sentinel2_rgb_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet18_sentinel2_rgb_moco/resolve/e1c032e7785fd0625224cdb6699aa138bb304eec/resnet18_sentinel2_rgb_moco-e3a335e3.pth",
        hf_hub="torchgeo/resnet18_sentinel2_rgb_moco",
        filename="resnet18_sentinel2_rgb_moco-e3a335e3.pth",
        input_size=(3, 224, 224),
    ),
    "resnet18_sentinel2_rgb_seco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet18_sentinel2_rgb_seco/resolve/f8dcee692cf7142163b55a5c197d981fe0e717a0/resnet18_sentinel2_rgb_seco-cefca942.pth",
        hf_hub="torchgeo/resnet18_sentinel2_rgb_seco",
        filename="resnet18_sentinel2_rgb_seco-cefca942.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_landsat_tm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_tm_toa_moco-ba1ce753.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_tm_toa_moco-ba1ce753.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_landsat_tm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_tm_toa_simclr-a1c93432.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_tm_toa_simclr-a1c93432.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_landsat_etm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_toa_moco-e9a84d5a.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_toa_moco-e9a84d5a.pth",
        input_size=(9, 224, 224),
    ),
    "resnet50_landsat_etm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_toa_simclr-70b5575f.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_toa_simclr-70b5575f.pth",
        input_size=(9, 224, 224),
    ),
    "resnet50_landsat_etm_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_sr_moco-1266cde3.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_sr_moco-1266cde3.pth",
        input_size=(6, 224, 224),
    ),
    "resnet50_landsat_etm_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_sr_simclr-e5d185d7.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_sr_simclr-e5d185d7.pth",
        input_size=(6, 224, 224),
    ),
    "resnet50_landsat_oli_tirs_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_tirs_toa_moco-de7f5e0f.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_tirs_toa_moco-de7f5e0f.pth",
        input_size=(11, 224, 224),
    ),
    "resnet50_landsat_oli_tirs_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_tirs_toa_simclr-030cebfe.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_tirs_toa_simclr-030cebfe.pth",
        input_size=(11, 224, 224),
    ),
    "resnet50_landsat_oli_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_sr_moco-ff580dad.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_sr_moco-ff580dad.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_landsat_oli_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_sr_simclr-94f78913.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_sr_simclr-94f78913.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_sentinel2_all_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_all_moco/resolve/da4f3c9dbe09272eb902f3b37f46635fa4726879/resnet50_sentinel2_all_moco-df8b932e.pth",
        hf_hub="torchgeo/resnet50_sentinel2_all_moco",
        filename="resnet50_sentinel2_all_moco-df8b932e.pth",
        input_size=(13, 224, 224),
    ),
    "resnet50_sentinel2_rgb_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_rgb_moco/resolve/efd9723b59a88e9dc1420dc1e96afb25b0630a3c/resnet50_sentinel2_rgb_moco-2b57ba8b.pth",
        hf_hub="torchgeo/resnet50_sentinel2_rgb_moco",
        filename="resnet50_sentinel2_rgb_moco-2b57ba8b.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_sentinel2_rgb_seco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_rgb_seco/resolve/fbd07b02a8edb8fc1035f7957160deed4321c145/resnet50_sentinel2_rgb_seco-018bf397.pth",
        hf_hub="torchgeo/resnet50_sentinel2_rgb_seco",
        filename="resnet50_sentinel2_rgb_seco-018bf397.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_sentinel2_all_dino": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_all_dino/resolve/d7f14bf5530d70ac69d763e58e77e44dbecfec7c/resnet50_sentinel2_all_dino-d6c330e9.pth",
        hf_hub="torchgeo/resnet50_sentinel2_all_dino",
        filename="resnet50_sentinel2_all_dino-d6c330e9.pth",
        input_size=(13, 224, 224),
    ),
    "resnet50_fmow_rgb_gassl": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_fmow_rgb_gassl/resolve/fe8a91026cf9104f1e884316b8e8772d7af9052c/resnet50_fmow_rgb_gassl-da43d987.pth",
        hf_hub="torchgeo/resnet50_fmow_rgb_gassl",
        filename="resnet50_fmow_rgb_gassl-da43d987.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_sentinel2_mi_ms_satlas": _res_cfg(
        # url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet50_mi_ms-da5413d2.pth",
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet50_mi_ms-da5413d2.pth",
        input_size=(9, 224, 224),
    ),
    "resnet50_sentinel2_mi_rgb_satlas": _res_cfg(
        # url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet50_mi_rgb-e79bb7fe.pth",
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet50_mi_rgb-e79bb7fe.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_sentinel2_si_ms_satlas": _res_cfg(
        # url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet50_si_ms-1f454cc6.pth",
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet50_si_ms-1f454cc6.pth",
        input_size=(9, 224, 224),
    ),
    "resnet50_sentinel2_si_rgb_satlas": _res_cfg(
        # url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet50_si_rgb-45fc6972.pth",
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet50_si_rgb-45fc6972.pth",
        input_size=(3, 224, 224),
    ),
    "resnet152_sentinel2_mi_ms_satlas": _res_cfg(
        # url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet152_mi_ms-fd35b4bb.pth",
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet152_mi_ms-fd35b4bb.pth",
        input_size=(9, 224, 224),
    ),
    "resnet152_sentinel2_mi_rgb_satlas": _res_cfg(
        # url='https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet152_mi_rgb-67563ac5.pth',
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet152_mi_rgb-67563ac5.pth",
        input_size=(3, 224, 224),
    ),
    "resnet152_sentinel2_si_ms_satlas": _res_cfg(
        # url='https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet152_si_ms-4500c6cb.pth',
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet152_si_ms-4500c6cb.pth",
        input_size=(9, 224, 224),
    ),
    "resnet152_sentinel2_si_rgb_satlas": _res_cfg(
        # url='https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_resnet152_si_rgb-f4d24c3c.pth',
        hf_hub="torchgeo/satlas",
        filename="sentinel2_resnet152_si_rgb-f4d24c3c.pth",
        input_size=(3, 224, 224),
    ),
}


resnet_updated_cfgs = resnet_default_cfgs | hf_resnet_cfgs

timm.models.resnet.default_cfgs = resnet_updated_cfgs


def resnet_checkpoint_filter_fn(state_dict, model):
    """make downloaded state dict keys' names same as model state keys' names for resnet models"""
    out_dict = model.state_dict().copy()
    for ix, (kx, vx) in zip(model.state_dict(), state_dict.items()):
        out_dict[ix] = vx

    return out_dict


def _create_resnet(variant, pretrained=False, **kwargs):
    return build_model_with_cfg(
        ResNet,
        variant,
        pretrained,
        default_cfg=resnet_updated_cfgs[variant],
        pretrained_filter_fn=resnet_checkpoint_filter_fn,
        **kwargs,
    )


@register_model
def resnet18_landsat_tm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_tm_toa_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_tm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_tm_toa_simclr", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_toa_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_toa_simclr", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_sr_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_sr_simclr", pretrained, **model_args)


@register_model
def resnet18_landsat_oli_tirs_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet(
        "resnet18_landsat_oli_tirs_toa_moco", pretrained, **model_args
    )


@register_model
def resnet18_landsat_oli_tirs_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet(
        "resnet18_landsat_oli_tirs_toa_simclr", pretrained, **model_args
    )


@register_model
def resnet18_landsat_oli_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_oli_sr_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_oli_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_oli_sr_simclr", pretrained, **model_args)


@register_model
def resnet18_sentinel2_all_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_sentinel2_all_moco", pretrained, **model_args)


@register_model
def resnet18_sentinel2_rgb_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_sentinel2_rgb_moco", pretrained, **model_args)


@register_model
def resnet18_sentinel2_rgb_seco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_sentinel2_rgb_seco", pretrained, **model_args)


@register_model
def resnet50_landsat_tm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_tm_toa_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_tm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_tm_toa_simclr", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_toa_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_toa_simclr", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_sr_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_sr_simclr", pretrained, **model_args)


@register_model
def resnet50_landsat_oli_tirs_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet(
        "resnet50_landsat_oli_tirs_toa_moco", pretrained, **model_args
    )


@register_model
def resnet50_landsat_oli_tirs_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet(
        "resnet50_landsat_oli_tirs_toa_simclr", pretrained, **model_args
    )


@register_model
def resnet50_landsat_oli_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_oli_sr_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_oli_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_oli_sr_simclr", pretrained, **model_args)


@register_model
def resnet50_sentinel2_all_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_all_moco", pretrained, **model_args)


@register_model
def resnet50_sentinel2_rgb_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_rgb_moco", pretrained, **model_args)


@register_model
def resnet50_sentinel2_rgb_seco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_rgb_seco", pretrained, **model_args)


@register_model
def resnet50_sentinel2_all_dino(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_all_dino", pretrained, **model_args)


@register_model
def resnet50_fmow_rgb_gassl(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_fmow_rgb_gassl", pretrained, **model_args)


@register_model
def resnet50_sentinel2_mi_ms_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_mi_ms_satlas", pretrained, **model_args)


@register_model
def resnet50_sentinel2_mi_rgb_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_mi_rgb_satlas", pretrained, **model_args)


@register_model
def resnet50_sentinel2_si_ms_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_si_ms_satlas", pretrained, **model_args)


@register_model
def resnet50_sentinel2_si_rgb_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_si_rgb_satlas", pretrained, **model_args)


@register_model
def resnet152_sentinel2_mi_ms_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 8, 36, 3], **kwargs)
    return _create_resnet("resnet152_sentinel2_mi_ms_satlas", pretrained, **model_args)


@register_model
def resnet152_sentinel2_mi_rgb_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 8, 36, 3], **kwargs)
    return _create_resnet("resnet152_sentinel2_mi_rgb_satlas", pretrained, **model_args)


@register_model
def resnet152_sentinel2_si_ms_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 8, 36, 3], **kwargs)
    return _create_resnet("resnet152_sentinel2_si_ms_satlas", pretrained, **model_args)


@register_model
def resnet152_sentinel2_si_rgb_satlas(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 8, 36, 3], **kwargs)
    return _create_resnet("resnet152_sentinel2_si_rgb_satlas", pretrained, **model_args)


########################################### vit based backbones ##############################################


def _vit_cfg(url="", **kwargs):
    return {
        "url": url,
        "num_classes": 1000,
        "input_size": (3, 224, 224),
        "pool_size": None,
        "crop_pct": 0.9,
        "interpolation": "bicubic",
        "fixed_input_size": True,
        "mean": timm.data.IMAGENET_INCEPTION_MEAN,
        "std": timm.data.IMAGENET_INCEPTION_STD,
        "first_conv": "patch_embed.proj",
        "classifier": "head",
        **kwargs,
    }


hf_vit_cfgs = {
    # ResNet18 and ResNet50 variants
    "vit_small_patch16_224_landsat_tm_toa_moco": _vit_cfg(
        # url='https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_tm_toa_moco-a1c967d8.pth',
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_tm_toa_moco-a1c967d8.pth",
        input_size=(7, 224, 224),
    ),
    "vit_small_patch16_224_landsat_tm_toa_simclr": _vit_cfg(
        # url='https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_tm_toa_simclr-7c2d9799.pth',
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_tm_toa_simclr-7c2d9799.pth",
        input_size=(7, 224, 224),
    ),
    "vit_small_patch16_224_landsat_etm_toa_moco": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_etm_toa_moco-26d19bcf.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_etm_toa_moco-26d19bcf.pth",
        input_size=(9, 224, 224),
    ),
    "vit_small_patch16_224_landsat_etm_toa_simclr": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_etm_toa_simclr-34fb12cb.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_etm_toa_simclr-34fb12cb.pth",
        input_size=(9, 224, 224),
    ),
    "vit_small_patch16_224_landsat_etm_sr_moco": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_etm_sr_moco-eaa4674e.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_etm_sr_moco-eaa4674e.pth",
        input_size=(6, 224, 224),
    ),
    "vit_small_patch16_224_landsat_etm_sr_simclr": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_etm_sr_simclr-a14c466a.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_etm_sr_simclr-a14c466a.pth",
        input_size=(6, 224, 224),
    ),
    "vit_small_patch16_224_landsat_oli_tirs_toa_moco": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_oli_tirs_toa_moco-c7c2cceb.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_oli_tirs_toa_moco-c7c2cceb.pth",
        input_size=(11, 224, 224),
    ),
    "vit_small_patch16_224_landsat_oli_tirs_toa_simclr": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_oli_tirs_toa_simclr-ad43e9a4.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_oli_tirs_toa_simclr-ad43e9a4.pth",
        input_size=(11, 224, 224),
    ),
    "vit_small_patch16_224_landsat_oli_sr_moco": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_oli_sr_moco-c9b8898d.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_oli_sr_moco-c9b8898d.pth",
        input_size=(7, 224, 224),
    ),
    "vit_small_patch16_224_landsat_oli_sr_simclr": _vit_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/vits16_landsat_oli_sr_simclr-4e8f6102.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="vits16_landsat_oli_sr_simclr-4e8f6102.pth",
        input_size=(7, 224, 224),
    ),
    "vit_small_patch16_224_sentinel2_all_dino": _vit_cfg(
        # url="https://hf.co/torchgeo/vit_small_patch16_224_sentinel2_all_dino/resolve/5b41dd418a79de47ac9f5be3e035405a83818a62/vit_small_patch16_224_sentinel2_all_dino-36bcc127.pth",
        hf_hub="torchgeo/vit_small_patch16_224_sentinel2_all_dino",
        filename="vit_small_patch16_224_sentinel2_all_dino-36bcc127.pth",
        input_size=(13, 224, 224),
    ),
    "vit_small_patch16_224_sentinel2_all_moco": _vit_cfg(
        # url="https://hf.co/torchgeo/vit_small_patch16_224_sentinel2_all_moco/resolve/1cb683f6c14739634cdfaaceb076529adf898c74/vit_small_patch16_224_sentinel2_all_moco-67c9032d.pth",
        hf_hub="torchgeo/vit_small_patch16_224_sentinel2_all_moco",
        filename="vit_small_patch16_224_sentinel2_all_moco-67c9032d.pth",
        input_size=(13, 224, 224),
    ),
}


vit_updated_cfgs = vit_default_cfgs | hf_vit_cfgs

timm.models.vision_transformer.default_cfgs = vit_updated_cfgs


def _create_vision_transformer(variant, pretrained=False, default_cfg=None, **kwargs):
    default_cfg = default_cfg or vit_updated_cfgs[variant]
    if kwargs.get("features_only", None):
        raise RuntimeError(
            "features_only not implemented for Vision Transformer models."
        )

    # NOTE this extra code to support handling of repr size for in21k pretrained models
    default_num_classes = default_cfg["num_classes"]
    num_classes = kwargs.get("num_classes", default_num_classes)
    repr_size = kwargs.pop("representation_size", None)
    if repr_size is not None and num_classes != default_num_classes:
        # Remove representation layer if fine-tuning. This may not always be the desired action,
        # but I feel better than doing nothing by default for fine-tuning. Perhaps a better interface?
        # _logger.warning("Removing representation layer for fine-tuning.")
        repr_size = None

    model = build_model_with_cfg(
        VisionTransformer,
        variant,
        pretrained,
        default_cfg=default_cfg,
        representation_size=repr_size,
        pretrained_filter_fn=vit_checkpoint_filter_fn,
        pretrained_custom_load="npz" in default_cfg["url"],
        **kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_tm_toa_moco(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_tm_toa_moco",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_tm_toa_simclr(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_tm_toa_simclr",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_etm_toa_moco(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_etm_toa_moco",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_etm_toa_simclr(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_etm_toa_simclr",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_etm_sr_moco(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_etm_sr_moco",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_etm_sr_simclr(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_etm_sr_simclr",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_oli_tirs_toa_moco(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_oli_tirs_toa_moco",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_oli_tirs_toa_simclr(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_oli_tirs_toa_simclr",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_oli_sr_moco(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_oli_sr_moco",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_landsat_oli_sr_simclr(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_landsat_oli_sr_simclr",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_sentinel2_all_dino(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_sentinel2_all_dino",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


@register_model
def vit_small_patch16_224_sentinel2_all_moco(pretrained=False, **kwargs):
    """ViT-Small (ViT-S/16)
    NOTE I've replaced my previous 'small' model definition and weights with the small variant from the DeiT paper
    """
    model_kwargs = dict(patch_size=16, embed_dim=384, depth=12, num_heads=6, **kwargs)
    model = _create_vision_transformer(
        "vit_small_patch16_224_sentinel2_all_moco",
        pretrained=pretrained,
        **model_kwargs,
    )
    return model


########################################### swin based backbones ##############################################


from torchvision.models import SwinTransformer
from torchvision.models._api import Weights, WeightsEnum
from typing import Any
import torch
import torchvision


from torch.hub import load_state_dict_from_url


"""Pre-trained Swin v2 Transformer models."""

from typing import Any

import torch
import torchvision
from torchvision.models import (
    SwinTransformer,
    Swin_V2_T_Weights,
    Swin_V2_B_Weights,
)
from torchvision.models.swin_transformer import (
    PatchMergingV2,
    SwinTransformerBlockV2,
)
from torchvision.models._api import Weights, WeightsEnum
from torch import Tensor
from torchvision.models._api import register_model as register_model_tv
from typing import Any, Callable, List, Optional
from torchvision.models._utils import _ovewrite_named_param, handle_legacy_interface


_satlas_bands = ("B04", "B03", "B02")


_satlas_sentinel2_bands = (*_satlas_bands, "B05", "B06", "B07", "B08", "B11", "B12")


_satlas_landsat_bands = tuple(f"B{i:02}" for i in range(1, 12))


Weights.__deepcopy__ = lambda *args, **kwargs: args[0]


class Swin_Weights(WeightsEnum):  # type: ignore[misc]
    """Swin Transformer v2 Tiny/Base weights.

    For `torchvision <https://github.com/pytorch/vision>`_
    *swin_v2_t* implementation.
    *swin_v2_b* implementation.

    .. versionadded:: 0.6
    """

    swin_v2_t_sentinel2_mi_ms_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swint_mi_ms-d8c659e3.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 9,
            "model": "swin_v2_t",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_sentinel2_bands,
        },
    )

    swin_v2_t_sentinel2_mi_rgb_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swint_mi_rgb-424d91f4.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 3,
            "model": "swin_v2_t",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_bands,
        },
    )

    swin_v2_t_sentinel2_si_ms_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swint_si_ms-bc68e396.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 9,
            "model": "swin_v2_t",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_sentinel2_bands,
        },
    )

    swin_v2_t_sentinel2_si_rgb_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swint_si_rgb-0c1a96e0.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 3,
            "model": "swin_v2_t",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_bands,
        },
    )

    swin_v2_b_naip_rgb_mi_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/aerial_swinb_mi-326d69e1.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 3,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": ("R", "G", "B"),
        },
    )

    swin_v2_b_naip_rgb_si_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/aerial_swinb_si-e4169eb1.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 3,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": ("R", "G", "B"),
        },
    )

    swin_v2_b_landsat_mi_satlas = Weights(
        url="https://huggingface.co/torchgeo/satlas/resolve/main/landsat_swinb_mi-6b4a1cda.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 11,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_landsat_bands,
        },
    )

    swin_v2_b_landsat_si_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/landsat_swinb_si-4af978f6.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 11,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_landsat_bands,
        },
    )

    swin_v2_b_sentinel2_mi_ms_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swinb_mi_ms-39c86721.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 9,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_sentinel2_bands,
        },
    )

    swin_v2_b_sentinel2_mi_rgb_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swinb_mi_rgb-4efa210c.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 3,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_bands,
        },
    )

    swin_v2_b_sentinel2_si_ms_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swinb_si_ms-fe22a12c.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 9,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_sentinel2_bands,
        },
    )

    swin_v2_b_sentinel2_si_rgb_satlas = Weights(
        url="https://hf.co/torchgeo/satlas/resolve/081d6607431bf36bdb59c223777cbb267131b8f2/sentinel2_swinb_si_rgb-156a98d5.pth",
        transforms=None,
        meta={
            "dataset": "SatlasPretrain",
            "in_chans": 3,
            "model": "swin_v2_b",
            "publication": "https://arxiv.org/abs/2211.15660",
            "repo": "https://github.com/allenai/satlas",
            "bands": _satlas_bands,
        },
    )


swin_v2_t_params = {
    "patch_size": [4, 4],
    "embed_dim": 96,
    "depths": [2, 2, 6, 2],
    "num_heads": [3, 6, 12, 24],
    "window_size": [8, 8],
    "stochastic_depth_prob": 0.2,
    "block": SwinTransformerBlockV2,
    "downsample_layer": PatchMergingV2,
}

swin_v2_b_params = {
    "patch_size": [4, 4],
    "embed_dim": 128,
    "depths": [2, 2, 18, 2],
    "num_heads": [4, 8, 16, 32],
    "window_size": [8, 8],
    "stochastic_depth_prob": 0.5,
    "block": SwinTransformerBlockV2,
    "downsample_layer": PatchMergingV2,
}


from torch.serialization import MAP_LOCATION
from typing import Dict, Optional, Any
import os
import warnings
from torch.hub import get_dir, _is_legacy_zip_format, _legacy_zip_load
from urllib.parse import urlparse  # noqa: F401
import errno
import sys
import re
import requests

HASH_REGEX = re.compile(r"-([a-f0-9]*)\.")


def _torch_load_state_dict_from_url(
    url: str,
    model_dir: Optional[str] = None,
    map_location: MAP_LOCATION = None,
    progress: bool = True,
    check_hash: bool = False,
    file_name: Optional[str] = None,
) -> Dict[str, Any]:
    r"""Loads the Torch serialized object at the given URL.

    If downloaded file is a zip file, it will be automatically
    decompressed.

    If the object is already present in `model_dir`, it's deserialized and
    returned.
    The default value of ``model_dir`` is ``<hub_dir>/checkpoints`` where
    ``hub_dir`` is the directory returned by :func:`~torch.hub.get_dir`.

    Args:
        url (str): URL of the object to download
        model_dir (str, optional): directory in which to save the object
        map_location (optional): a function or a dict specifying how to remap storage locations (see torch.load)
        progress (bool, optional): whether or not to display a progress bar to stderr.
            Default: True
        check_hash(bool, optional): If True, the filename part of the URL should follow the naming convention
            ``filename-<sha256>.ext`` where ``<sha256>`` is the first eight or more
            digits of the SHA256 hash of the contents of the file. The hash is used to
            ensure unique names and to verify the contents of the file.
            Default: False
        file_name (str, optional): name for the downloaded file. Filename from ``url`` will be used if not set.

    Example:
        >>> # xdoctest: +REQUIRES(env:TORCH_DOCTEST_HUB)
        >>> state_dict = torch.hub.load_state_dict_from_url('https://s3.amazonaws.com/pytorch/models/resnet18-5c106cde.pth')

    """
    # Issue warning to move data if old env is set
    if os.getenv("TORCH_MODEL_ZOO"):
        warnings.warn(
            "TORCH_MODEL_ZOO is deprecated, please use env TORCH_HOME instead"
        )

    if model_dir is None:
        hub_dir = get_dir()
        model_dir = os.path.join(hub_dir, "checkpoints")

    try:
        os.makedirs(model_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # Directory already exists, ignore.
            pass
        else:
            # Unexpected OSError, re-raise.
            raise

    parts = urlparse(url)
    filename = os.path.basename(parts.path)
    if file_name is not None:
        filename = file_name
    cached_file = os.path.join(model_dir, filename)
    if not os.path.exists(cached_file):
        sys.stderr.write('Downloading: "{}" to {}\n'.format(url, cached_file))
        hash_prefix = None
        if check_hash:
            r = HASH_REGEX.search(filename)  # r is Optional[Match[str]]
            hash_prefix = r.group(1) if r else None

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(cached_file, "wb") as f:
                f.write(response.content)
            print(f"Weights downloaded successfully and saved to {cached_file}")
        else:
            print(f"Failed to download weights. Status code: {response.status_code}")

    if _is_legacy_zip_format(cached_file):
        return _legacy_zip_load(cached_file, model_dir, map_location)
    return torch.load(cached_file, map_location=map_location)


def modify_tail_and_load(weights, model):
    num_channels = weights.meta["in_chans"]
    out_channels = model.features[0][0].out_channels
    model.features[0][0] = torch.nn.Conv2d(
        num_channels, out_channels, kernel_size=(4, 4), stride=(4, 4)
    )

    missing_keys, unexpected_keys = model.load_state_dict(
        _torch_load_state_dict_from_url(url=weights.url, progress=True), strict=False
    )

    assert set(missing_keys) <= set()
    assert not unexpected_keys

    return model


@register_model_tv()
def swin_v2_t_sentinel2_mi_ms_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_t_sentinel2_mi_ms_satlas)

    model = SwinTransformer(
        **swin_v2_t_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_t_sentinel2_mi_rgb_satlas(
    pretrained=True, **kwargs: Any
) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_t_sentinel2_mi_rgb_satlas)

    model = SwinTransformer(
        **swin_v2_t_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_t_sentinel2_si_ms_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_t_sentinel2_si_ms_satlas)

    model = SwinTransformer(
        **swin_v2_t_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_t_sentinel2_si_rgb_satlas(
    pretrained=True, **kwargs: Any
) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_t_sentinel2_si_rgb_satlas)

    model = SwinTransformer(
        **swin_v2_t_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_naip_rgb_mi_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_naip_rgb_mi_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_naip_rgb_si_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_naip_rgb_si_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_landsat_mi_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_landsat_mi_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_landsat_si_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_landsat_si_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_sentinel2_mi_ms_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_sentinel2_mi_ms_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_sentinel2_mi_rgb_satlas(
    pretrained=True, **kwargs: Any
) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_sentinel2_mi_rgb_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_sentinel2_si_ms_satlas(pretrained=True, **kwargs: Any) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_sentinel2_si_ms_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model


@register_model_tv()
def swin_v2_b_sentinel2_si_rgb_satlas(
    pretrained=True, **kwargs: Any
) -> SwinTransformer:

    weights = None
    if pretrained:
        weights = Swin_Weights.verify(Swin_Weights.swin_v2_b_sentinel2_si_rgb_satlas)

    model = SwinTransformer(
        **swin_v2_b_params,
        **kwargs,
    )

    if weights is not None:
        return modify_tail_and_load(weights=weights, model=model)

    return model
