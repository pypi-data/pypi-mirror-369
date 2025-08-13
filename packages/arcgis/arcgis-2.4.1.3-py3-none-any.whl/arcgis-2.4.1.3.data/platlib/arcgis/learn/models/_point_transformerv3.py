import traceback
from .._utils.env import raise_fastai_import_error

import_exception = None
try:
    from ._pointcnnseg import PointCNN
    from fastai.basic_train import Learner
    from ._point_transformerv3_utils import PointTransformerV3Seg
    from .._utils.pointcloud_serialization import prepare_data_dict
    from ._arcgis_model import _EmptyData
    from ._pointcnn_utils import (
        CrossEntropyPC,
        AverageMetric,
        CalculateClassificationReport,
        accuracy,
        precision,
        recall,
        f1,
    )
    import json
    from pathlib import Path
    from .._utils.common import _get_emd_path
    from .._data import _raise_fastai_import_error
    from copy import deepcopy

    HAS_FASTAI = True
except Exception as e:
    import_exception = traceback.format_exc()
    HAS_FASTAI = False


class PTv3Seg(PointCNN):
    """
    Model architecture from https://arxiv.org/pdf/2312.10035.
    Creates PTv3Seg point cloud segmentation model.

    =====================   ===========================================
    **Parameter**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            `prepare_data` function.
    ---------------------   -------------------------------------------
    pretrained_path         Optional String. Path where pre-trained model
                            is saved.
    =====================   ===========================================

    **kwargs**

    =====================   ===========================================
    **Parameter**            **Description**
    ---------------------   -------------------------------------------
    sub_sampling_ratio      Optional int. Sampling ratio of points in each
                            layer. Default: 2.
    ---------------------   -------------------------------------------
    seq_len                 Optional int. Sequence length for transformer.
                            Default: 1024.
    ---------------------   -------------------------------------------
    voxel_size              Optional float. Defines the size of voxels in
                            meters for a block. Default: 0.02.
    ---------------------   -------------------------------------------
    focal_loss              Optional boolean. If True, it will use focal loss.
                            Default: False.
    =====================   ===========================================

    :return: `PTv3Seg` Object
    """

    def __init__(self, data, pretrained_path=None, *args, **kwargs):
        super().__init__(data, None)

        if not HAS_FASTAI:
            raise_fastai_import_error(
                import_exception=import_exception,
                message="This model requires module 'torch_geometric' to be installed.",
                installation_steps=" ",
            )

        self._backbone = None
        self.sample_point_num = data.max_point
        self._focal_loss = kwargs.get("focal_loss", False)
        self.encoder_params = kwargs

        if not isinstance(data, _EmptyData):
            data = prepare_data_dict(
                deepcopy(data), grid_size=kwargs.get("voxel_size", 0.02)
            )
        self._data = data

        self.learn = Learner(
            data,
            PointTransformerV3Seg(
                in_channels=data.extra_dim + 3,
                num_classes=data.c,
                max_points=self.sample_point_num,
                **kwargs
            ),
            loss_func=CrossEntropyPC(data.c, data.device, self._focal_loss),
            metrics=[
                AverageMetric(accuracy),
                AverageMetric(precision),
                AverageMetric(recall),
                AverageMetric(f1),
            ],
            callback_fns=CalculateClassificationReport,
        )

        self.learn.model = self.learn.model.to(self._device)

        if pretrained_path is not None:
            self.load(pretrained_path)

    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates an PTv3Seg model object from a Deep Learning Package(DLPK)
        or Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Deep Learning Package
                                (DLPK) or Esri Model Definition(EMD) file.
        ---------------------   -------------------------------------------
        data                    Required fastai Databunch or None. Returned data
                                object from :meth:`~arcgis.learn.prepare_data` function or None for
                                inferencing.
        =====================   ===========================================

        :return: :class:`~arcgis.learn.PTv3Seg`  Object
        """
        if not HAS_FASTAI:
            _raise_fastai_import_error(import_exception=import_exception)

        emd_path = _get_emd_path(emd_path)
        with open(emd_path) as f:
            emd = json.load(f)

        model_file = Path(emd["ModelFile"])
        if not model_file.is_absolute():
            model_file = emd_path.parent / model_file
        model_params = emd["ModelParameters"]["encoder_params"]

        try:
            class_mapping = {i["Value"]: i["Name"] for i in emd["Classes"]}
            color_mapping = {i["Value"]: i["Color"] for i in emd["Classes"]}
        except KeyError:
            class_mapping = {i["ClassValue"]: i["ClassName"] for i in emd["Classes"]}
            color_mapping = {i["ClassValue"]: i["Color"] for i in emd["Classes"]}

        if data is None:
            data = _EmptyData(
                path=emd_path.parent.parent,
                loss_func=None,
                c=len(class_mapping),
                chip_size=emd["ImageHeight"],
            )
            data._is_empty = True
            data.emd_path = emd_path
            data.emd = emd
            for key, value in emd["DataAttributes"].items():
                setattr(data, key, value)

            ## backward compatibility.
            if not hasattr(data, "class_mapping"):
                data.class_mapping = class_mapping
                if not hasattr(data, "class2idx"):
                    data.class2idx = class_mapping
            if not hasattr(data, "color_mapping"):
                data.color_mapping = color_mapping
            if not hasattr(data, "class2idx"):
                data.class2idx = data.class_mapping
            if not hasattr(data, "classes"):
                data.classes = list(data.class2idx.values())

            data.class2idx = {int(k): int(v) for k, v in data.class2idx.items()}
            if hasattr(data, "idx2class"):
                data.idx2class = {int(k): int(v) for k, v in data.idx2class.items()}

            data.color_mapping = {int(k): v for k, v in data.color_mapping.items()}

            ## Below are the lines to make save function work
            data.chip_size = None
            data._image_space_used = None
            data.dataset_type = "PointCloud"

        return cls(data, **model_params, pretrained_path=str(model_file))
