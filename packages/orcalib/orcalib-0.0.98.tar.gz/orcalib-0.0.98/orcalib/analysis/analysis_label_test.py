from math import log2
from uuid import uuid4

import numpy as np
from datasets import Dataset

from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset
from .analysis import run_analyses
from .analysis_label import MemorysetLabelAnalysis, MemorysetLabelMetrics


def test_compute_neighbor_label_logits():
    # Given a batch of memory labels and lookup scores
    num_classes = 3
    batch_size = 2
    memory_count = 5
    memories_labels = np.array([[1, 0, 2, 0, 2], [1, 1, 1, 2, 2]], dtype=np.int64)
    assert memories_labels.shape == (batch_size, memory_count)
    memories_lookup_scores = np.array([[0.9, 0.1, 0.3, 0.3, 0.5], [0.1, 0.2, 0.3, 0.6, 0.01]], dtype=np.float32)
    assert memories_lookup_scores.shape == (batch_size, memory_count)
    # When the compute the logits
    logits_batch = MemorysetLabelAnalysis.compute_neighbor_label_logits(
        memories_labels=memories_labels,
        memories_lookup_scores=memories_lookup_scores,
        num_classes=num_classes,
    )
    # Then we get a list with logits for each entry in the batch
    assert len(logits_batch) == batch_size
    assert all(isinstance(logits, np.ndarray) for logits in logits_batch)
    # And the logits have the correct shape and dtype
    assert all(logits.shape == (num_classes,) for logits in logits_batch)
    assert all(logits.dtype == np.float32 for logits in logits_batch)
    # And the logits predict the correct labels
    assert [int(np.argmax(logits)) for logits in logits_batch] == [1, 2]
    # And the logits reflect the confidence in the predictions
    assert np.allclose(logits_batch[0], np.array([0.4 / 5, 0.9 / 5, 0.8 / 5]))
    assert np.allclose(logits_batch[1], np.array([0, 0.6 / 5, 0.61 / 5]))


def test_compute_label_metrics():
    # Given some neighbor label logits
    label_logits = np.array([0.0, 0.25, 0.5, 0.1], dtype=np.float32)
    assert all(label_logits >= 0) and label_logits.sum() <= 1
    # And a current label
    current_label = 1
    # When we compute the metrics
    result = MemorysetLabelAnalysis.compute_neighbor_label_metrics(label_logits, current_label)
    # Then the predicted label is the one with the highest logit
    assert result.neighbor_predicted_label == 2
    # And the predicted label ambiguity is the difference between the highest and second highest logit
    assert result.neighbor_predicted_label_ambiguity == 0.5 - 0.25
    # And the predicted label confidence is the highest logit
    assert result.neighbor_predicted_label_confidence == 0.5
    # And the current label confidence is the logit for the current label
    assert result.current_label_neighbor_confidence == 0.25
    # And the label entropy is the sum of the logits times the log of the logits
    assert result.normalized_neighbor_label_entropy is not None
    assert result.neighbor_predicted_label_matches_current_label == (result.neighbor_predicted_label == current_label)
    # Handle both float and array cases for label_logits
    if isinstance(label_logits, list):
        label_logits_list = label_logits
    else:
        label_logits_list = [label_logits]

    # Convert to numpy array and handle array operations properly
    label_logits_array = np.array(label_logits_list)
    positive_mask = label_logits_array > 0
    positive_logits = label_logits_array[positive_mask]

    # Handle edge cases and normalize properly
    if len(positive_logits) == 0:
        expected_entropy = 0.0
    else:
        # Normalize by the maximum possible entropy for the number of classes in label_logits
        num_classes = len(label_logits)
        max_entropy = log2(num_classes) if num_classes > 0 else 1.0
        if max_entropy == 0:
            expected_entropy = 0.0
        else:
            expected_entropy = -np.sum(positive_logits * np.log2(positive_logits)) / max_entropy
    assert 0 <= expected_entropy <= 1
    assert 0 <= result.normalized_neighbor_label_entropy <= 1
    assert result.normalized_neighbor_label_entropy - expected_entropy < 1e-6


def test_analyze_neighbor_labels():
    # Given a memoryset with 5 memories
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["climate", "economy", "sports"],
    )
    memoryset.insert(
        Dataset.from_list(
            [
                {"value": "about climate change", "label": 0},
                {"value": "about the economy", "label": 1},
                {"value": "about sports", "label": 2},
                {"value": "about sports", "label": 2},
                {"value": "about sports", "label": 2},
            ]
        )
    )
    # When we analyze the neighbor labels
    result = run_analyses(
        memoryset,
        MemorysetLabelAnalysis(),
        lookup_count=3,
        show_progress_bar=False,
        batch_size=2,
    )["label"]
    # Then aggregate label class metrics are returned
    assert isinstance(result, MemorysetLabelMetrics)
    assert len(result.label_metrics) == 3
    assert result.label_metrics[0].memory_count == 1
    assert result.label_metrics[1].memory_count == 1
    assert result.label_metrics[2].memory_count == 3
    assert all(0 <= metrics.average_lookup_score <= 1 for metrics in result.label_metrics)
    # And metrics are saved to the memories in the memoryset
    for memory in memoryset:
        assert memory.metrics.get("neighbor_label_logits", None) is not None
        assert memory.metrics.get("neighbor_predicted_label", None) is not None
        assert memory.metrics.get("neighbor_predicted_label_ambiguity", None) is not None
        assert memory.metrics.get("neighbor_predicted_label_confidence", None) is not None
        assert memory.metrics.get("current_label_neighbor_confidence", None) is not None
        assert memory.metrics.get("normalized_neighbor_label_entropy", None) is not None
        assert memory.metrics.get("neighbor_predicted_label_matches_current_label", None) is not None
