from collections import defaultdict
from itertools import combinations
from uuid import uuid4

import numpy as np

from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset
from .analysis import run_analyses
from .analysis_projection import MemorysetProjectionAnalysis, MemorysetProjectionMetrics


def test_projection_analysis():
    # Given a memoryset with text entries
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["technology", "sports", "politics", "entertainment"],
    )
    memoryset.insert(
        [
            # Technology cluster
            {"value": "AI technology is advancing rapidly", "label": 0},
            {"value": "Machine learning models are improving", "label": 0},
            {"value": "Neural networks can solve complex problems", "label": 0},
            # Sports cluster
            {"value": "Basketball championships are exciting events", "label": 1},
            {"value": "Soccer is the most popular sport globally", "label": 1},
            {"value": "Tennis requires precision and endurance", "label": 1},
            # Politics cluster
            {"value": "Election campaigns are important democratic processes", "label": 2},
            {"value": "Political debates shape public opinion", "label": 2},
            # Entertainment cluster
            {"value": "Movies can transport us to different worlds", "label": 3},
            {"value": "Music festivals bring people together", "label": 3},
        ]
    )
    # When we run a projection analysis
    result = run_analyses(
        memoryset,
        MemorysetProjectionAnalysis(min_dist=0.2),
        lookup_count=5,
        show_progress_bar=False,
    )["projection"]
    assert isinstance(result, MemorysetProjectionMetrics)
    # Then 2d projection coordinates are saved to the metrics of the memories
    projections_by_label = defaultdict(list)
    for memory in memoryset:
        assert "embedding_2d" in memory.metrics
        assert isinstance(memory.metrics["embedding_2d"], tuple)
        assert len(memory.metrics["embedding_2d"]) == 2
        assert all(isinstance(coord, float) for coord in memory.metrics["embedding_2d"])
        projections_by_label[memory.label].append(memory.metrics["embedding_2d"])
    # And the coordinates are roughly grouped by label
    centroids = [np.mean(vectors, axis=0) for vectors in projections_by_label.values()]
    average_distance_to_centroid = [
        np.mean([np.linalg.norm(vector - centroid) for vector in vectors])
        for vectors, centroid in zip(projections_by_label.values(), centroids)
    ]
    average_distance_between_centroids = np.mean(
        [np.linalg.norm(centroids[0] - centroids[1]) for centroids in combinations(centroids, 2)]
    )
    assert all(d < average_distance_between_centroids for d in average_distance_to_centroid)
