from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Literal, Unpack, cast, overload

import numpy as np
import torch
from datasets import Dataset
from torch import Tensor, nn
from tqdm.auto import trange
from transformers import (
    AutoConfig,
    AutoModelForImageClassification,
    AutoModelForSequenceClassification,
)
from transformers.configuration_utils import PretrainedConfig
from transformers.modeling_outputs import SequenceClassifierOutput
from uuid_utils.compat import uuid4

from ..memoryset import InputType, InputTypeList, Memoryset
from ..memoryset.repository import FilterItem, FilterItemTuple
from ..shared import ClassificationMetrics, calculate_classification_metrics
from ..torch_layers import (
    BalancedMemoryMixtureOfExpertsClassificationHead,
    FeedForwardClassificationHead,
    MemoryMixtureOfExpertsClassificationHead,
    NearestMemoriesClassificationHead,
)
from ..utils import (
    OnLogCallback,
    OnProgressCallback,
    parse_dataset,
    safely_call_on_progress,
)
from .base_model import MemoryAugmentedModel, MemoryAugmentedModelInput
from .model_finetuning import MemoryAugmentedTrainingArguments, finetune
from .prediction_types import LabelPredictionMemoryLookup, LabelPredictionWithMemories


class RACHeadType(str, Enum):
    KNN = "KNN"
    MMOE = "MMOE"
    FF = "FF"
    BMMOE = "BMMOE"


class RACModelConfig(PretrainedConfig):
    model_type = "rac-model"

    head_type: RACHeadType
    num_classes: int | None
    memoryset_uri: str | None
    memoryset: Memoryset[Literal["labeled"]]
    memory_lookup_count: int | None
    weigh_memories: bool | None
    min_memory_weight: float | None
    num_layers: int | None
    dropout_prob: float | None
    description: str | None

    def __init__(
        self,
        memoryset_uri: str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool | None = None,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
        description: str | None = None,
        **kwargs,
    ):
        """
        Initialize the config

        Note:
            While all args of a pretrained config must be optional, `memoryset_uri` must be specified.

        Args:
            memoryset_uri: URI of the memoryset to use, this is required
            memory_lookup_count: Number of memories to lookup for each input,
                by default the system uses a simple heuristic to choose a number of memories that works well in most cases
            head_type: Type of classification head to use
            num_classes: Number of classes to predict, will be inferred from memoryset if not specified
            weigh_memories: Optional parameter for KNN head, whether to weigh memories by their lookup score
            min_memory_weight: Optional parameter for KNN head, minimum memory weight under which memories are ignored
            num_layers: Optional parameter for FF head, number of layers in the feed forward network
            dropout_prob: Optional parameter for FF head, dropout probability
        """
        # We cannot require memoryset_uri here, because this class must be initializable without
        # passing any parameters for the PretrainedConfig.save_pretrained method to work, so instead
        # we throw an error in the RetrievalAugmentedClassifier initializer if it is missing
        self.memoryset_uri = memoryset_uri
        self.memory_lookup_count = memory_lookup_count
        self.head_type = head_type if isinstance(head_type, RACHeadType) else RACHeadType(head_type)
        self.num_classes = num_classes
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob
        self.description = description
        super().__init__(**kwargs)


