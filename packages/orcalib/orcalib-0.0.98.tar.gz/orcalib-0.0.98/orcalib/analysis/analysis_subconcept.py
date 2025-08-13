from __future__ import annotations

from warnings import warn

import numpy as np
from pydantic import BaseModel

from ..concepts.concept_layer import ConceptMap
from ..memoryset.memoryset import LabeledMemoryset
from ..utils.pydantic import UUID7
from .analysis import MemorysetAnalysis

NOISE_CLUSTER = -1


class MemorySubconceptMetrics(BaseModel):
    """Concept-analysis metrics for a single memory."""

    subconcept_cluster_id: int | None
    """The ID of the subconcept cluster this memory belongs to, or -1 if it is an outlier."""

    subconcept_name: str | None
    """The name of the subconcept this memory belongs to, or Noise if it is an outlier."""


class MemorysetSubconceptMetrics(BaseModel):
    """Concept-analysis metrics for the entire memoryset."""

    class SubconceptClusterMetrics(BaseModel):
        """Metrics for a single cluster within an analysis."""

        cluster_id: int
        """The cluster id"""

        name: str
        """The name of the cluster"""

        primary_label_index: int | None = None
        """The index of the primary label in the cluster, if any"""

        description: str | None = None
        """The description of the cluster"""

        memory_count: int
        """The number of memories in the cluster"""

    clusters_by_id: dict[int, SubconceptClusterMetrics]
    """The metrics for each cluster"""

    num_clusters: int
    """The number of clusters"""

    num_outliers: int
    """The number of outliers"""


class MemorysetSubconceptAnalysisConfig(BaseModel):
    """Configuration for memoryset concept analysis."""

    high_level_description: str | None = None
    """A high-level description of the concept analysis, e.g., "Classify news articles by topic." This
    helps the agent understand how to name and describe the subconcepts."""

    max_sample_rows: int = 20_000
    """Maximum number of rows to sample from the memoryset for analysis.
    Using a lower number will speed up the analysis, but may reduce its accuracy."""

    max_trial_count: int = 10
    """Maximum number of trials for hyperparameter optimization."""

    min_desired_clusters_per_label: int = 2
    """Minimum number of desired clusters per label.
    The clustering algorithm will try to find at least this many clusters for each label."""

    max_desired_clusters_per_label: int = 5
    """Maximum number of desired clusters per label.
    The clustering algorithm will try to find fewer than this many clusters within each label."""

    accuracy_importance: float = 0.5
    """Importance of accuracy in the clustering algorithm."""

    noise_penalty: float = 0.5
    """Importance of noise in the clustering algorithm.
    A higher value will penalize noise more heavily, leading to fewer noise points."""

    naming_examples_count: int = 7
    """Maximum number of examples to use for naming clusters. Increasing this can improve the quality of cluster names,
    but will also increase the time taken to generate names. Increasing this too much may lead to diminishing returns."""

    naming_counterexample_count: int = 5
    """Maximum number of counterexamples to use for naming clusters. Increasing this can improve the quality of cluster names,
    but will also increase the time taken to generate names. Increasing this too much may lead to diminishing returns."""

    seed: int = 42
    """Random seed for reproducibility."""


