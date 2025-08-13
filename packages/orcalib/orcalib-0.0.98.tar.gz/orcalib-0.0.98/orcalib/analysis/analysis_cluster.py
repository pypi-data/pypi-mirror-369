import logging
from time import perf_counter
from typing import Literal

import numpy as np
from igraph import Graph
from leidenalg import (
    CPMVertexPartition,
    ModularityVertexPartition,
    RBConfigurationVertexPartition,
    find_partition,
)
from leidenalg.VertexPartition import MutableVertexPartition
from numpy.typing import NDArray
from pydantic import BaseModel
from scipy.sparse import csr_matrix
from sklearn.cluster import HDBSCAN

from ..memoryset import LabeledMemory, LabeledMemoryLookup
from ..utils.pydantic import UUID7
from .analysis import MemorysetAnalysis


class MemoryClusterMetrics(BaseModel):
    cluster: int | None


class MemorysetClusterMetrics(BaseModel):
    class ClusterMetrics(BaseModel):
        cluster: int
        """The cluster number"""

        memory_count: int
        """The number of memories in the cluster"""

    cluster_metrics: list[ClusterMetrics]
    """The metrics for each cluster"""

    num_outliers: int
    """The number of outliers"""

    num_clusters: int
    """The number of clusters"""


class MemorysetClusterAnalysisConfig(BaseModel):
    min_cluster_size: int | None = None
    """Minimum number of samples in a cluster"""

    max_cluster_size: int | None = None
    """Maximum number of samples in a cluster"""

    clustering_method: Literal["density", "graph"] = "graph"
    """
    Method used to cluster the data

    **graph**: Leiden algorithm clustering (robust solution for most cases)
    **density**: HDBSCAN clustering (only works for highly separable data)
    """

    min_cluster_distance: float = 0.0
    """Minimum distance between clusters for density clustering"""

    partitioning_method: Literal["ng", "rb", "cpm"] = "ng"
    """
    The graph partitioning method to use for the clustering.

    **ng**: Standard Newman‐Girvan modularity (does not accept resolution parameter)
    **rb**: Reichardt & Bornholdt model with configurable resolution
    **cpm**: Constant Potts model with configurable resolution
    """

    resolution: float | None = None
    """Resolution parameter for graph clustering, the higher the value, the more clusters"""

    num_iterations: int = 2
    """Number of iterations for graph clustering"""

    random_state: int | None = 42
    """Random state for clustering"""


