from collections import defaultdict

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel

from ..memoryset import LabeledMemory, LabeledMemoryLookup, LabeledMemoryset
from ..utils.pydantic import UUID7, Vector
from .analysis import MemorysetAnalysis


class MemoryLabelMetrics(BaseModel):
    neighbor_label_logits: Vector
    neighbor_predicted_label: int
    neighbor_predicted_label_ambiguity: float
    neighbor_predicted_label_confidence: float
    current_label_neighbor_confidence: float
    normalized_neighbor_label_entropy: float
    neighbor_predicted_label_matches_current_label: bool


class MemorysetLabelMetrics(BaseModel):
    class LabelClassMetrics(BaseModel):
        label: int
        """The value of the label class"""

        label_name: str | None = None
        """The name of the label class"""

        average_lookup_score: float
        """The average lookup score for the label class"""

        memory_count: int
        """The number of memories with this label"""

    label_metrics: list[LabelClassMetrics]
    """Aggregate metrics for each label class in the memoryset"""

    neighbor_prediction_accuracy: float
    """The mean hit rate of the predicted label matching the current label"""

    mean_neighbor_label_confidence: float
    """The mean confidence of the predicted label"""

    mean_neighbor_label_entropy: float
    """The mean normalized entropy of the neighbor labels"""

    mean_neighbor_predicted_label_ambiguity: float
    """The mean ambiguity of the predicted label"""


class MemorysetLabelAnalysisConfig(BaseModel):
    normalize_logits: bool = False
    """Whether to normalize the logits of the neighbor labels"""