class RACModel(MemoryAugmentedModel):
    config_class = RACModelConfig
    base_model_prefix = "rac"
    memory_lookup_count: int
    memoryset: Memoryset[Literal["labeled"]]

    def _init_head(self):
        # TODO: break this up into three subclasses that inherit from RACModel and have their own con
        match self.config.head_type:
            case RACHeadType.MMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = MemoryMixtureOfExpertsClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                )
            case RACHeadType.BMMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = BalancedMemoryMixtureOfExpertsClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                )
            case RACHeadType.KNN:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = NearestMemoriesClassificationHead(
                    num_classes=self.num_classes,
                    weigh_memories=self.config.weigh_memories,
                    min_memory_weight=self.config.min_memory_weight,
                )
            case RACHeadType.FF:
                self.memory_lookup_count = 0
                self.head = FeedForwardClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                    num_layers=self.config.num_layers,
                )
            case _:
                raise ValueError(f"Unsupported head type: {self.config.head_type}")

    @overload
    def __init__(self, config: RACModelConfig):
        pass

    @overload
    def __init__(
        self,
        *,
        memoryset: Memoryset[Literal["labeled"]] | str,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        pass

    def __init__(
        self,
        config: RACModelConfig | None = None,
        *,
        memoryset: Memoryset[Literal["labeled"]] | str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
        description: str | None = None,
    ):
        if config is None:
            assert memoryset is not None
            if isinstance(memoryset, Memoryset):
                self.memoryset = memoryset
            else:
                self.memoryset = Memoryset.connect(memoryset)
            config = RACModelConfig(
                memoryset_uri=self.memoryset.uri,
                memory_lookup_count=memory_lookup_count,
                head_type=head_type,
                num_classes=num_classes,
                weigh_memories=weigh_memories,
                min_memory_weight=min_memory_weight,
                num_layers=num_layers,
                dropout_prob=dropout_prob,
                description=description,
            )
        else:
            assert (
                memoryset is not None
                or memory_lookup_count is not None
                or head_type is not None
                or num_classes is not None
                or weigh_memories is not None
                or min_memory_weight is not None
                or num_layers is not None
                or dropout_prob is not None
            ), "Either config or kwargs can be provided, not both"
            if not config.memoryset_uri:
                # all configs must have defaults in a PretrainedConfig, but this one is required
                raise ValueError("memoryset_uri must be specified in config")
            self.memoryset = Memoryset.connect(config.memoryset_uri)
        assert self.memoryset.memory_type == "labeled"
        super().__init__(config)
        self.embedding_dim = self.memoryset.embedding_model.embedding_dim
        if config.num_classes is None:
            logging.warning("num_classes not specified in config, using number of classes in memoryset")
            self.num_classes = self.memoryset.num_classes
        else:
            self.num_classes = config.num_classes
        self._init_head()
        self.criterion = nn.CrossEntropyLoss() if config.num_labels > 1 else nn.MSELoss()

    @property
    def num_trainable_parameters(self) -> int:
        """Number of trainable parameters in the model"""
        return self.num_parameters(only_trainable=True)

    def reset(self):
        """
        Reset the model weights to their initial state
        """
        self._init_head()

    def forward(
        self,
        **kwargs: Unpack[MemoryAugmentedModelInput],
    ) -> SequenceClassifierOutput:
        logits = self.head(
            memories_labels=kwargs["memories_labels"],
            memories_embeddings=kwargs["memories_embeddings"],
            input_embeddings=kwargs["input_embeddings"],
            memories_weights=kwargs["memories_weights"],
        )
        loss = self.criterion(logits, kwargs["labels"]) if "labels" in kwargs and kwargs["labels"] is not None else None
        return SequenceClassifierOutput(loss=loss, logits=logits)

    def finetune(
        self,
        checkpoint_dir: str | None = None,
        train_dataset: Dataset | None = None,
        eval_dataset: Dataset | None = None,
        value_column: str = "value",
        label_column: str = "label",
        training_args: MemoryAugmentedTrainingArguments = MemoryAugmentedTrainingArguments(),
        on_progress: OnProgressCallback | None = None,
        on_log: OnLogCallback | None = None,
    ):
        """
        Finetune the model on a given dataset

        Args:
            checkpoint_dir: The directory to save the checkpoint to, if this is `None` no checkpoint will be saved
            train_dataset: The data to finetune on, if this is `None` the memoryset will be used
            eval_dataset: The data to evaluate the finetuned model on, if this is `None` no evaluations will be performed
            value_column: The column in the dataset that contains the input values
            label_column: The column in the dataset that contains the expected labels
            training_args: The training arguments to use for the finetuning
            on_progress: Callback to report progress
        """
        if not train_dataset:
            train_dataset = self.memoryset.to_dataset()
        else:
            train_dataset = parse_dataset(train_dataset, value_column=value_column, label_column=label_column)
        if eval_dataset:
            eval_dataset = parse_dataset(eval_dataset, value_column=value_column, label_column=label_column)

        finetune(
            self,
            checkpoint_dir=checkpoint_dir,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            training_args=training_args,
            on_progress=on_progress,
            on_log=on_log,
        )

    def evaluate(
        self,
        dataset: Dataset,
        value_column: str = "value",
        label_column: str = "label",
        batch_size: int = 32,
        include_curves: bool = True,
        on_progress: OnProgressCallback | None = None,
        on_predict: Callable[[list[LabelPredictionWithMemories]], None] | None = None,
        prompt: str | None = None,
    ) -> ClassificationMetrics:
        """
        Evaluate the model on a given dataset

        Params:
            dataset: Data to evaluate the model on
            value_column: Column in the dataset that contains input values
            label_column: Column in the dataset that contains expected labels
            batch_size: Batch size to use for evaluation
            include_curves: Whether to include full PR and ROC curves in the evaluation result
            on_progress: Optional callback to report progress
            on_predict: Optional callback to save telemetry for a batch of predictions
            prompt: Optional prompt for instruction-tuned embedding models

        Returns:
            Evaluation result including metrics and anomaly score statistics
        """
        dataset = parse_dataset(dataset, value_column=value_column, label_column=label_column)

        logits: list[np.ndarray] = []
        anomaly_scores: list[float] = []

        # Process dataset in batches
        safely_call_on_progress(on_progress, 0, len(dataset))
        for i in trange(0, len(dataset), batch_size, disable=on_progress is not None):
            batch = dataset[i : i + batch_size]
            predictions = self.predict(
                batch["value"], use_lookup_cache=True, expected_label=batch["label"], prompt=prompt
            )
            if on_predict:
                on_predict(predictions)
            logits.extend([p.logits for p in predictions])
            anomaly_scores.extend([p.anomaly_score for p in predictions])
            safely_call_on_progress(on_progress, len(logits), len(dataset))

        return calculate_classification_metrics(
            expected_labels=dataset["label"],
            logits=logits,
            anomaly_scores=anomaly_scores,
            include_curves=include_curves,
        )

    @overload
    def predict(
        self,
        value: InputType,
        use_lookup_cache: bool = True,
        expected_label: int | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
        prompt: str | None = None,
    ) -> LabelPredictionWithMemories:
        pass

    @overload
    def predict(
        self,
        value: InputTypeList,
        use_lookup_cache: bool = True,
        expected_label: list[int] | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
        prompt: str | None = None,
    ) -> list[LabelPredictionWithMemories]:
        pass

    @torch.no_grad()
    def predict(
        self,
        value: InputType | InputTypeList,
        use_lookup_cache: bool = True,
        expected_label: int | list[int] | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
        prompt: str | None = None,
    ) -> LabelPredictionWithMemories | list[LabelPredictionWithMemories]:
        """
        Predict the label for a given input

        Args:
            value: The input to predict the label for
            use_lookup_cache: Whether to use the lookup cache
            expected_label: Expected label(s) for evaluation purposes
            filters: Optional filters to apply during memory lookup
            prompt: Optional prompt for instruction-tuned embedding models

        Returns:
            Either a single prediction or a list of predictions depending on the input type
        """
        timestamp = datetime.now(timezone.utc)
        if expected_label is not None:
            expected_label = expected_label if isinstance(expected_label, list) else [expected_label]

        if isinstance(value, list):
            list_input = True
        else:
            value = [value]
            list_input = False

        lookup_res = self.memoryset.lookup(
            value,
            count=self.memory_lookup_count,
            return_type="columns",
            use_cache=use_lookup_cache,
            filters=filters,
            prompt=prompt,
        )

        # Ensure that we have enough memories to make a prediction

        # This should be (len(value) x self.memory_lookup_count):
        lookup_memories_shape = lookup_res["memories_labels"].shape

        if lookup_memories_shape[0] != len(value):
            raise ValueError(
                f"Expected {len(value)} lookup results, but got {lookup_memories_shape[0]}",
            )

        if self.memory_lookup_count > lookup_memories_shape[1]:
            raise ValueError(
                f"Not enough memories to make a prediction, expected {self.memory_lookup_count} but only found {lookup_memories_shape[1]}"
            )

        logits = self.forward(
            input_embeddings=torch.tensor(lookup_res["input_embeddings"]).to(self.device),
            memories_labels=torch.tensor(lookup_res["memories_labels"]).to(self.device),
            memories_embeddings=torch.tensor(lookup_res["memories_embeddings"]).to(self.device),
            memories_weights=torch.tensor(lookup_res["memories_lookup_scores"]).to(self.device),
        ).logits
        assert isinstance(logits, Tensor)
        predictions = torch.argmax(logits, dim=-1)

        results: list[LabelPredictionWithMemories] = []
        for i, prediction in enumerate(predictions):
            prediction_id = uuid4()
            predicted_label = int(prediction.item())
            anomaly_score = self.estimate_anomaly_score(lookup_res, i)
            result_memory_lookups = [
                LabelPredictionMemoryLookup(
                    prediction_id=prediction_id,
                    value=lookup_res["memories_values"][i][j],
                    embedding=lookup_res["memories_embeddings"][i][j],
                    label=lookup_res["memories_labels"][i][j],
                    label_name=lookup_res["memories_label_names"][i][j],
                    memory_id=lookup_res["memories_ids"][i][j],
                    memory_version=lookup_res["memories_versions"][i][j],
                    source_id=lookup_res["memories_source_ids"][i][j],
                    metadata=lookup_res["memories_metadata"][i][j],
                    metrics=lookup_res["memories_metrics"][i][j],
                    created_at=lookup_res["memories_created_ats"][i][j],
                    updated_at=lookup_res["memories_updated_ats"][i][j],
                    edited_at=lookup_res["memories_edited_ats"][i][j],
                    lookup_score=lookup_res["memories_lookup_scores"][i][j],
                    # does not run for feed forward heads since they use memory_lookup_count = 0
                    attention_weight=cast(Tensor, self.head.last_memories_attention_weights).tolist()[i][j],
                )
                for j in range(self.memory_lookup_count)
            ]
            result = LabelPredictionWithMemories(
                prediction_id=prediction_id,
                label=predicted_label,
                label_name=self.memoryset.get_label_name(predicted_label),
                expected_label=expected_label[i] if expected_label is not None else None,
                expected_label_name=(
                    self.memoryset.get_label_name(expected_label[i]) if expected_label is not None else None
                ),
                confidence=float(logits[i][predicted_label].item()),
                timestamp=timestamp,
                input_value=value[i],
                input_embedding=lookup_res["input_embeddings"][i],
                logits=logits.to("cpu").numpy()[i],
                memories=result_memory_lookups,
                anomaly_score=anomaly_score,
            )
            results.append(result)

        if list_input:
            return results
        else:
            return results[0]


AutoConfig.register("rac-model", RACModelConfig)
AutoModelForSequenceClassification.register(RACModelConfig, RACModel)
AutoModelForImageClassification.register(RACModelConfig, RACModel)
