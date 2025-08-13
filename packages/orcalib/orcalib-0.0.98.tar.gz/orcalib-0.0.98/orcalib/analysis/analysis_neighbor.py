import logging

import numpy as np
from pydantic import BaseModel

from ..memoryset import LabeledMemory, LabeledMemoryLookup
from ..utils import UUID7
from .analysis import MemorysetAnalysis


class MemoryNeighborMetrics(BaseModel):
    anomaly_score: float
    """The distance to the closest neighbor"""


class MemorysetNeighborMetrics(BaseModel):
    class LookupScoreMetrics(BaseModel):
        median: float
        std: float
        quantiles: list[float]
        quantile_values: list[float]

    lookup_score_metrics: dict[int, LookupScoreMetrics]  # neighbor_count -> metrics
    """The lookup score metrics for the top k neighbors"""


class MemorysetNeighborAnalysisConfig(BaseModel):
    neighbor_counts: list[int] = [1, 3, 5, 9, 15]
    """Values of top k neighbors for which to compute lookup score distribution metrics"""

    quantiles: list[float] = [0.1, 0.25, 0.5, 0.75, 0.9]
    """The quantiles to compute for the lookup score metrics"""


class MemorysetNeighborAnalysis(
    MemorysetAnalysis[MemorysetNeighborAnalysisConfig, MemoryNeighborMetrics, MemorysetNeighborMetrics]
):
    """
    Analyze neighbors of each memory to detect anomalies and aggregate distribution metrics (independent of labels)
    """

    name = "neighbor"

    def __init__(self, config: MemorysetNeighborAnalysisConfig | None = None, **kwargs):
        self.config = config or MemorysetNeighborAnalysisConfig(**kwargs)

        self.lookup_scores: list[list[float]] = []

    def on_batch(
        self, memories_batch: list[LabeledMemory], neighbors_batch: list[list[LabeledMemoryLookup]]
    ) -> list[tuple[UUID7, MemoryNeighborMetrics]]:
        memory_metrics: list[tuple[UUID7, MemoryNeighborMetrics]] = []
        for memory, neighbors in zip(memories_batch, neighbors_batch):
            self.lookup_scores.append([n.lookup_score for n in neighbors])
            anomaly_score = max(0, min(1, 1 - neighbors[0].lookup_score))
            memory_metrics.append((memory.memory_id, MemoryNeighborMetrics(anomaly_score=anomaly_score)))
        return memory_metrics

    def after_all(self) -> MemorysetNeighborMetrics:
        similarities = np.array(self.lookup_scores)
        lookup_score_metrics: dict[int, MemorysetNeighborMetrics.LookupScoreMetrics] = {}
        for k in self.config.neighbor_counts:
            if similarities.shape[1] < k:
                logging.warning(f"Not enough neighbors to compute lookup score metrics for count={k}")
                continue
            top_k_similarities = similarities[:, :k]
            lookup_score_metrics[k] = MemorysetNeighborMetrics.LookupScoreMetrics(
                median=float(np.median(top_k_similarities)),
                std=float(np.std(top_k_similarities)),
                quantiles=self.config.quantiles,
                quantile_values=[float(x) for x in np.quantile(top_k_similarities, self.config.quantiles)],
            )
        return MemorysetNeighborMetrics(lookup_score_metrics=lookup_score_metrics)