class MemorysetSubconceptAnalysis(
    MemorysetAnalysis[MemorysetSubconceptAnalysisConfig, MemorySubconceptMetrics, MemorysetSubconceptMetrics]
):
    """Class for analyzing the concepts in a memoryset."""

    name = "subconcepts"

    requires_lookups = False  # This analysis does not require lookups, as it operates on the memoryset directly.

    def __init__(self, config: MemorysetSubconceptAnalysisConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or MemorysetSubconceptAnalysisConfig(**kwargs)
        ## TODO: Update the list of steps to include all of the optuna search steps.

    def on_batch(self, memories_batch, neighbors_batch):
        raise NotImplementedError("This method should not be called during this analysis.")

    def _create_fallback_clusters(
        self,
    ) -> tuple[MemorysetSubconceptMetrics, list[tuple[UUID7, MemorySubconceptMetrics]]]:
        """
        Create a fallback clustering result when the dataset is too small for meaningful clustering.
        Returns one cluster per label using the actual label names.
        """
        clusters_by_id = {}
        memory_metrics = []

        for label_index, label_name in enumerate(self.memoryset.label_names):
            # Count memories for this label
            memories_with_label = [memory for memory in self.memoryset if memory.label == label_index]

            if memories_with_label:  # Only create cluster if there are memories with this label
                cluster_metrics = MemorysetSubconceptMetrics.SubconceptClusterMetrics(
                    cluster_id=label_index,
                    name=label_name,
                    description=f"All memories labeled as '{label_name}'",
                    memory_count=len(memories_with_label),
                    primary_label_index=label_index,
                )
                clusters_by_id[label_index] = cluster_metrics

                # Add memory metrics for all memories in this label
                for memory in memories_with_label:
                    memory_metrics.append(
                        (
                            memory.memory_id,
                            MemorySubconceptMetrics(subconcept_cluster_id=label_index, subconcept_name=label_name),
                        )
                    )

        cluster_results = MemorysetSubconceptMetrics(
            clusters_by_id=clusters_by_id,
            num_outliers=0,
            num_clusters=len(clusters_by_id),
        )
        return cluster_results, memory_metrics

    def after_all(self) -> tuple[MemorysetSubconceptMetrics, list[tuple[UUID7, MemorySubconceptMetrics]]]:
        """Run the concept analysis on the memoryset."""
        if not isinstance(self.memoryset, LabeledMemoryset):
            raise TypeError("Concept analysis requires a LabeledMemoryset.")

        # Check if the dataset is large enough for meaningful clustering
        if len(self.memoryset) < 20:
            warn(
                f"Dataset is too small ({len(self.memoryset)} samples) for reliable clustering. Consider using at least 20 samples."
            )
            return self._create_fallback_clusters()

        concept_map = ConceptMap.build(
            self.memoryset,
            max_sample_rows=self.config.max_sample_rows,
            min_desired_clusters_per_class=self.config.min_desired_clusters_per_label,
            max_desired_clusters_per_class=self.config.max_desired_clusters_per_label,
            cluster_count_weight=1.0,
            accuracy_weight=self.config.accuracy_importance,
            noise_weight=self.config.noise_penalty,
            seed=self.config.seed,
        )

        high_level_description = self.config.high_level_description
        if high_level_description is None:
            high_level_description = (
                f"Classify text samples into these categories: {','.join(self.memoryset.label_names)}."
            )

        concept_map.generate_cluster_names(
            self.memoryset,
            categorization_description=high_level_description,
            example_count=self.config.naming_examples_count,
            contrast_count=self.config.naming_counterexample_count,
        )

        # Collect the cluster information for each memory
        # Get cluster assignments for all memories in the memoryset using their existing embeddings
        memory_metrics: list[tuple[UUID7, MemorySubconceptMetrics]] = []

        # Get all memories from the memoryset and use their pre-computed embeddings
        all_embeddings = []
        all_memory_ids = []

        for memory in self.memoryset:
            all_embeddings.append(memory.embedding)
            all_memory_ids.append(memory.memory_id)

        # Stack embeddings into a numpy array and use the concept map to predict cluster assignments
        embeddings_array = np.stack(all_embeddings)
        predictions = concept_map.predict(embeddings_array, already_reduced=False)

        # Create MemoryConceptMetrics for each memory
        for memory_id, prediction in zip(all_memory_ids, predictions):
            if prediction.cluster is not None:
                cluster_id = prediction.cluster.cluster_id
                cluster_name = prediction.cluster.name or f"Cluster {cluster_id}"

                # Handle noise cluster
                if cluster_id == -1:
                    cluster_name = "Noise"
            else:
                # If no cluster prediction available, mark as noise
                cluster_id = -1
                cluster_name = "Noise"

            memory_metrics.append(
                (memory_id, MemorySubconceptMetrics(subconcept_cluster_id=cluster_id, subconcept_name=cluster_name))
            )

        # Create a mapping of memory IDs to their cluster metrics
        cluster_results = MemorysetSubconceptMetrics(
            clusters_by_id={
                cluster_id: MemorysetSubconceptMetrics.SubconceptClusterMetrics(
                    cluster_id=cluster_id,
                    name=cluster.name or f"Cluster {cluster_id}",
                    description=cluster.description,
                    memory_count=cluster.size,
                    primary_label_index=cluster.dominant_label,
                )
                for cluster_id, cluster in concept_map.cluster_by_id.items()
            },
            num_outliers=(
                0 if NOISE_CLUSTER not in concept_map.cluster_by_id else concept_map.cluster_by_id[NOISE_CLUSTER].size
            ),
            num_clusters=len(concept_map.cluster_by_id),
        )

        return cluster_results, memory_metrics