class MemorysetLabelAnalysis(
    MemorysetAnalysis[MemorysetLabelAnalysisConfig, MemoryLabelMetrics, MemorysetLabelMetrics]
):
    """
    Analyze the labels of the memories based on their neighbors labels to detect potential mislabelings
    """

    name = "label"

    def __init__(self, config: MemorysetLabelAnalysisConfig | None = None, **kwargs):
        self.config = config or MemorysetLabelAnalysisConfig(**kwargs)

        self._label_lookup_scores: defaultdict[int, list[float]] = defaultdict(lambda: [])
        self._label_memory_counts: defaultdict[int, int] = defaultdict(lambda: 0)
        self._sum_neighbor_prediction_accuracy = 0.0
        self._sum_neighbor_label_confidence = 0.0
        self._sum_neighbor_label_entropy = 0.0
        self._sum_neighbor_predicted_label_ambiguity = 0.0

    def bind_memoryset(
        self, memoryset: LabeledMemoryset, memoryset_num_rows: int, memoryset_num_classes: int, lookup_count: int
    ) -> None:
        if lookup_count < 3:
            raise ValueError("lookup_count must be at least 3 to perform a label analysis")
        return super().bind_memoryset(memoryset, memoryset_num_rows, memoryset_num_classes, lookup_count)

    @staticmethod
    def compute_neighbor_label_logits(
        memories_labels: NDArray[np.int64],  # (batch_size, lookup_count)
        memories_lookup_scores: NDArray[np.float32],  # (batch_size, lookup_count)
        num_classes: int,
    ) -> list[Vector]:
        """Compute label classification logits based on the given neighbor labels and lookup scores."""
        batch_size, lookup_count = memories_lookup_scores.shape
        assert lookup_count > 0
        logits = np.zeros((batch_size, num_classes), dtype=np.float32)  # (batch_size, num_classes)
        label_indices = (np.arange(batch_size)[:, None], memories_labels)  # (batch_size, lookup_count)
        np.add.at(logits, label_indices, memories_lookup_scores)
        logits = logits / lookup_count
        return list(logits)

    @staticmethod
    def compute_neighbor_label_metrics(
        neighbor_label_logits: Vector, current_label: int, normalize_logits: bool = False
    ) -> MemoryLabelMetrics:
        """Compute neighbor label metrics based on the given neighbor label logits."""
        # TODO: test if there are benefits to normalizing logits, otherwise remove this option, since
        # it makes metrics less comparable between memories as confidence scores will not be small for
        # memories with few close neighbors anymore when logits are normalized.
        if normalize_logits:
            neighbor_label_logits = neighbor_label_logits / neighbor_label_logits.sum()

        # Sort the logits in ascending order for ambiguity computation
        sorted_logits = np.sort(neighbor_label_logits)

        # Compute label entropy (don't normalize because logits represent absolute likelihoods)
        assert (neighbor_label_logits >= 0).all() and (neighbor_label_logits.sum() <= 1.01)
        num_classes = neighbor_label_logits.shape[0]
        non_zero_logits = sorted_logits[sorted_logits > 0]
        entropy = -np.sum(non_zero_logits * np.log2(non_zero_logits))
        normalized_entropy = entropy / np.log2(num_classes)
        predicted_label = int(np.argmax(neighbor_label_logits))

        return MemoryLabelMetrics(
            neighbor_label_logits=neighbor_label_logits,
            neighbor_predicted_label=predicted_label,
            neighbor_predicted_label_ambiguity=float(sorted_logits[-1] - sorted_logits[-2]),
            neighbor_predicted_label_confidence=float(sorted_logits[-1]),
            current_label_neighbor_confidence=float(neighbor_label_logits[current_label]),
            normalized_neighbor_label_entropy=float(normalized_entropy),
            neighbor_predicted_label_matches_current_label=predicted_label == current_label,
        )

    def on_batch(
        self, memories_batch: list[LabeledMemory], neighbors_batch: list[list[LabeledMemoryLookup]]
    ) -> list[tuple[UUID7, MemoryLabelMetrics]]:
        """Analyze neighbor labels for a batch of memories"""

        neighbor_label_logits_batch = self.compute_neighbor_label_logits(
            memories_labels=np.array([[m.label for m in memories] for memories in neighbors_batch], dtype=np.int64),
            memories_lookup_scores=np.array(
                [[m.lookup_score for m in memories] for memories in neighbors_batch], dtype=np.float32
            ),
            num_classes=self.memoryset_num_classes,
        )
        memory_metrics: list[tuple[UUID7, MemoryLabelMetrics]] = []
        for memory, neighbor_label_logits in zip(memories_batch, neighbor_label_logits_batch):
            metrics = self.compute_neighbor_label_metrics(
                neighbor_label_logits, memory.label, normalize_logits=self.config.normalize_logits
            )
            memory_metrics.append((memory.memory_id, metrics))

            # update aggregate metrics
            self._label_memory_counts[memory.label] += 1
            for label, logit in enumerate(neighbor_label_logits):
                self._label_lookup_scores[label].append(float(logit))
            self._sum_neighbor_prediction_accuracy += metrics.neighbor_predicted_label_matches_current_label
            self._sum_neighbor_label_confidence += metrics.neighbor_predicted_label_confidence
            self._sum_neighbor_label_entropy += metrics.normalized_neighbor_label_entropy
            self._sum_neighbor_predicted_label_ambiguity += metrics.neighbor_predicted_label_ambiguity

        return memory_metrics

    def after_all(self) -> MemorysetLabelMetrics:
        return MemorysetLabelMetrics(
            label_metrics=[
                MemorysetLabelMetrics.LabelClassMetrics(
                    label=label,
                    label_name=self.memoryset.get_label_name(label),
                    average_lookup_score=float(np.mean(self._label_lookup_scores[label])),
                    memory_count=self._label_memory_counts[label],
                )
                for label in range(self.memoryset_num_classes)
            ],
            neighbor_prediction_accuracy=self._sum_neighbor_prediction_accuracy / self.memoryset_num_rows,
            mean_neighbor_label_confidence=self._sum_neighbor_label_confidence / self.memoryset_num_rows,
            mean_neighbor_label_entropy=self._sum_neighbor_label_entropy / self.memoryset_num_rows,
            mean_neighbor_predicted_label_ambiguity=self._sum_neighbor_predicted_label_ambiguity
            / self.memoryset_num_rows,
        )
