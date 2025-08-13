from datetime import datetime

from pydantic import UUID4, BaseModel

from ..memoryset import InputType, LabeledMemoryLookup, ScoredMemoryLookup
from ..utils.pydantic import Vector


class BasePredictionResult(BaseModel):
    """Predicted label and confidence for a single input."""

    prediction_id: UUID4 | None
    """The unique ID to identify this prediction"""

    confidence: float
    """The confidence of the prediction."""

    anomaly_score: float | None
    """The score for how anomalous the input is relative to the memories."""


class BasePredictionProps(BaseModel):
    """Predicted label and confidence for a single input."""

    timestamp: datetime
    """The time when the prediction was requested"""

    input_value: InputType
    """The input to the model."""

    input_embedding: Vector
    """The embedding of the input."""


class BaseLabelPredictionResult(BasePredictionResult):
    """Predicted label and confidence for a single input."""

    label: int
    """The predicted label."""

    label_name: str | None
    """The name of the predicted label."""

    logits: Vector
    """The logits of the prediction."""

    def __repr__(self) -> str:
        label = f"<{self.label_name}: {str(self.label)}>" if self.label_name else str(self.label)
        return f"LabelPredictionResult(label={label}, confidence={self.confidence:.4f})"


class LabelPredictionResult(BaseLabelPredictionResult):
    """Predicted label and confidence for a single input."""

    prediction_id: UUID4  # type: ignore[override]
    """The unique ID to identify this prediction"""

    def __repr__(self) -> str:
        label = f"<{self.label_name}: {str(self.label)}>" if self.label_name else str(self.label)
        return f"LabelPredictionResult(label={label}, confidence={self.confidence:.4f})"


class LabelPrediction(BasePredictionProps, LabelPredictionResult):
    """Full details about a single label prediction."""

    logits: Vector
    """The logits of the prediction."""

    expected_label: int | None
    """The expected label for the input, if available (e.g. during evaluation)"""

    expected_label_name: str | None
    """The name of the expected label, if available (e.g. during evaluation)"""


class PredictionMemoryLookupProps(BaseModel):
    """Full information about the lookup of a single memory for a prediction."""

    prediction_id: UUID4
    """The unique ID of the prediction that this lookup was made for"""

    attention_weight: float
    """The attention the model gave to this memory lookup."""


class LabelPredictionMemoryLookup(PredictionMemoryLookupProps, LabeledMemoryLookup):
    """Full information about the lookup of a single memory for a prediction."""

    def __repr__(self) -> str:
        return "".join(
            [
                "LabeledMemoryLookup(\n",
                f"    value={(chr(39) + self.value + chr(39)) if isinstance(self.value, str) else '<Image>'},\n",
                f"    label={('<' + self.label_name + ': ' + str(self.label) + '>') if self.label_name else str(self.label)},\n",
                f"    metadata={self.metadata},\n" if self.metadata else "",
                f"    prediction_id={self.prediction_id},\n",
                f"    memory_id={self.memory_id},\n",
                f"    memory_version={self.memory_version},\n",
                f"    attention_weight={self.attention_weight},\n" if self.attention_weight else "",
                f"    lookup_score={self.lookup_score},\n",
                f"    embedding=<array.{self.embedding.dtype}{self.embedding.shape}>,\n",
                ")",
            ]
        )


class LabelPredictionWithMemories(LabelPrediction):
    """Result for a single prediction with full details and details of the memory lookups"""

    memories: list[LabelPredictionMemoryLookup]
    """The memory lookups that were used to guide this prediction."""

    def __repr__(self) -> str:
        return (
            "LabelPredictionWithMemories(\n"
            f"    label={('<' + self.label_name + ': ' + str(self.label) + '>') if self.label_name else str(self.label)},\n"
            f"    confidence={self.confidence:.4f},\n"
            f"    logits=<array.{self.logits.dtype}{self.logits.shape}>,\n"
            f"    input_embedding=<array.{self.input_embedding.dtype}{self.input_embedding.shape}>,\n"
            f"    memories=<list.LabelPredictionMemoryLookup({len(self.memories)})>,\n"
            ")"
        )


class BaseScorePredictionResult(BasePredictionResult):
    """Predicted score and confidence for a single input."""

    score: float
    """The predicted score."""

    def __repr__(self) -> str:
        return f"ScorePredictionResult(score={self.score}, confidence={self.confidence:.4f})"


class ScorePredictionResult(BaseScorePredictionResult):
    """Predicted score and confidence for a single input."""

    prediction_id: UUID4  # type: ignore[override]
    """The unique ID to identify this prediction"""

    def __repr__(self) -> str:
        return f"ScorePredictionResult(score={self.score}, confidence={self.confidence:.4f})"


class ScorePrediction(BasePredictionProps, ScorePredictionResult):
    """Full details about a single score prediction."""

    expected_score: float | None
    """The expected score for the input, if available (e.g. during evaluation)"""


class ScorePredictionMemoryLookup(PredictionMemoryLookupProps, ScoredMemoryLookup):
    """Full information about the lookup of a single memory for a prediction."""

    def __repr__(self) -> str:
        return "".join(
            [
                "ScoredMemoryLookup(\n",
                f"    value={(chr(39) + self.value + chr(39)) if isinstance(self.value, str) else '<Image>'},\n",
                f"    score={self.score},\n",
                f"    metadata={self.metadata},\n" if self.metadata else "",
                f"    prediction_id={self.prediction_id},\n",
                f"    memory_id={self.memory_id},\n",
                f"    memory_version={self.memory_version},\n",
                f"    attention_weight={self.attention_weight},\n" if self.attention_weight else "",
                f"    lookup_score={self.lookup_score},\n",
                f"    embedding=<array.{self.embedding.dtype}{self.embedding.shape}>,\n",
                ")",
            ]
        )


class ScorePredictionWithMemories(ScorePrediction):
    """Result for a single prediction with full details and details of the memory lookups"""

    memories: list[ScorePredictionMemoryLookup]
    """The memory lookups that were used to guide this prediction."""

    def __repr__(self) -> str:
        return (
            "ScoredPredictionWithMemories(\n"
            f"    score={self.score},\n"
            f"    confidence={self.confidence:.4f},\n"
            f"    input_embedding=<array.{self.input_embedding.dtype}{self.input_embedding.shape}>,\n"
            f"    memories=<list.ScoredPredictionMemoryLookup({len(self.memories)})>,\n"
            ")"
        )
