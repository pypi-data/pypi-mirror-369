import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, cast

import igraph as ig
import leidenalg
import numpy as np
import pandas as pd
import sklearn.cluster as sklearn_cluster
from pydantic import BaseModel
from sklearn.cluster import HDBSCAN
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.neighbors import kneighbors_graph


class ClusterDetails(BaseModel):
    """Details about a cluster including its exemplars and hierarchy info."""

    cluster_id: int
    exemplars: list[str]
    name: str
    parent_cluster_id: int | None = None
    is_noise_cluster: bool = False
    size: int = 0


class ClusteringMethod(ABC):
    """Abstract base class for clustering methods."""

    def __init__(self, name: str, has_noise: bool) -> None:
        """
        Initialize the clustering method base class.
        Args:
            name: Name of the clustering method.
            has_noise: Whether the method has an explicit noise concept.
        """
        self.name = name
        self.has_noise = has_noise

    @property
    @abstractmethod
    def minimum_required_points(self) -> int:
        """
        Minimum number of points required for this clustering method to operate.
        """
        pass

    @abstractmethod
    def cluster(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Cluster the embeddings and return cluster labels.
        Args:
            embeddings: Array of embeddings to cluster
        Returns:
            Array of cluster labels
        """
        pass


class HDBSCANClustering(ClusteringMethod):
    """HDBSCAN density-based clustering."""

    def __init__(self, min_cluster_size: int = 40, min_samples: int = 8) -> None:
        """
        Initialize HDBSCAN clustering method.
        Args:
            min_cluster_size: Minimum size of clusters.
            min_samples: Minimum samples for a core point.
        """
        super().__init__(name="HDBSCAN", has_noise=True)
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples

    @property
    def minimum_required_points(self) -> int:
        """
        Returns the minimum number of points for cluster() to operate.
        For HDBSCAN, this is the maximum of min_cluster_size and min_samples.
        """
        return max(self.min_cluster_size, self.min_samples)

    def cluster(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Cluster the embeddings using HDBSCAN.
        Args:
            embeddings: Array of embeddings to cluster.
        Returns:
            Array of cluster labels.
        """
        clusterer = HDBSCAN(min_cluster_size=self.min_cluster_size, min_samples=self.min_samples)
        return clusterer.fit_predict(embeddings)


class LeidenClustering(ClusteringMethod):
    """Leiden graph-based clustering."""

    def __init__(self, n_neighbors: int = 15, resolution: float = 1.0, seed: int = 42) -> None:
        """
        Initialize Leiden clustering method.
        Args:
            n_neighbors: Number of neighbors for k-NN graph.
            resolution: Resolution parameter for Leiden algorithm.
            seed: Random seed.
        """
        super().__init__(name="LEIDEN", has_noise=False)
        self.n_neighbors = n_neighbors
        self.resolution = resolution
        self.seed = seed

    @property
    def minimum_required_points(self) -> int:
        """
        Returns the minimum number of points required for Leiden clustering.
        This is n_neighbors + 1 to ensure we can form a k-NN graph.
        """
        return self.n_neighbors + 1

    def cluster(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Cluster the embeddings using Leiden algorithm on a k-NN graph.
        Args:
            embeddings: Array of embeddings to cluster.
        Returns:
            Array of cluster labels.
        """
        # Build k-NN graph
        knn_graph = kneighbors_graph(embeddings, n_neighbors=self.n_neighbors, mode="connectivity", include_self=False)
        sources, targets = knn_graph.nonzero()
        edges = list(zip(sources, targets))
        g = ig.Graph(n=len(embeddings), edges=edges)
        # Run Leiden algorithm
        partition = leidenalg.find_partition(
            g,
            leidenalg.RBConfigurationVertexPartition,
            resolution_parameter=self.resolution,
            seed=self.seed,
            n_iterations=6,
        )
        return np.array(partition.membership)


class AgglomerativeClustering(ClusteringMethod):
    """Agglomerative hierarchical clustering."""

    def __init__(
        self, min_cluster_size: int = 40, linkage: Literal["ward", "complete", "average", "single"] = "ward"
    ) -> None:
        """
        Initialize Agglomerative clustering method.
        Args:
            min_cluster_size: Minimum size of clusters.
            linkage: Linkage criterion to use.
        """
        super().__init__(name="AGGLOMERATIVE", has_noise=False)
        self.min_cluster_size = min_cluster_size
        self.linkage: Literal["ward", "complete", "average", "single"] = linkage

    @property
    def minimum_required_points(self) -> int:
        """
        Returns the minimum number of points required for AgglomerativeClustering to operate.
        This is equal to min_cluster_size.
        """
        return self.min_cluster_size

    def cluster(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Cluster the embeddings using Agglomerative clustering.
        Args:
            embeddings: Array of embeddings to cluster.
        Returns:
            Array of cluster labels.
        """
        # Estimate number of clusters based on min_cluster_size
        max_clusters = max(2, len(embeddings) // self.min_cluster_size)
        clusterer = sklearn_cluster.AgglomerativeClustering(n_clusters=max_clusters, linkage=self.linkage)
        return clusterer.fit_predict(embeddings)


def compute_cluster_center(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute the centroid of a cluster of embeddings.
    Args:
        embeddings: Array of embeddings in the cluster.
    Returns:
        The centroid embedding as a numpy array.
    """
    return np.mean(embeddings, axis=0)


def find_closest_to_center(
    embeddings: np.ndarray, values: list[str], center: np.ndarray, num_closest: int = 10
) -> list[str]:
    """
    Find the n closest points to the cluster center and return their values.
    Args:
        embeddings: Array of embeddings in the cluster.
        values: List of values corresponding to the embeddings.
        center: The centroid embedding.
        n_closest: Number of closest points to return.
    Returns:
        List of values closest to the center.
    """
    distances = euclidean_distances(np.array([center]), embeddings)[0]
    closest_indices = np.argsort(distances)[:num_closest]
    return [values[i] for i in closest_indices]


def split_by_label(
    df: pd.DataFrame, parent_cluster_id: int | None = None, max_exemplar_count: int = 10
) -> tuple[dict[int, ClusterDetails], pd.DataFrame]:
    """
    Split dataframe by label column and return cluster details and updated dataframe.
    Args:
        df: DataFrame with columns:
            - 'value' (list[str]): The values or identifiers for each data point.
            - 'embedding' (np.ndarray or array-like): The embedding vector for each data point.
            - 'label' (str or int): The label for each data point.
        parent_cluster_id: ID of parent cluster, if any.
        max_exemplar_count: Number of exemplars (closest to center) to select for each cluster.
    Returns:
        cluster_details: Dict mapping cluster_id to ClusterDetails objects.
        updated_df: DataFrame with an added 'cluster_id' column (int).
    """
    unique_labels = df["label"].unique()
    label_to_cluster = {label: i for i, label in enumerate(unique_labels)}
    df["cluster_id"] = df["label"].replace(label_to_cluster)
    cluster_details = {}
    for cluster_id in range(len(unique_labels)):
        cluster_mask = df["cluster_id"] == cluster_id
        cluster_embeddings = np.stack(list(df[cluster_mask]["embedding"].values))  # type: ignore
        cluster_values = df[cluster_mask]["value"].tolist()
        label_value = [label for label, cid in label_to_cluster.items() if cid == cluster_id][0]
        cluster_name = str(label_value)
        center = compute_cluster_center(cluster_embeddings)
        closest_values = find_closest_to_center(
            cluster_embeddings, cluster_values, center, num_closest=max_exemplar_count  # type: ignore
        )
        cluster_details[cluster_id] = ClusterDetails(
            cluster_id=cluster_id,
            exemplars=closest_values,
            name=cluster_name,
            parent_cluster_id=parent_cluster_id,
            is_noise_cluster=False,
            size=len(cluster_values),  # type: ignore
        )
    return cluster_details, df


def cluster_with_method(
    df: pd.DataFrame,
    method: ClusteringMethod,
    parent_cluster_id: int | None = None,
    all_cluster_details: dict[int, ClusterDetails] | None = None,
    minimum_cluster_size: int | float | None = None,
    max_exemplar_count: int = 10,
) -> tuple[dict[int, ClusterDetails], pd.DataFrame]:
    """
    Cluster dataframe using the specified clustering method.
    Args:
        df: DataFrame with columns:
            - 'embedding' (np.ndarray or array-like): The embedding vector for each data point.
            - 'value' (list[str]): The values or identifiers for each data point.
            - 'cluster_id' (int): The cluster id for each data point (optional, may be added/updated).
        method: Clustering method instance to use.
        parent_cluster_id: ID of parent cluster, if any.
        all_cluster_details: Existing cluster details for ID management.
        minimum_cluster_size: Minimum size of clusters to consider (int or float, optional).
        max_exemplar_count: Number of exemplars (closest to center) to select for each cluster.
    Returns:
        cluster_details: Dict mapping new_cluster_id to ClusterDetails objects.
        updated_df: DataFrame with updated 'cluster_id' column (int).
    """
    embeddings = np.stack(list(df["embedding"].values))
    cluster_labels = method.cluster(embeddings)
    return _process_cluster_results(
        df,
        embeddings,
        cluster_labels,
        method,
        parent_cluster_id,
        all_cluster_details,
        minimum_cluster_size,
        max_exemplar_count,
    )


def _process_cluster_results(
    df: pd.DataFrame,
    embeddings: np.ndarray,
    cluster_labels: np.ndarray,
    method: ClusteringMethod,
    parent_cluster_id: int | None,
    all_cluster_details: dict[int, ClusterDetails] | None,
    minimum_cluster_size: int | float | None = None,
    max_exemplar_count: int = 10,
) -> tuple[dict[int, ClusterDetails], pd.DataFrame]:
    """
    Process clustering results and create cluster details.
    Args:
        df: DataFrame with columns:
            - 'embedding' (np.ndarray or array-like): The embedding vector for each data point.
            - 'value' (list[str]): The values or identifiers for each data point.
            - 'cluster_id' (int): The cluster id for each data point (optional, may be added/updated).
        embeddings: Array of embeddings (np.ndarray).
        cluster_labels: Array of cluster labels (np.ndarray).
        method: Clustering method instance used.
        parent_cluster_id: ID of parent cluster, if any.
        all_cluster_details: Existing cluster details for ID management.
        minimum_cluster_size: Minimum size of clusters to consider for further subdivision. If in (0, 1], it is treated as
            a percentage of the dataset size. If None, no minimum size is enforced. Otherwise, it is treated as an absolute size.
        max_exemplar_count: Number of exemplars (closest to center) to select for each cluster.
    Returns:
        cluster_details: Dict mapping new_cluster_id to ClusterDetails objects.
        updated_df: DataFrame with updated 'cluster_id' column (int).
    """

    unique_clusters = np.unique(cluster_labels)
    n_points = len(embeddings)
    # Determine min_size_threshold based on minimum_cluster_size
    if minimum_cluster_size is None:
        min_size_threshold = 1  # Default to 1 to ensure all clusters are considered
    elif isinstance(minimum_cluster_size, float) and 0 < minimum_cluster_size <= 1:
        min_size_threshold = max(1, int(minimum_cluster_size * n_points))
    else:
        min_size_threshold = max(1, int(minimum_cluster_size))

    # Handle noise differently for different methods
    if method.has_noise:
        # Methods like HDBSCAN use -1 for noise
        noise_mask = cluster_labels == -1
        valid_clusters = unique_clusters[unique_clusters != -1]
        # Optionally, treat small clusters as noise if min_size_threshold is set
        cluster_sizes = np.bincount(cluster_labels[cluster_labels != -1])
        valid_clusters = [cl for cl in valid_clusters if np.sum(cluster_labels == cl) >= min_size_threshold]
    else:
        # Other methods don't have explicit noise, treat small clusters as noise
        cluster_sizes = np.bincount(cluster_labels)
        small_cluster_mask = np.isin(cluster_labels, np.where(cluster_sizes < min_size_threshold)[0])
        valid_clusters = unique_clusters[cluster_sizes[unique_clusters] >= min_size_threshold]
        noise_mask = small_cluster_mask  # noqa: F841
    if len(valid_clusters) == 0:
        return {}, df
    max_existing_cluster_id = max(all_cluster_details.keys()) if all_cluster_details else -1
    cluster_details = {}
    # Process each valid cluster
    for i, cluster_label in enumerate(valid_clusters):
        cluster_mask = cluster_labels == cluster_label
        cluster_embeddings = embeddings[cluster_mask]
        cluster_values = df[cluster_mask]["value"].tolist()
        new_cluster_id = max_existing_cluster_id + 1 + i
        df.loc[cluster_mask, "cluster_id"] = new_cluster_id
        center = compute_cluster_center(cluster_embeddings)
        closest_values = find_closest_to_center(
            cluster_embeddings, cluster_values, center, num_closest=max_exemplar_count  # type: ignore
        )
        cluster_details[new_cluster_id] = ClusterDetails(
            cluster_id=new_cluster_id,
            exemplars=closest_values,
            name=f"Cluster {new_cluster_id}",
            parent_cluster_id=parent_cluster_id,
            is_noise_cluster=False,
            size=len(cluster_values),  # type: ignore
        )
    return cluster_details, df


def recursive_cluster(
    df: pd.DataFrame,
    clustering_method: ClusteringMethod,
    cluster_cutoff_percent: int | float = 0.05,
    minimum_cluster_size: int | float | None = None,
    max_exemplar_count: int = 10,
) -> tuple[dict[int, ClusterDetails], pd.DataFrame]:
    """
    Recursively cluster a dataframe, starting with label splitting and then using the specified clustering method.
    Args:
        df: DataFrame with columns:
            - 'value' (list[str]): The values or identifiers for each data point.
            - 'embedding' (np.ndarray or array-like): The embedding vector for each data point.
            - 'label' (str or int): The label for each data point.
        clustering_method: Clustering method instance to use for subdivision.
        cluster_cutoff_percent: If float in (0, 1], continue clustering if subset >= (cutoff * original_dataset_size). If int, continue clustering if subset >= cutoff (absolute size).
        minimum_cluster_size: Minimum size of clusters to consider for further subdivision (int or float, optional).
        max_exemplar_count: Number of exemplars (closest to center) to select for each cluster.
    Returns:
        all_cluster_details: Dict mapping cluster_id to ClusterDetails objects.
        final_df: DataFrame with 'cluster_id' column populated (int).
    """
    all_cluster_details = {}
    current_df = df.copy()
    original_size = len(df)
    if isinstance(cluster_cutoff_percent, float) and 0 < cluster_cutoff_percent <= 1:
        min_subset_size = int(cluster_cutoff_percent * original_size)
    else:
        min_subset_size = int(cluster_cutoff_percent)
    failed_subdivision_attempts = set()

    # First iteration: split by labels
    cluster_details, current_df = split_by_label(current_df, max_exemplar_count=max_exemplar_count)
    all_cluster_details.update(cluster_details)
    # Create a queue of clusters to potentially subdivide
    clusters_to_process = []
    for cluster_id, details in cluster_details.items():
        if details.size >= min_subset_size:
            clusters_to_process.append(cluster_id)
    # Process clusters until no more clusters are large enough
    while clusters_to_process:
        current_cluster_id = clusters_to_process.pop(0)
        if current_cluster_id in failed_subdivision_attempts:
            continue
        cluster_mask = current_df["cluster_id"] == current_cluster_id
        cluster_subset = cast(pd.DataFrame, current_df[cluster_mask].copy())
        if len(cluster_subset) < min_subset_size:
            continue
        if len(cluster_subset) < clustering_method.minimum_required_points:
            failed_subdivision_attempts.add(current_cluster_id)
            logging.warning(
                f"Cluster {current_cluster_id} has only {len(cluster_subset)} points, "
                f"which is less than the minimum required points ({clustering_method.minimum_required_points}) "
                f"for {clustering_method.name} clustering as configured."
            )
            continue
        sub_cluster_details, clustered_subset = cluster_with_method(
            cluster_subset,
            method=clustering_method,
            parent_cluster_id=current_cluster_id,
            all_cluster_details=all_cluster_details,
            minimum_cluster_size=minimum_cluster_size,
            max_exemplar_count=max_exemplar_count,
        )
        if len(sub_cluster_details) <= 1:
            failed_subdivision_attempts.add(current_cluster_id)
            continue
        cluster_indices = current_df[cluster_mask].index
        # Update cluster_id for the subdivided points
        # NOTE: This works because we didn't reorder the DataFrame, so the indices still match
        for orig_idx, new_cluster_id in zip(cluster_indices, clustered_subset["cluster_id"]):
            current_df.loc[orig_idx, "cluster_id"] = new_cluster_id
        all_cluster_details.update(sub_cluster_details)
        # Update the parent cluster's exemplars to only include points that remain in it
        remaining_in_parent = current_df[current_df["cluster_id"] == current_cluster_id]
        if len(remaining_in_parent) > 0:
            parent_embeddings = np.stack(remaining_in_parent["embedding"].values)  # type: ignore
            parent_values = remaining_in_parent["value"].tolist()
            parent_center = compute_cluster_center(parent_embeddings)
            parent_exemplars = find_closest_to_center(
                parent_embeddings, parent_values, parent_center, num_closest=max_exemplar_count  # type: ignore
            )
            all_cluster_details[current_cluster_id].exemplars = parent_exemplars
            all_cluster_details[current_cluster_id].size = len(remaining_in_parent)
        else:
            del all_cluster_details[current_cluster_id]
            # For any clusters that were using this as a parent, remove the parent reference
            for details in all_cluster_details.values():
                if details.parent_cluster_id == current_cluster_id:
                    details.parent_cluster_id = None
        # Add new clusters to processing queue if they're large enough and log results
        for new_cluster_id, new_details in sub_cluster_details.items():
            if new_details.size >= min_subset_size and not new_details.is_noise_cluster:
                clusters_to_process.append(new_cluster_id)
    return all_cluster_details, current_df
