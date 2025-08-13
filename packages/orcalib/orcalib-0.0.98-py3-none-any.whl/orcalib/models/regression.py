from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Literal, Unpack, overload

import numpy as np
import torch
from datasets import Dataset
from numpy.typing import NDArray
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

from orcalib.models.model_finetuning import MemoryAugmentedTrainingArguments, finetune
from orcalib.utils.progress import OnLogCallback

from ..memoryset import InputType, InputTypeList, Memoryset
from ..shared.metrics import RegressionMetrics, calculate_regression_metrics
from ..torch_layers import (
    MemoryMixtureOfExpertsRegressionHead,
    NearestMemoriesRegressionHead,
)
from ..utils import OnProgressCallback, parse_dataset, safely_call_on_progress
from .base_model import MemoryAugmentedModel, MemoryAugmentedModelInput
from .prediction_types import ScorePredictionMemoryLookup, ScorePredictionWithMemories


class RARHeadType(str, Enum):
    MMOE = "MMOE"
    KNN = "KNN"


class RARModelConfig(PretrainedConfig):
    model_type = "rar-model"

    head_type: RARHeadType
    memoryset_uri: str | None
    memoryset: Memoryset[Literal["scored"]]
    memory_lookup_count: int | None
    weigh_memories: bool | None
    min_memory_weight: float | None
    num_layers: int | None
    dropout_prob: float | None

    def __init__(
        self,
        memoryset_uri: str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool | None = None,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
        **kwargs,
    ):
        """
        Initialize the config

        Note:
            While all args of a pretrained config must be optional, `memoryset_uri` must be specified.

        Args:
            memoryset_uri: URI of the memoryset to use, this is required
            memory_lookup_count: Number of memories to lookup for each input, defaults to 10
            head_type: Type of regression head to use, either "MMOE" or "KNN"
            weigh_memories: Optional parameter for KNN head, whether to weigh memories by their lookup score
            min_memory_weight: Optional parameter for KNN head, minimum memory weight under which memories are ignored
            num_layers: Optional parameter for MMOE head, number of layers in the feed forward network
            dropout_prob: Optional parameter for MMOE head, dropout probability
        """
        # We cannot require memoryset_uri here, because this class must be initializable without
        # passing any parameters for the PretrainedConfig.save_pretrained method to work, so instead
        # we throw an error in the RetrievalAugmentedRegressor initializer if it is missing
        self.memoryset_uri = memoryset_uri
        self.memory_lookup_count = memory_lookup_count
        self.head_type = head_type if isinstance(head_type, RARHeadType) else RARHeadType(head_type)
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob
        super().__init__(**kwargs)


