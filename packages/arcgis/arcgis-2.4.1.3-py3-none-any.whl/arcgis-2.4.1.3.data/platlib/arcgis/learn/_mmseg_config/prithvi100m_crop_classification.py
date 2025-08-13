bands = [1, 2, 3, 8, 11, 12]
# required bands Blue, Green, Red, Narrow NIR, SWIR 1, SWIR 2

loss_weights_multi = [
    0.386375,
    0.661126,
    0.548184,
    0.640482,
    0.876862,
    0.925186,
    3.249462,
    1.542289,
    2.175141,
    2.272419,
    3.062762,
    3.626097,
    1.198702,
]

img_norm_crop_model = dict(
    means=[
        494.905781,
        815.239594,
        924.335066,
        2968.881459,
        2634.621962,
        1739.579917,
        494.905781,
        815.239594,
        924.335066,
        2968.881459,
        2634.621962,
        1739.579917,
        494.905781,
        815.239594,
        924.335066,
        2968.881459,
        2634.621962,
        1739.579917,
    ],
    stds=[
        284.925432,
        357.84876,
        575.566823,
        896.601013,
        951.900334,
        921.407808,
        284.925432,
        357.84876,
        575.566823,
        896.601013,
        951.900334,
        921.407808,
        284.925432,
        357.84876,
        575.566823,
        896.601013,
        951.900334,
        921.407808,
    ],
)


CLASSES = (
    "Natural Vegetation",
    "Forest",
    "Corn",
    "Soybeans",
    "Wetlands",
    "Developed/Barren",
    "Open Water",
    "Winter Wheat",
    "Alfalfa",
    "Fallow/Idle Cropland",
    "Cotton",
    "Sorghum",
    "Others",
    "nodata",
)


nframes = 3
norm_cfg = dict(type="BN", requires_grad=True)
model = dict(
    type="EncoderDecoder",
    backbone=dict(
        type="PrithviBackbone",
        img_size=224,
        in_chans=len(bands),
        num_frames=nframes,
        tubelet_size=1,
        depth=6,
        num_heads=8,
        pretrained=False,
    ),
    neck=dict(
        type="PrithviNeck",
        embed_dim=768 * nframes,
        output_embed_dim=768 * nframes,
        input_hw=(14, 14),
    ),
    decode_head=dict(
        in_channels=768 * nframes,
        type="FCNHead",
        in_index=-1,
        channels=256,
        num_convs=1,
        concat_input=False,
        dropout_ratio=0.1,
        norm_cfg=dict(type="BN", requires_grad=True),
        align_corners=False,
        loss_decode=dict(
            type="CrossEntropyLoss",
            use_sigmoid=False,
            class_weight=loss_weights_multi,
            avg_non_ignore=True,
        ),
    ),
    auxiliary_head=dict(
        in_channels=768 * nframes,
        type="FCNHead",
        in_index=-1,
        channels=256,
        num_convs=2,
        concat_input=False,
        dropout_ratio=0.1,
        norm_cfg=dict(type="BN", requires_grad=True),
        align_corners=False,
        loss_decode=dict(
            type="CrossEntropyLoss",
            use_sigmoid=False,
            class_weight=loss_weights_multi,
            avg_non_ignore=True,
        ),
    ),
    # model training and testing settings
    train_cfg=dict(),
    test_cfg=dict(mode="whole"),
)

checkpoint = "https://huggingface.co/ibm-nasa-geospatial/Prithvi-100M-multi-temporal-crop-classification/resolve/main/multi_temporal_crop_classification_Prithvi_100M.pth"
