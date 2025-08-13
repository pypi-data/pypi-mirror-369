import os
import json
import traceback
import logging
import warnings
import pandas as pd

from ._llm import LLM

try:
    from ._ner_spacy import _SpacyEntityRecognizer
    from .._utils._ner_utils import spaCyNERDatabunch
    from arcgis.features import FeatureSet

    warnings.filterwarnings("ignore", category=UserWarning)
    HAS_SPACY = True
except Exception as e:
    spacy_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    HAS_SPACY = False

try:
    from ._ner_transformer import (
        _TransformerEntityRecognizer,
        backbone_models_reverse_map,
    )
    from .._utils.text_data import TextDataObject
    from .._utils.common import _get_emd_path
    from ._model_extension_text import TextModelExtension
    from transformers import AutoConfig

    HAS_TRANSFORMERS = True
except Exception as e:
    transformer_exception = "\n".join(
        traceback.format_exception(type(e), e, e.__traceback__)
    )
    HAS_TRANSFORMERS = False

    class _TransformerEntityRecognizer:
        supported_backbones = []


try:
    from ._ner_llm import _LlmEntityRecognizer

except Exception as e:
    llm_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))


def _raise_spacy_import_error():
    error_message = (
        f"{spacy_exception}\n\n\n"
        "This module requires spacy version 2.1.8 or above and fastprogress."
        "Install it using 'pip install spacy==2.1.8 fastprogress pandas'"
    )
    raise Exception(error_message)


def _raise_transformers_import_error():
    error_message = (
        f"{transformer_exception}\n\n\n"
        "This module requires transformers version 3.3.0, "
        "install it using 'pip install transformers==3.3.0'"
    )
    raise Exception(error_message)


