from uuid import uuid4

import numpy as np

from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset
from .analysis import run_analyses
from .analysis_neighbor import MemorysetNeighborAnalysis, MemorysetNeighborMetrics


def test_neighbor_analysis():
    # Given a memoryset with distinct text clusters and an outlier
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["technology", "sports", "other"],
    )
    memoryset.insert(
        [
            # Technology cluster (should be close to each other)
            {"value": "AI technology is advancing rapidly", "label": 0},
            {"value": "Machine learning models are improving", "label": 0},
            {"value": "Neural networks can solve complex problems", "label": 0},
            # Sports cluster (should be close to each other)
            {"value": "Basketball championships are exciting events", "label": 1},
            {"value": "Soccer is the most popular sport globally", "label": 1},
            {"value": "Tennis requires precision and endurance", "label": 1},
            # An outlier (should be far from others)
            {"value": "Heute ist ein schöner Tag", "label": 2},
        ]
    )

    # When we run a neighbor analysis on the memoryset
    result = run_analyses(
        memoryset,
        MemorysetNeighborAnalysis(neighbor_counts=[1, 2, 3], quantiles=[0.1, 0.9]),
        lookup_count=5,
        show_progress_bar=False,
    )["neighbor"]

    # Then the analysis returns valid metrics for the entire memoryset
    assert isinstance(result, MemorysetNeighborMetrics)

    # And the lookup score metrics contain data for the expected lookup counts
    for count in [1, 2, 3]:
        assert count in result.lookup_score_metrics

    # And each lookup score metric has the correct structure and data types
    for count, metrics in result.lookup_score_metrics.items():
        assert isinstance(metrics.median, float)
        assert isinstance(metrics.std, float)
        assert isinstance(metrics.quantiles, list)
        assert isinstance(metrics.quantile_values, list)
        assert len(metrics.quantiles) == len(metrics.quantile_values) == 2
        assert all(isinstance(q, float) for q in metrics.quantiles)
        assert all(isinstance(v, float) for v in metrics.quantile_values)

    # And each memory has a valid anomaly score added to its metrics
    for memory in memoryset:
        assert "anomaly_score" in memory.metrics
        assert isinstance(memory.metrics["anomaly_score"], float)
        assert 0 <= memory.metrics["anomaly_score"] <= 1

    # And the outlier has a higher anomaly score than the average of memories in clusters
    average_anomaly_score = sum(memory.metrics.get("anomaly_score", float("nan")) for memory in memoryset[:5]) / 5
    assert average_anomaly_score < memoryset[6].metrics.get("anomaly_score", float("nan"))