class RARModel(MemoryAugmentedModel):
    """A retrieval augmented regression model that uses a memoryset to make predictions."""

    config_class = RARModelConfig
    base_model_prefix = "rar"
    memory_lookup_count: int
    memoryset: Memoryset[Literal["scored"]]

    def _init_head(self):
        match self.config.head_type:
            case RARHeadType.MMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or 10
                self.head = MemoryMixtureOfExpertsRegressionHead(
                    embedding_dim=self.embedding_dim,
                )
            case RARHeadType.KNN:
                self.memory_lookup_count = self.config.memory_lookup_count or 10
                self.head = NearestMemoriesRegressionHead(
                    weigh_memories=self.config.weigh_memories,
                    min_memory_weight=self.config.min_memory_weight,
                )
            case _:
                raise ValueError(f"Unsupported head type: {self.config.head_type}")

    @overload
    def __init__(self, config: RARModelConfig):
        pass

    @overload
    def __init__(
        self,
        *,
        memoryset: Memoryset[Literal["scored"]] | str,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool | None = None,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        pass

    def __init__(
        self,
        config: RARModelConfig | None = None,
        *,
        memoryset: Memoryset[Literal["scored"]] | str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool | None = None,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        if config is None:
            assert memoryset is not None
            if isinstance(memoryset, Memoryset):
                self.memoryset = memoryset
            else:
                self.memoryset = Memoryset.connect(memoryset)
            config = RARModelConfig(
                memoryset_uri=self.memoryset.uri,
                memory_lookup_count=memory_lookup_count,
                head_type=head_type,
                weigh_memories=True if weigh_memories is None else weigh_memories,
                min_memory_weight=min_memory_weight,
                num_layers=num_layers,
                dropout_prob=dropout_prob,
            )
        else:
            assert (
                memoryset is not None
                or memory_lookup_count is not None
                or head_type is not None
                or weigh_memories is not None
                or min_memory_weight is not None
                or num_layers is not None
                or dropout_prob is not None
            ), "Either config or kwargs can be provided, not both"
            if not config.memoryset_uri:
                # all configs must have defaults in a PretrainedConfig, but this one is required
                raise ValueError("memoryset_uri must be specified in config")
            self.memoryset = Memoryset.connect(config.memoryset_uri)
        assert self.memoryset.memory_type == "scored"
        super().__init__(config)
        self.embedding_dim = self.memoryset.embedding_model.embedding_dim
        self._init_head()
        self.criterion = nn.MSELoss()

    @property
    def num_trainable_parameters(self) -> int:
        """Number of trainable parameters in the model"""
        return self.num_parameters(only_trainable=True)

    def reset(self):
        """Reset the model weights to their initial state"""
        self._init_head()

    def forward(
        self,
        **kwargs: Unpack[MemoryAugmentedModelInput],
    ) -> SequenceClassifierOutput:
        logits = self.head(
            memories_embeddings=kwargs["memories_embeddings"],
            memories_scores=kwargs["memories_labels"],
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
        score_column: str = "score",
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
            score_column: The column in the dataset that contains the expected scores
            training_args: The training arguments to use for the finetuning
            on_progress: Callback to report progress
        """
        if not train_dataset:
            train_dataset = self.memoryset.to_dataset()
        else:
            train_dataset = parse_dataset(train_dataset, value_column=value_column, score_column=score_column)
        if eval_dataset:
            eval_dataset = parse_dataset(eval_dataset, value_column=value_column, score_column=score_column)

        finetune(
            self,
            checkpoint_dir=checkpoint_dir,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            training_args=training_args,
            on_progress=on_progress,
            on_log=on_log,
        )

    def _estimate_confidence(
        self,
        attention_weights: list[float] | NDArray[np.float32],
        memory_scores: list[float] | NDArray[np.float32],
    ) -> float:
        """
        Estimate the confidence of a regression prediction based on attention weights and memory scores.

        The confidence is computed using:
        1. Attention entropy: How focused vs spread out the attention is
        2. Score variance: How much the scores of attended memories vary

        Args:
            attention_weights: The attention weights for each memory
            memory_scores: The scores of each memory

        Returns:
            A confidence score between 0 and 1
        """
        from scipy.stats import entropy

        # Convert to numpy arrays if needed
        attention_weights = np.array(attention_weights, dtype=np.float32)
        memory_scores = np.array(memory_scores, dtype=np.float32)

        # Normalize attention weights to sum to 1
        attention_weights = attention_weights / np.sum(attention_weights)

        # Compute attention entropy (normalized to [0, 1])
        max_entropy = np.log(len(attention_weights))
        attention_entropy = entropy(attention_weights) / max_entropy if max_entropy > 0 else 0
        attention_focus = 1 - attention_entropy  # Higher focus = more confident

        # Compute weighted standard deviation of scores
        weighted_mean = np.sum(attention_weights * memory_scores)
        weighted_var = np.sum(attention_weights * (memory_scores - weighted_mean) ** 2)
        weighted_std = np.sqrt(weighted_var)

        # Scale std to [0, 1] using a soft threshold
        # We use 2 * weighted_mean as a reference - if std is larger than this, confidence goes to 0
        score_consistency = 1 / (1 + (weighted_std / (abs(weighted_mean) + 1e-6)))

        # Combine the two factors with more weight on score consistency
        confidence = 0.3 * attention_focus + 0.7 * score_consistency

        return float(confidence)

    @overload
    def predict(
        self,
        value: InputType,
        use_lookup_cache: bool = True,
        expected_score: float | None = None,
        prompt: str | None = None,
    ) -> ScorePredictionWithMemories:
        pass

    @overload
    def predict(
        self,
        value: InputTypeList,
        use_lookup_cache: bool = True,
        expected_score: list[float] | None = None,
        prompt: str | None = None,
    ) -> list[ScorePredictionWithMemories]:
        pass

    @torch.no_grad()
    def predict(
        self,
        value: InputType | InputTypeList,
        use_lookup_cache: bool = True,
        expected_score: float | list[float] | None = None,
        prompt: str | None = None,
    ) -> ScorePredictionWithMemories | list[ScorePredictionWithMemories]:
        """
        Predict the score for a given input

        Args:
            value: The input to predict the score for
            use_lookup_cache: Whether to use the lookup cache
            expected_score: Expected score(s) for evaluation purposes
            prompt: Optional prompt for instruction-tuned embedding models

        Returns:
            Either a single prediction or a list of predictions depending on the input type
        """
        timestamp = datetime.now(timezone.utc)
        if expected_score is not None:
            expected_score = expected_score if isinstance(expected_score, list) else [expected_score]

        lookup_res = self.memoryset.lookup(
            [value] if not isinstance(value, list) else value,
            count=self.memory_lookup_count,
            return_type="columns",
            use_cache=use_lookup_cache,
            prompt=prompt,
        )
        logits = self.forward(
            input_embeddings=torch.tensor(lookup_res["input_embeddings"]).to(self.device),
            memories_labels=torch.tensor(lookup_res["memories_scores"]).to(self.device),
            memories_embeddings=torch.tensor(lookup_res["memories_embeddings"]).to(self.device),
            memories_weights=torch.tensor(lookup_res["memories_lookup_scores"]).to(self.device),
        ).logits
        predictions = logits

        results: list[ScorePredictionWithMemories] = []
        assert isinstance(predictions, Tensor)
        for i, prediction in enumerate(predictions):
            assert self.head.last_memories_attention_weights is not None
            prediction_id = uuid4()
            predicted_score = float(prediction.item())
            attention_weights: list[float] = self.head.last_memories_attention_weights.tolist()[i]
            memory_scores = lookup_res["memories_scores"][i]

            confidence = self._estimate_confidence(attention_weights, memory_scores)
            anomaly_score = self.estimate_anomaly_score(lookup_res, i)

            result_memory_lookups = [
                ScorePredictionMemoryLookup(
                    prediction_id=prediction_id,
                    value=lookup_res["memories_values"][i][j],
                    embedding=lookup_res["memories_embeddings"][i][j],
                    score=lookup_res["memories_scores"][i][j],
                    memory_id=lookup_res["memories_ids"][i][j],
                    memory_version=lookup_res["memories_versions"][i][j],
                    source_id=lookup_res["memories_source_ids"][i][j],
                    metadata=lookup_res["memories_metadata"][i][j],
                    metrics=lookup_res["memories_metrics"][i][j],
                    created_at=lookup_res["memories_created_ats"][i][j],
                    updated_at=lookup_res["memories_updated_ats"][i][j],
                    edited_at=lookup_res["memories_edited_ats"][i][j],
                    lookup_score=lookup_res["memories_lookup_scores"][i][j],
                    attention_weight=attention_weights[j],
                )
                for j in range(self.memory_lookup_count)
            ]
            result = ScorePredictionWithMemories(
                prediction_id=prediction_id,
                score=predicted_score,
                confidence=confidence,
                timestamp=timestamp,
                input_value=value[i] if isinstance(value, list) else value,
                input_embedding=lookup_res["input_embeddings"][i],
                expected_score=expected_score[i] if expected_score is not None else None,
                memories=result_memory_lookups,
                anomaly_score=anomaly_score,
            )
            results.append(result)

        if not isinstance(value, list):
            return results[0]
        return results

    def evaluate(
        self,
        dataset: Dataset,
        value_column: str = "value",
        score_column: str = "score",
        batch_size: int = 32,
        on_progress: OnProgressCallback | None = None,
        on_predict: Callable[[list[ScorePredictionWithMemories]], None] | None = None,
        prompt: str | None = None,
    ) -> RegressionMetrics:
        """
        Evaluate the model on a given dataset

        Args:
            dataset: The data to evaluate the model on
            value_column: The column in the dataset that contains the input values
            score_column: The column in the dataset that contains the expected scores
            batch_size: The batch size to use for evaluation
            on_progress: Optional callback to report progress
            on_predict: Optional callback to save telemetry for a batch of predictions
            prompt: Optional prompt for instruction-tuned embedding models

        Returns:
            The evaluation result with regression metrics
        """
        dataset = parse_dataset(dataset, value_column=value_column, score_column=score_column)

        predicted_scores: list[float] = []
        anomaly_scores: list[float] = []

        # Process dataset in batches
        safely_call_on_progress(on_progress, 0, len(dataset))
        for i in trange(0, len(dataset), batch_size, disable=on_progress is not None):
            batch = dataset[i : i + batch_size]
            predictions = self.predict(
                batch["value"], use_lookup_cache=True, expected_score=batch["score"], prompt=prompt
            )
            if on_predict:
                on_predict(predictions)
            predicted_scores.extend([p.score for p in predictions])
            anomaly_scores.extend([p.anomaly_score for p in predictions])
            safely_call_on_progress(on_progress, len(predicted_scores), len(dataset))

        return calculate_regression_metrics(
            expected_scores=dataset["score"],
            predicted_scores=predicted_scores,
            anomaly_scores=anomaly_scores,
        )


AutoConfig.register("rar-model", RARModelConfig)
AutoModelForSequenceClassification.register(RARModelConfig, RARModel)
AutoModelForImageClassification.register(RARModelConfig, RARModel)