class EntityRecognizer:
    """
    Creates an entity recognition model to extract text entities from unstructured text documents.

    To load a custom DLPK using the model extensibility support, instantiate an object of the class using `from_model`.

    =====================   ===========================================
    **Parameter**            **Description**
    ---------------------   -------------------------------------------
    data                    Optional data object returned from :meth:`~arcgis.learn.prepare_textdata` function.
                            data object can be `None`, in case where someone wants to use a
                            Hugging Face Transformer model fine-tuned on entity-recognition
                            task. In this case the model should be used directly for inference.
    ---------------------   -------------------------------------------
    lang                    Optional string. Language-specific code,
                            named according to the language’s `ISO code <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_
                            The default value is 'en' for English.
    ---------------------   -------------------------------------------
    backbone                Optional string. Specify `spacy`, `mistral` or the  HuggingFace
                            transformer model name to be used to train the
                            entity recognizer model. Default set to `spacy`.

                            Entity recognition via `spaCy` is based on <https://spacy.io/api/entityrecognizer>

                            To learn more about the available transformer models or
                            choose models that are suitable for your dataset,
                            kindly visit:- https://huggingface.co/transformers/pretrained_models.html

                            To learn more about the available transformer models fine-tuned
                            on Named Entity Recognition Task, kindly visit:-
                            https://huggingface.co/models?pipeline_tag=token-classification

                            To learn more about mistral, kindly visit:
                            https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2

    =====================   ===========================================

    **kwargs**

    =====================   ===========================================
    **Parameter**            **Description**
    ---------------------   -------------------------------------------
    verbose                 Optional string. Default set to `error`. The
                            log level you want to set. It means the amount
                            of information you want to display while training
                            or calling the various methods of this class.
                            Allowed values are - `debug`, `info`, `warning`,
                            `error` and `critical`. Applicable only for models
                            with HuggingFace transformer backbones.
    ---------------------   -------------------------------------------
    seq_len                 Optional Integer. Default set to 512. Maximum
                            sequence length (at sub-word level after tokenization)
                            of the training data to be considered for training
                            the model. Applicable only for models with
                            HuggingFace transformer backbones.
    ---------------------   -------------------------------------------
    mixed_precision         Optional Bool. Default set to False. If set
                            True, then mixed precision training is used
                            to train the model. Applicable only for models
                            with HuggingFace transformer backbones.
    ---------------------   -------------------------------------------
    pretrained_path         Optional String. Path where pre-trained model
                            is saved. Accepts a Deep Learning Package
                            (DLPK) or Esri Model Definition(EMD) file.
    ---------------------   -------------------------------------------
    prompt                  Optional String. This parameter is applicable if the selected model backbone is from the
                            LLM family.

                            This parameter outlines the task and its corresponding guardrails.
    ---------------------   -------------------------------------------
    examples                Optional List. The list comprises tuple(s) where the first element denotes the text for
                            entity extraction, while the second element is a dictionary used for mapping named entities.

                            This parameter is applicable if the selected model backbone is from the LLM family.

                            Pydantic Schema: List[Tuple[str, Dict[str, List]]]

                            Example: [("Jim stays in London", {"name": ["Jim"], "location": ["London"]})]

                            If examples are not supplied, a data object must be provided.
    ---------------------   -------------------------------------------
    =====================   ===========================================

    :return: :class:`~arcgis.learn.text.EntityRecognizer` Object
    """

    supported_backbones = ["spacy"] + _TransformerEntityRecognizer.supported_backbones

    def __init__(self, data=None, lang="en", backbone="spacy", **kwargs):

        self.model_extension = False
        self.inference_model = None

        if kwargs.get("model_extension", False):
            self.inference_model = kwargs.get("extensible_model", None)
            assert self.inference_model is not None
            self.inference_model = self.inference_model.model
            self.model_extension = True
            return

        if backbone in backbone_models_reverse_map:
            if backbone_models_reverse_map[backbone] == "llm":
                backup_backbone = backbone
                kwargs["submodel"] = backup_backbone
                kwargs.update(kwargs.get("llm_params", {}))
                backbone = "llm"
                self.backbone = backbone

        create_empty = kwargs.get("create_empty", False)
        if backbone == "llm":
            if create_empty:
                pass
            else:
                self._model = _LlmEntityRecognizer(data, backbone=backbone, **kwargs)
                return
        self.data = data
        self.lang = lang
        self.backbone = backbone
        self.entities = None
        if create_empty:
            pass
        else:
            if data is None:
                model = EntityRecognizer.from_pretrained(backbone, **kwargs)
                self._model = model._model
                self.entities = self._model.entities
            elif data and backbone == "spacy":
                if not HAS_SPACY:
                    _raise_spacy_import_error()
                if data.backbone != "spacy":
                    logging.info("Preparing data for spacy backbone!")
                    data.prepare_data_for_spacy()
                data_obj = data.get_data_object()
                self._model = _SpacyEntityRecognizer(data_obj, lang=lang, **kwargs)
            elif data:
                if not HAS_TRANSFORMERS:
                    _raise_transformers_import_error()
                model_config = AutoConfig.from_pretrained(backbone)

                if data.backbone == "spacy":
                    logging.info("Preparing data for transformer backbone!")
                    if model_config.id2label != {0: "LABEL_0", 1: "LABEL_1"}:
                        label2id, id2label = (
                            model_config.label2id,
                            model_config.id2label,
                        )
                        # sci-bert has `label2id` mapping as {"LABEL_0": 0, "LABEL_1": 1, "LABEL_10": 10...} and
                        # `id2label` mapping as {"0": "I-cell_type", "1": "B-DNA", "2": "O"...}, hence this hack
                        if label2id != {y: x for x, y in id2label.items()} and not any(
                            ["-" in x for x in label2id.keys()]
                        ):
                            label2id = {y: x for x, y in id2label.items()}
                        labels = list(label2id.keys())
                    else:
                        labels, label2id = [], None
                    logging.info(f"Labels - {labels}\n\tlabel2id mappings - {label2id}")
                    ignore_tag_order = not any(["-" in label for label in labels])
                    data.prepare_data_for_transformer(
                        ignore_tag_order=ignore_tag_order, label2id=label2id
                    )
                data_obj = data.get_data_object()
                kwargs.update({"model_config": model_config})
                self._model = _TransformerEntityRecognizer(data_obj, backbone, **kwargs)

        if create_empty is False:
            self.train_ds = self._model.train_ds
            self.valid_ds = self._model.val_ds

    @staticmethod
    def _available_metrics():
        return ["valid_loss", "precision_score", "recall_score", "f1_score"]

    @property
    def available_metrics(self):
        """
        List of available metrics that are displayed in the training
        table. Set `monitor` value to be one of these while calling
        the `fit` method.
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )

        if self.backbone == "llm":
            return ["precision_score", "recall_score", "f1_score"]

        return ["valid_loss", "precision_score", "recall_score", "f1_score"]

    @classmethod
    def available_backbone_models(cls, architecture):
        """
        Get available models for the given entity recognition backbone

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        architecture            Required string. name of the architecture or 'llm'
                                one wishes to use.

                                To learn more about
                                the available models or choose models that are
                                suitable for your dataset, kindly visit:-
                                https://huggingface.co/transformers/pretrained_models.html


                                To learn more about `llm` and mistral
                                https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
        =====================   ===========================================

        :return: a tuple containing the available models for the given entity recognition backbone
        """

        if architecture == "spacy":
            return ("spacy",)
        else:
            return _TransformerEntityRecognizer.available_backbone_models(architecture)

    def lr_find(self, allow_plot=True, **kwargs):
        """
        Runs the Learning Rate Finder. Helps in choosing the
        optimum learning rate for training the model.

        This method is not supported when the backbone is configured as llm/mistral.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        allow_plot              Optional boolean. Display the plot of losses
                                against the learning rates and mark the optimal
                                value of the learning rate on the plot.
                                The default value is 'True'.
        =====================   ===========================================
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        return self._model.lr_find(allow_plot=allow_plot, **kwargs)

    def unfreeze(self):
        """
        Unfreezes the earlier layers of the model for fine-tuning.

        This method is not supported when the backbone is configured as llm/mistral.
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        self._model.unfreeze()

    def freeze(self):
        """
        Freeze up to last layer group to train only the last layer group of the model.

        This method is not supported when the backbone is configured as llm/mistral.
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        self._model.freeze()

    def fit(
        self,
        epochs=20,
        lr=None,
        one_cycle=True,
        early_stopping=False,
        checkpoint=True,
        **kwargs,
    ):
        """
        Train the model for the specified number of epochs and using the
        specified learning rates

        This method is not supported when the backbone is configured as llm/mistral.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        epochs                  Required integer. Number of cycles of training
                                on the data. Increase it if underfitting.
        ---------------------   -------------------------------------------
        lr                      Optional float or slice of floats. Learning rate
                                to be used for training the model. If ``lr=None``,
                                an optimal learning rate is automatically deduced
                                for training the model.

                                .. note::
                                    Passing slice of floats as `lr` value is not supported for models with `spaCy` backbone.
        ---------------------   -------------------------------------------
        one_cycle               Optional boolean. Parameter to select 1cycle
                                learning rate schedule. If set to `False` no
                                learning rate schedule is used.

                                .. note::
                                        Not applicable for models with spaCy backbone
        ---------------------   -------------------------------------------
        early_stopping          Optional boolean. Parameter to add early stopping.
                                If set to 'True' training will stop if parameter
                                `monitor` value stops improving for 5 epochs.

                                .. note::
                                    Not applicable for models with spaCy backbone
        ---------------------   -------------------------------------------
        checkpoint              Optional boolean or string.
                                Parameter to save checkpoint during training.
                                If set to `True` the best model
                                based on `monitor` will be saved during
                                training. If set to 'all', all checkpoints
                                are saved. If set to False, checkpointing will
                                be off. Setting this parameter loads the best
                                model at the end of training.

                                .. note::
                                    Not applicable for models with spaCy backbone
        ---------------------   -------------------------------------------
        tensorboard             Optional boolean. Parameter to write the training log.
                                If set to 'True' the log will be saved at
                                <dataset-path>/training_log which can be visualized in
                                tensorboard. Required tensorboardx version=2.1

                                The default value is 'False'.

                                .. note::
                                    Not applicable for Text Models
        ---------------------   -------------------------------------------
        monitor                 Optional string. Parameter specifies
                                which metric to monitor while checkpointing
                                and early stopping. Defaults to 'valid_loss'. Value
                                should be one of the metric that is displayed in
                                the training table. Use `{model_name}.available_metrics`
                                to list the available metrics to set here.

                                .. note::
                                        Not applicable for models with spaCy backbone
        =====================   ===========================================
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        self._model.fit(
            epochs=epochs,
            lr=lr,
            one_cycle=one_cycle,
            early_stopping=early_stopping,
            checkpoint=checkpoint,
            **kwargs,
        )
        self.entities = self._model.entities

    def save(self, name_or_path, **kwargs):
        """
        Saves the model weights, creates an Esri Model Definition and Deep
        Learning Package zip for deployment to Image Server or ArcGIS Pro.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Name of the model to save. It
                                stores it at the pre-defined location. If path
                                is passed then it stores at the specified path
                                with model name as directory name and creates
                                all the intermediate directories.
        ---------------------   -------------------------------------------
        publish                 Optional boolean. Publishes the DLPK as an item.
                                Default is set to False.
        ---------------------   -------------------------------------------
        gis                     Optional :class:`~arcgis.gis.GIS`  Object. Used for publishing the item.
                                If not specified then active gis user is taken.
        ---------------------   -------------------------------------------
        compute_metrics         Optional boolean. Used for computing model
                                metrics. Default is set to True.
        ---------------------   -------------------------------------------
        save_optimizer          Optional boolean. Used for saving the model-optimizer
                                state along with the model. Default is set to False
                                Not applicable for models with `spaCy` backbone.
        =====================   ===========================================

        **kwargs**

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        overwrite               Optional boolean `overwrite` if True, it will overwrite
                                the item on ArcGIS Online/Enterprise, default False.
        ---------------------   -------------------------------------------
        zip_files               Optional boolean `zip_files` if True, it will create the Deep
                                Learning Package (DLPK) file while saving the model.
        =====================   ===========================================
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        return self._model.save(name_or_path=name_or_path, **kwargs)

    def load(self, name_or_path):
        """

        Loads a saved EntityRecognizer model from disk.

        This method is not supported when the backbone is configured as llm/mistral.

        To load a custom DLPK using the model extensibility support, instantiate an object of the class using `from_model`.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Path to Deep Learning Package
                                (DLPK) or Esri Model Definition(EMD) file.
        =====================   ===========================================
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        self._model.load(name_or_path=name_or_path)
        self.entities = self._model.entities

    @classmethod
    def from_pretrained(cls, backbone, **kwargs):
        """
        Creates an EntityRecognizer model object from an already fine-tuned
        Hugging Face Transformer backbone.

        This method is not supported when the backbone is configured as llm/mistral.

        To load a custom DLPK using the model extensibility support, instantiate an object of the class using `from_model`.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        backbone                Required string. Specify the Hugging Face Transformer
                                backbone name fine-tuned on Named Entity Recognition(NER)/
                                Token Classification task.

                                To get more details on available transformer models
                                fine-tuned on Named Entity Recognition(NER) Task, kindly visit:-
                                https://huggingface.co/models?pipeline_tag=token-classification
        =====================   ===========================================

        **kwargs**

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        verbose                 Optional string. Default set to `error`. The
                                log level you want to set. It means the amount
                                of information you want to display while calling
                                the various methods of this class. Allowed values
                                are - `debug`, `info`, `warning`, `error` and `critical`.
        =====================   ===========================================

        :return: :class:`~arcgis.learn.text.EntityRecognizer` Object
        """
        backup_backbone = backbone
        if backbone in backbone_models_reverse_map:
            if backbone_models_reverse_map[backbone] == "llm":
                backbone = "llm"

        if "spacy" in backbone or "llm" in backbone:
            error_message = (
                f"Wrong backbone - `{backup_backbone}` supplied. Only HuggingFace model names fine-tuned on "
                "`TokenClassification` tasks are allowed to be passed as `backbone` in the method."
            )
            raise Exception(error_message)

        model_config = AutoConfig.from_pretrained(backbone)
        if model_config.id2label == {0: "LABEL_0", 1: "LABEL_1"}:
            error_message = (
                f"Wrong backbone - `{backbone}` supplied. This backbone is not fine-tuned on a"
                "`TokenClassification` task. Kindly choose an appropriate backbone to call this method."
                "Visit:- https://huggingface.co/models?pipeline_tag=token-classification to find models"
                " for `NamedEntityRecognition` or `TokenClassification` tasks."
            )
            raise Exception(error_message)

        label2id, id2label = model_config.label2id, model_config.id2label
        # sci-bert has `label2id` mapping as {"LABEL_0": 0, "LABEL_1": 1, "LABEL_10": 10...} and
        # `id2label` mapping as {"0": "I-cell_type", "1": "B-DNA", "2": "O"...}, hence this hack
        if label2id != {y: x for x, y in id2label.items()} and not any(
            ["-" in x for x in label2id.keys()]
        ):
            label2id = {y: x for x, y in id2label.items()}

        model = _TransformerEntityRecognizer._from_pretrained(
            backbone, label2id, **kwargs
        )

        clas_object = cls(data=None, backbone=backbone, create_empty=True)

        clas_object._model = model
        clas_object.entities = clas_object._model.entities
        clas_object.train_ds = clas_object._model.train_ds
        clas_object.valid_ds = clas_object._model.val_ds

        return clas_object

    @classmethod
    def from_model(cls, emd_path, data=None, **kwargs):
        """
        Creates an EntityRecognizer model object from a Deep Learning
        Package(DLPK) or Esri Model Definition (EMD) file.

        To load a custom DLPK using the model extensibility support, instantiate an object of the class using this
        method.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Deep Learning Package
                                (DLPK) or Esri Model Definition(EMD) file.
        ---------------------   -------------------------------------------
        data                    Required DatabunchNER object or None. Returned data
                                object from :meth:`~arcgis.learn.prepare_data` function or None for
                                inferencing.
        =====================   ===========================================
        :return: :class:`~arcgis.learn.text.EntityRecognizer` Object
        """
        data_obj = None
        emd_path = _get_emd_path(emd_path)
        with open(emd_path) as f:
            emd_json = json.load(f)
        backbone = emd_json.get("ModelType", "spacy").lower()
        # backward compatibility
        IS_INFERENCE_FUNCTION_SUPPORTED = False
        version = emd_json.get("ArcGISLearnVersion", None)
        if version is not None:
            major_version = int(version.split(".")[0])
            minor_version = int(version.split(".")[1])
            if minor_version >= 4 and major_version >= 2:
                IS_INFERENCE_FUNCTION_SUPPORTED = True

        if "InferenceFunction" in emd_json and IS_INFERENCE_FUNCTION_SUPPORTED:
            extensible_model = TextModelExtension.from_model(emd_path, **kwargs)
            if extensible_model.model_loaded:
                cls_object = cls(
                    data,
                    backbone,
                    pretrained_path=str(emd_path),
                    model_extension=True,
                    extensible_model=extensible_model,
                )
                return cls_object

        backup_backbone = backbone
        if backbone in backbone_models_reverse_map:
            if backbone_models_reverse_map[backbone] == "llm":
                backbone = "llm"

        if backbone == "spacy":
            if data and data.backbone != "spacy":
                logging.info("Preparing data for spacy backbone!")
                data.prepare_data_for_spacy()
            if data:
                data_obj = data.get_data_object()
            model = _SpacyEntityRecognizer.from_model(emd_path=emd_path, data=data_obj)
        elif backbone == "llm":
            emd_json.update(kwargs.get("llm_params", {}))
            model = _LlmEntityRecognizer.from_model(data, backup_backbone, emd_json)
            clas_object = cls(data=None, backbone=backbone, create_empty=True)
            clas_object._model = model
            return clas_object
        else:
            if data and data.backbone == "spacy":
                logging.info("Preparing data for transformer backbone!")
                labels = set(emd_json["Labels"])
                label2id = emd_json["Label2Id"]
                logging.info(f"Labels - {labels}\n\tlabel2id mappings - {label2id}")
                ignore_tag_order = not any(["-" in label for label in labels])
                data.prepare_data_for_transformer(
                    ignore_tag_order=ignore_tag_order, label2id=label2id
                )
            if data:
                data_obj = data.get_data_object()
            model = _TransformerEntityRecognizer.from_model(
                emd_path=emd_path, data=data_obj
            )

        clas_object = cls(data=None, backbone=backbone, create_empty=True)

        clas_object._model = model
        clas_object.entities = clas_object._model.entities
        clas_object.train_ds = clas_object._model.train_ds
        clas_object.valid_ds = clas_object._model.val_ds

        return clas_object

    def extract_entities(
        self, text_list, drop=True, batch_size=4, show_progress=True, **kwargs
    ) -> pd.DataFrame | FeatureSet:
        """
        Extracts the entities from [documents in the mentioned path or text_list].

        Field defined as 'address_tag' in :meth:`~arcgis.learn.prepare_data` function's class mapping
        attribute will be treated as a location. In cases where trained model extracts
        multiple locations from a single document, that document will be replicated
        for each location in the resulting dataframe.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        text_list               Required string(path) or list(documents).
                                List of documents for entity extraction OR
                                path to the documents.
        ---------------------   -------------------------------------------
        drop                    Optional bool. If documents without address
                                needs to be dropped from the results.
                                Default is set to True.
        ---------------------   -------------------------------------------
        batch_size              Optional integer. Number of items to process
                                at once. (Reduce it if getting CUDA Out of Memory
                                Errors). Default is set to 4.
                                Not applicable for models with `spaCy` backbone.
        ---------------------   -------------------------------------------
        show_progress           Optional Bool. If set to True, will display a
                                progress bar depicting the items processed so far.
                                Applicable only when a list of text is passed.
        =====================   ===========================================

        **kwargs**

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        input_field             Optional string.
                                Input field name in the feature set. Supported
                                in model extension.
                                Default value: input_str
        =====================   ===========================================

        :return: Pandas DataFrame
        """
        file_name = []
        if self.model_extension:
            if isinstance(text_list, str):
                if os.path.isdir(text_list):
                    path = text_list
                    text_list, skipped_docs = [], []
                    item_names = os.listdir(path)
                    for item_name in item_names:
                        try:
                            with open(
                                f"{path}/{item_name}",
                                "r",
                                encoding="utf-16",
                                errors="ignore",
                            ) as f:
                                text_list.append(f.read())
                            file_name.append(item_name)
                        except:
                            try:
                                with open(
                                    f"{path}/{item_name}",
                                    "r",
                                    encoding="utf-8",
                                    errors="ignore",
                                ) as f:
                                    text_list.append(f.read())
                                file_name.append(item_name)
                            except Exception as e:
                                self.logger.exception(e)
                                skipped_docs.append(item_name)
                    if len(skipped_docs):
                        print(
                            "Unable to read the following documents ",
                            ", ".join(skipped_docs),
                        )
                    if not len(file_name):
                        raise Exception(
                            "Unable to read any of the document from the folder."
                        )
                else:
                    text_list = [text_list]
            # To make it more flexible. We will add the Featureset for further processing
            feature_set = []
            input_field = kwargs.get("input_field", "input_str")
            for i in text_list:
                feature_set.append({"attributes": {input_field: i}})

            feature_set_final = FeatureSet.from_dict(
                {
                    "fields": [
                        {"name": input_field, "type": "esriFieldTypeString"},
                    ],
                    "geometryType": "",
                    "features": feature_set,
                }
            )
            results = self.inference_model.predict(
                feature_set_final, **{"input_field": input_field}
            )
            if not isinstance(results, FeatureSet):
                raise Exception(
                    "The output should be a FeatureSet. Please refer https://developers.arcgis.com/python/api-reference/arcgis.features.toc.html#featureset"
                )

            return results

        return self._model.extract_entities(
            text_list, drop=drop, batch_size=batch_size, show_progress=show_progress
        )

    def show_results(self, rows=5, ds_type="valid"):
        """
        Runs entity extraction on a random batch from the mentioned ds_type.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        ds_type                 Optional string, defaults to valid.
        ---------------------   -------------------------------------------
        rows                    Optional integer, defaults to 5.
                                Number of rows to print.
        =====================   ===========================================

        :return: Pandas DataFrame
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        return self._model.show_results(ds_type=ds_type, rows=rows)

    def precision_score(self):
        """
        Calculate precision score of the trained model
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        return self._model.precision_score()

    def recall_score(self):
        """
        Calculate recall score of the trained model
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility only supports inference."
            )
        return self._model.recall_score()

    def f1_score(self):
        """
        Calculate F1 score of the trained model
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        return self._model.f1_score()

    def metrics_per_label(self):
        """
        Calculate precision, recall & F1 scores per labels/entities
        for which the model was trained on
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        return self._model.metrics_per_label()

    def plot_losses(self, show=True):
        """
        Plot training and validation losses.

        This method is not supported when the backbone is configured as llm/mistral.

        =====================   ===========================================
        **Parameter**            **Description**
        ---------------------   -------------------------------------------
        show                    Optional bool. Defaults to True
                                If set to False, figure will not be plotted
                                but will be returned, when set to True function
                                will plot the figure and return nothing.
        =====================   ===========================================

        :return: `matplotlib.figure.Figure <https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure>`_
        """
        if self.model_extension:
            raise Exception(
                f"This method is not supported when using the model extensibility feature, as model extensibility "
                f"only supports inference."
            )
        return self._model.plot_losses(show=show)
