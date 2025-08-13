from uuid import uuid4

import pytest

from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset
from .analysis import run_analyses
from .analysis_cluster import MemorysetClusterAnalysis, MemorysetClusterMetrics


@pytest.mark.parametrize("clustering_method", ["density", "graph"])
def test_cluster_analysis(clustering_method):
    # Given a memoryset with distinct clusters of data
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["technology", "sports", "politics", "entertainment", "science"],
    )
    memoryset.insert(
        [
            # Technology cluster
            {"value": "AI technology is advancing rapidly in modern smartphones", "label": 0},
            {"value": "AI technology is transforming how we use smartphones today", "label": 0},
            {"value": "AI technology continues to evolve in smartphone applications", "label": 0},
            {"value": "AI technology is the key feature in new smartphone models", "label": 0},
            # Sports cluster
            {"value": "Basketball championships are exciting competitive events", "label": 1},
            {"value": "Basketball tournaments draw large crowds of enthusiastic fans", "label": 1},
            {"value": "Basketball players train intensively for championship games", "label": 1},
            {"value": "Basketball teams compete fiercely in championship matches", "label": 1},
            # Politics cluster
            {"value": "Election campaigns are heating up across the country", "label": 2},
            {"value": "Election season brings intense political debates nationwide", "label": 2},
            {"value": "Election polling shows shifting voter preferences this month", "label": 2},
            {"value": "Election candidates are increasing their campaign activities", "label": 2},
            # Some outliers that don't fit neatly into clusters
            {"value": "A unique archaeological discovery was made in the remote desert", "label": 4},
            {"value": "The recipe calls for unusual ingredients and preparation methods", "label": 3},
        ]
    )
    # When we run a cluster analysis
    result = run_analyses(
        memoryset,
        MemorysetClusterAnalysis(
            min_cluster_size=3,
            max_cluster_size=5,
            clustering_method=clustering_method,
        ),
        lookup_count=5,
        show_progress_bar=False,
    )["cluster"]
    # Then a result is returned
    assert isinstance(result, MemorysetClusterMetrics)
    # And the result contains 3 clusters and 2 outliers
    assert len(result.cluster_metrics) == 3
    assert result.num_outliers == 2
    # And each cluster should have the expected number of memories
    cluster_sizes = [metric.memory_count for metric in result.cluster_metrics]
    assert cluster_sizes == [4, 4, 4]
    # And each memory should be assigned to the expected cluster
    clusters: dict[str, int | None] = {"AI technology": None, "Basketball": None, "Election": None}
    for memory in memoryset:
        assert isinstance(memory.value, str)
        assert "cluster" in memory.metrics
        prefix = next((prefix for prefix in clusters if memory.value.startswith(prefix)), None)
        if prefix is not None:
            if clusters[prefix] is None:
                clusters[prefix] = memory.metrics["cluster"]
            else:
                assert (
                    memory.metrics["cluster"] == clusters[prefix]
                ), f"Memory '{memory.value}' not in expected cluster '{clusters[prefix]}'"
        else:
            assert memory.metrics["cluster"] == -1, f"Memory '{memory.value}' is not an outlier"