class MemorysetClusterAnalysis(
    MemorysetAnalysis[MemorysetClusterAnalysisConfig, MemoryClusterMetrics, MemorysetClusterMetrics]
):
    name = "cluster"

    def __init__(self, config: MemorysetClusterAnalysisConfig | None = None, **kwargs):
        self.config = config or MemorysetClusterAnalysisConfig(**kwargs)

        self._memory_ids: dict[UUID7, int] = {}
        self._similarities: dict[tuple[UUID7, UUID7], float] = {}

    def on_batch(self, memories_batch: list[LabeledMemory], neighbors_batch: list[list[LabeledMemoryLookup]]) -> None:
        for i, memory in enumerate(memories_batch):
            self._memory_ids[memory.memory_id] = len(self._memory_ids)

            for neighbor in neighbors_batch[i]:
                self._similarities[(memory.memory_id, neighbor.memory_id)] = neighbor.lookup_score

    def density_clustering(self) -> tuple[MemorysetClusterMetrics, list[tuple[UUID7, MemoryClusterMetrics]]]:
        start = perf_counter()
        values, rows, cols = [], [], []
        for (mem1_id, mem2_id), similarity in self._similarities.items():
            values.append(1.0 - similarity)
            rows.append(self._memory_ids[mem1_id])
            cols.append(self._memory_ids[mem2_id])
        self.distance_matrix = csr_matrix(
            (values, (rows, cols)),
            shape=(self.memoryset_num_rows, self.memoryset_num_rows),
            dtype=np.float32,
        )
        # the distance matrix has to be perfectly symmetric
        self.distance_matrix = self.distance_matrix.maximum(self.distance_matrix.T)
        self.distance_matrix.setdiag(0)
        logging.info(f"Constructed distance matrix in {perf_counter() - start:.2f} seconds")

        # default min cluster size to num_rows / (10 * num_classes)
        min_cluster_size = self.config.min_cluster_size or (
            self.memoryset_num_rows // (10 * self.memoryset_num_classes)
        )
        try:
            cluster_labels: NDArray[np.int32] = HDBSCAN(
                min_cluster_size=min_cluster_size,
                max_cluster_size=self.config.max_cluster_size,
                cluster_selection_epsilon=self.config.min_cluster_distance,
                allow_single_cluster=True,
                metric="precomputed",
                min_samples=self.lookup_count + 1 if self.lookup_count <= min_cluster_size else min_cluster_size,
                copy=True,
            ).fit_predict(self.distance_matrix)
        except ValueError as e:
            # see https://github.com/scikit-learn-contrib/hdbscan/issues/135#issuecomment-368922696
            if "Ensure that the sparse distance matrix has only one connected component" in str(e):
                cluster_labels = np.full(self.memoryset_num_rows, -1, dtype=np.int32)
            else:
                raise e
        logging.info(f"Performed density clustering in {perf_counter() - start:.2f} seconds")

        return MemorysetClusterMetrics(
            cluster_metrics=[
                MemorysetClusterMetrics.ClusterMetrics(
                    cluster=int(cluster), memory_count=np.sum(cluster_labels == cluster)
                )
                for cluster in np.unique(cluster_labels)
                if cluster >= 0
            ],
            num_outliers=np.sum(cluster_labels == -1),
            num_clusters=int(np.max(cluster_labels) + 1),
        ), [
            (memory_id, MemoryClusterMetrics(cluster=int(cluster)))
            for memory_id, cluster in zip(self._memory_ids, cluster_labels)
        ]

    def graph_clustering(self) -> tuple[MemorysetClusterMetrics, list[tuple[UUID7, MemoryClusterMetrics]]]:
        start = perf_counter()
        self.graph = Graph(
            n=self.memoryset_num_rows,
            edges=[
                (self._memory_ids[mem1_id], self._memory_ids[mem2_id]) for mem1_id, mem2_id in self._similarities.keys()
            ],
            edge_attrs={"weight": list(self._similarities.values())},
            directed=False,
        )
        logging.info(f"Constructed nearest neighbor graph in {perf_counter() - start:.2f} seconds")
        partition: MutableVertexPartition = find_partition(
            self.graph,
            partition_type={
                "ng": ModularityVertexPartition,
                "rb": RBConfigurationVertexPartition,
                "cpm": CPMVertexPartition,
            }[self.config.partitioning_method],
            weights="weight",
            n_iterations=self.config.num_iterations,
            seed=self.config.random_state,
            max_comm_size=self.config.max_cluster_size or 0,
            **{"resolution_parameter": self.config.resolution} if self.config.resolution is not None else {},
        )
        logging.info(f"Performed graph clustering in {perf_counter() - start:.2f} seconds")
        too_small_clusters = (
            {c for c, n in enumerate(partition.sizes()) if n < self.config.min_cluster_size}
            if self.config.min_cluster_size
            else set()
        )
        cluster_labels = partition.membership

        # remove clusters that are too small and mark their members as outliers
        num_outliers = 0
        if len(too_small_clusters) > 0:
            for i, c in enumerate(cluster_labels):
                if c in too_small_clusters:
                    cluster_labels[i] = -1
                    num_outliers += 1
            logging.info(
                f"Marked {num_outliers} rows as outliers from {len(too_small_clusters)} clusters that were too small"
            )

        return MemorysetClusterMetrics(
            num_outliers=num_outliers,
            num_clusters=len(partition) - len(too_small_clusters),
            cluster_metrics=[
                MemorysetClusterMetrics.ClusterMetrics(cluster=c, memory_count=n)
                for c, n in enumerate(partition.sizes())
                if c not in too_small_clusters
            ],
        ), [
            (memory_id, MemoryClusterMetrics(cluster=cluster))
            for memory_id, cluster in zip(self._memory_ids, cluster_labels)
        ]

    def after_all(self) -> tuple[MemorysetClusterMetrics, list[tuple[UUID7, MemoryClusterMetrics]]]:
        match self.config.clustering_method:
            case "density":
                return self.density_clustering()
            case "graph":
                return self.graph_clustering()
            case _:
                raise ValueError(f"Invalid clustering method: {self.config.clustering_method}")
