import logging
from itertools import batched
from uuid import UUID

import numpy as np
from numpy.typing import NDArray
from PIL import Image as pil
from pydantic import BaseModel
from tqdm.auto import tqdm
from typing_extensions import deprecated

from ..utils.progress import OnProgressCallback, safely_call_on_progress
from ..utils.pydantic import Vector
from .memory_types import LabeledMemoryUpdate, MemoryMetrics
from .memoryset import FilterItem, LabeledMemoryset


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


def compute_neighbor_label_metrics(
    neighbor_label_logits: Vector, current_label: int, normalize_logits: bool = False
) -> MemoryMetrics:
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

    return MemoryMetrics(
        neighbor_label_logits=neighbor_label_logits,
        neighbor_predicted_label=predicted_label,
        neighbor_predicted_label_ambiguity=float(sorted_logits[-1] - sorted_logits[-2]),
        neighbor_predicted_label_confidence=float(sorted_logits[-1]),
        current_label_neighbor_confidence=float(neighbor_label_logits[current_label]),
        normalized_neighbor_label_entropy=float(normalized_entropy),
        neighbor_predicted_label_matches_current_label=predicted_label == current_label,
    )


class FindDuplicatesAnalysisResult(BaseModel):
    num_duplicates: int
    """The number of duplicate memories in the memoryset"""


class AnalyzeNeighborLabelsResult(BaseModel):
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


@deprecated("use analyzer.MemorysetAnalyzer instead")
class LabeledMemorysetAnalyzer:
    def __init__(
        self,
        memoryset: LabeledMemoryset,
        neighbor_count: int = 10,
        task_id: UUID | None = None,
        num_classes: int | None = None,
    ):
        """
        Initialize the labeled memoryset analyzer.

        Args:
            memoryset: the memoryset to analyze
            neighbor_count: number of neighbors to lookup for analysis
            task_id: optional ID of the task that this is called from
        """
        self.memoryset = memoryset
        self.neighbor_count = neighbor_count
        self.task_id = task_id
        self.num_classes = num_classes or self.memoryset.num_classes

    def clear_metrics(self) -> None:
        """Clear the metrics of all memories in the memoryset."""

        self.memoryset.update(
            [LabeledMemoryUpdate(metrics=MemoryMetrics(), memory_id=memory.memory_id) for memory in self.memoryset]
        )

    def save_memory_metrics(
        self,
        metric_updates: dict[UUID, MemoryMetrics],
    ):
        """Save the given metric values to the memoryset"""
        logging.debug(f"Saving metrics for {len(metric_updates)} memories")
        self.memoryset.update(
            [LabeledMemoryUpdate(memory_id=memory_id, metrics=metrics) for memory_id, metrics in metric_updates.items()]
        )

    def find_duplicates(
        self,
        remove_duplicates: bool = False,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
    ) -> FindDuplicatesAnalysisResult:
        """
        Find duplicate memories in the memoryset.

        Note:
            This method is not supported for image memories.

        Returns:
            Number of duplicate memories found, individual duplicates will be marked in the memoryset
        """
        num_duplicates = 0
        memory_count = len(self.memoryset)

        duplicate_values = {}

        call_every = max(1, min(100, memory_count // 10))

        for i, memory in tqdm(enumerate(self.memoryset), disable=not show_progress_bar, total=memory_count):
            if i % call_every == 0:
                safely_call_on_progress(on_progress, i, memory_count)

            if memory.value in duplicate_values:
                # If we have already found duplicates for this value, we can skip this memory
                continue

            if isinstance(memory.value, pil.Image) or isinstance(memory.value, np.ndarray):
                raise ValueError("Cannot find duplicates of images or timeseries")

            same_value_memories = self.memoryset.query(
                filters=[FilterItem(field=("value",), op="==", value=memory.value)]
            )

            if len(same_value_memories) > 1:
                duplicate_values[memory.value] = same_value_memories

        metrics_updates = {}

        for _, memories in duplicate_values.items():
            # sort memories by ID to ensure consistent results
            memories.sort(key=lambda x: x.memory_id)

            for memory in memories[:-1]:
                num_duplicates += 1
                metrics_updates[memory.memory_id] = MemoryMetrics(
                    is_duplicate=True,
                    duplicate_memory_ids=[m.memory_id for m in memories if m.memory_id != memory.memory_id],
                )

        safely_call_on_progress(on_progress, memory_count, memory_count)

        if remove_duplicates:
            logging.info(f"Removing {num_duplicates} duplicates from memoryset")
            self.memoryset.delete(list(metrics_updates.keys()))
        else:
            self.save_memory_metrics(metrics_updates)

        return FindDuplicatesAnalysisResult(num_duplicates=num_duplicates)

    def analyze_neighbor_labels(
        self,
        batch_size: int = 32,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
        normalize_logits: bool = False,
    ) -> AnalyzeNeighborLabelsResult:
        """
        Analyze neighbor labels for each memory in the memoryset.

        Args:
            lookup_count: number of neighbors to lookup for each memory
            batch_size: number of memories to process in each batch
            show_progress_bar: whether to show a progress bar
            on_progress: callback function to call with the current and total number of batches
            normalize_logits: whether to normalize logits, this makes metrics less comparable between memories
        Returns:
            Aggregated results of the analysis, individual memory metrics are saved to the memoryset
        """
        label_lookup_scores: dict[int, list[float]] = {label: [] for label in range(self.num_classes)}
        label_memory_counts: dict[int, int] = {label: 0 for label in range(self.num_classes)}

        num_memories = len(self.memoryset)
        num_batches = len(self.memoryset) // batch_size

        neighbor_prediction_accuracy = 0.0
        mean_neighbor_label_confidence = 0.0
        mean_neighbor_label_entropy = 0.0
        mean_neighbor_predicted_label_ambiguity = 0.0

        offset = 0
        for memory_batch in tqdm(batched(self.memoryset, batch_size), total=num_batches, disable=not show_progress_bar):
            safely_call_on_progress(on_progress, offset, num_memories)

            memory_lookups_batch = self.memoryset.lookup(
                [m.value for m in memory_batch],
                count=self.neighbor_count,
                exclude_exact_match=True,
                return_type="columns",
            )

            neighbor_label_logits_batch = compute_neighbor_label_logits(
                memories_labels=memory_lookups_batch["memories_labels"],
                memories_lookup_scores=memory_lookups_batch["memories_lookup_scores"],
                num_classes=self.num_classes,
            )

            neighbor_metrics = {}

            for memory, neighbor_label_logits in zip(memory_batch, neighbor_label_logits_batch):
                # update label class aggregate metrics
                label_memory_counts[memory.label] += 1
                for label, logit in enumerate(neighbor_label_logits):
                    label_lookup_scores[label].append(float(logit))
                # compute and save neighbor metrics
                metrics = compute_neighbor_label_metrics(
                    neighbor_label_logits, memory.label, normalize_logits=normalize_logits
                )
                neighbor_metrics[memory.memory_id] = metrics

                neighbor_prediction_accuracy += (
                    1.0 if metrics.get("neighbor_predicted_label_matches_current_label", False) else 0.0
                )
                mean_neighbor_label_confidence += metrics.get("neighbor_predicted_label_confidence", 0.0)
                mean_neighbor_label_entropy += metrics.get("normalized_neighbor_label_entropy", 0.0)
                mean_neighbor_predicted_label_ambiguity += metrics.get("neighbor_predicted_label_ambiguity", 0.0)

            self.save_memory_metrics(neighbor_metrics)

            offset += batch_size

        neighbor_prediction_accuracy /= num_memories
        mean_neighbor_label_confidence /= num_memories
        mean_neighbor_label_entropy /= num_memories
        mean_neighbor_predicted_label_ambiguity /= num_memories

        safely_call_on_progress(on_progress, num_memories, num_memories)
        return AnalyzeNeighborLabelsResult(
            label_metrics=[
                AnalyzeNeighborLabelsResult.LabelClassMetrics(
                    label=label,
                    label_name=self.memoryset.get_label_name(label),
                    average_lookup_score=float(np.mean(label_lookup_scores[label])),
                    memory_count=label_memory_counts[label],
                )
                for label in range(self.num_classes)
            ],
            neighbor_prediction_accuracy=neighbor_prediction_accuracy,
            mean_neighbor_label_confidence=mean_neighbor_label_confidence,
            mean_neighbor_label_entropy=mean_neighbor_label_entropy,
            mean_neighbor_predicted_label_ambiguity=mean_neighbor_predicted_label_ambiguity,
        )
