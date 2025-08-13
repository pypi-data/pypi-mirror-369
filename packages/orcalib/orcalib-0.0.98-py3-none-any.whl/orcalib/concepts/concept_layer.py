from __future__ import annotations

import base64
import json
import logging
import pickle
from collections import Counter
from itertools import batched
from typing import Any, Sequence, Type, cast
from warnings import warn

import hdbscan
import numpy as np
import optuna
import pandas as pd
import torch
import umap
from datasets import ClassLabel, Dataset
from numpy.typing import NDArray
from pydantic import BaseModel
from sklearn.metrics import silhouette_score
from torch import Tensor
from tqdm.auto import tqdm

from orcalib.agents.agent_utils import run_agent_safely
from orcalib.agents.describe_concept import (
    ConceptualGroupInstance,
    DescribeConceptContext,
    DescribeConceptResult,
    describe_concept_agent,
)
from orcalib.embedding.embedding_models import EmbeddingModel
from orcalib.memoryset.memoryset import LabeledMemoryset

NOISE_CLUSTER = -1
MINIMUM_SCORE = float("-inf")


def subsample_dataset(
    dataset: Dataset, max_rows: int, stratify_by_column: str | None = None, seed: int = 42
) -> Dataset:
    """
    Reduce the dataset to a maximum number of rows.

    If the dataset has fewer rows than `max_rows`, return a copy of the dataset.
    If the dataset has more rows than `max_rows`, return a random sample of `max_rows` rows.

    Args:
        dataset: The input dataset to reduce.
        max_rows: Maximum number of rows to retain in the dataset.
        stratify_by_column: Optional column name to stratify the sampling by, must be a [ClassLabel][datasets.ClassLabel] column.
        seed: Random seed for reproducibility.

    Returns:
        A reduced dataset with at most `max_rows` rows.
    """
    if max_rows >= len(dataset):
        return dataset.map(lambda x: x)
    return dataset.train_test_split(train_size=max_rows, stratify_by_column=stratify_by_column, seed=seed)["train"]


def object_to_pickle_str(obj: object) -> str:
    """
    Serialize an object to a base64-encoded string using pickle.

    Args:
        obj: The object to serialize.

    Returns:
        A base64-encoded string representation of the object.
    """
    data: bytes = pickle.dumps(obj)
    return base64.b64encode(data).decode("utf-8")


def unpickle_from_str[T](data: str, t: Type[T]) -> T:
    """
    Deserialize an object from a base64-encoded string.

    Args:
        data: The base64-encoded string representation of the object.
        t: The expected type of the deserialized object.

    Returns:
        The deserialized object cast to the specified type.
    """
    raw = base64.b64decode(data.encode("utf-8"))
    return cast(T, pickle.loads(raw))


class ConceptCluster(BaseModel):
    """
    Represents a cluster of concepts with metadata about its composition.

    Attributes:
        cluster_id: Unique identifier for the cluster.
        size: Number of elements in the cluster.
        dominant_label: The most common label in the cluster.
        label_purity: Fraction of elements in the cluster with the dominant label.
        label_counts: Counts of each label in the cluster.
        description: Optional description of the cluster.
        name: Optional name of the cluster.
    """

    cluster_id: int
    size: int
    dominant_label: int
    label_purity: float
    label_counts: Sequence[int]
    description: str | None = None
    name: str | None = None


class ConceptPrediction(BaseModel):
    """
    Represents a prediction made by the ConceptMap.

    Attributes:
        label: The predicted label for the input.
        probability: The confidence score for the predicted label.
    """

    label: int | None
    probability: float | None
    cluster: ConceptCluster | None = None


class ConceptMap:
    """
    Represents a conceptual map of clusters derived from embeddings.

    Attributes:
        fit_hdbscan: The HDBSCAN clustering model used for clustering.
        fit_umap: The UMAP dimensionality reduction model used for embedding reduction.
        predicted_labels: Cluster labels predicted by HDBSCAN.
        true_labels: Ground-truth labels for the dataset.
        embedding: The embedding model used to generate embeddings for the data.
        cluster_by_id: A dictionary mapping cluster IDs to their corresponding ConceptCluster objects.
    """

    def __init__(
        self,
        fit_hdbscan: hdbscan.HDBSCAN,
        fit_umap: umap.UMAP,
        true_labels: NDArray[np.int32],
        embedding_model: EmbeddingModel,
    ):
        """
        Initialize the ConceptMap with clustering and embedding models.

        Args:
            fit_hdbscan: Trained HDBSCAN clustering model.
            fit_umap: Trained UMAP dimensionality reduction model.
            true_labels: Ground-truth labels for the dataset.
            embedding: The embedding model used for generating embeddings.
        """
        self.fit_hdbscan = fit_hdbscan
        self.fit_umap = fit_umap
        self.embedding_model = embedding_model
        self.true_labels = true_labels

        # Build cluster objects from HDBSCAN soft clustering
        cluster_details = self._build_clusters(self.true_labels)

        self.cluster_by_id = {cluster.cluster_id: cluster for cluster in cluster_details}

    def __getstate__(self) -> dict:
        """
        Serialize the state of the ConceptMap for pickling.

        Returns:
            A dictionary containing the serialized state.
        """
        return {
            "fit_hdbscan": self.fit_hdbscan,
            "fit_umap": self.fit_umap,
            "true_labels": self.true_labels,
            "cluster_by_id": self.cluster_by_id,
            "embedding_path": self.embedding_model.path,
        }

    def __setstate__(self, state: dict) -> None:
        """
        Deserialize the state of the ConceptMap from pickled data.

        Args:
            state: The serialized state dictionary.
        """
        self.fit_hdbscan = state["fit_hdbscan"]
        self.fit_umap = state["fit_umap"]
        self.true_labels = state["true_labels"]
        self.cluster_by_id = state["cluster_by_id"]
        self.embedding_model = EmbeddingModel(state["embedding_path"])

    def _predict_label_confidence(
        self,
        embeddings: NDArray[np.float32],
        already_reduced: bool = False,
    ) -> list[ConceptPrediction]:
        """
        Classify embeddings using soft clustering.

        Args:
            embeddings: The input embeddings to classify.
            already_reduced: Whether the embeddings are already reduced by UMAP.

        Returns:
            A list of ConceptPrediction objects containing the predicted labels and probabilities.

        """
        cluster_ids, probabilities = reduce_and_cluster(embeddings, self.fit_umap, self.fit_hdbscan, already_reduced)
        label_ids = [self.cluster_to_label(cluster_id) for cluster_id in cluster_ids]

        # Step 3: Map cluster IDs to labels
        return [
            ConceptPrediction(
                label=label_id,
                probability=prob,
                cluster=self.cluster_by_id[cluster_id] if cluster_id != NOISE_CLUSTER else None,
            )
            for label_id, cluster_id, prob in zip(label_ids, cluster_ids, probabilities)
        ]

    def is_noise(self, samples: list[str], *, confidence_threshold=0.20) -> np.ndarray:
        """
        Experimental: This function is subject to change and may not work as expected.

        Args:
            samples: A list of input samples to classify.

        Returns:
            A numpy array indicating whether each sample is classified as noise.
        """
        warn("The 'is_noise' function is experimental and may change in future versions.", UserWarning)
        predictions = self.predict(samples)

        # Check if the predicted labels are None (indicating noise)
        def is_prediction_noise(p: ConceptPrediction) -> bool:
            return p.label is None or p.probability is None or p.probability < confidence_threshold

        return np.array([is_prediction_noise(p) for p in predictions], dtype=np.bool_)

    # Classify new embeddings using soft clustering
    def predict(
        self,
        samples: list[str] | NDArray[np.float32],
        already_reduced: bool = False,
        batch_size: int = 1000,
    ) -> list[ConceptPrediction]:
        """
        Classify new embeddings using soft clustering.
        """

        predictions: list[ConceptPrediction] = []

        if already_reduced:
            if not isinstance(samples, np.ndarray):
                raise TypeError("Samples should be a numpy array when already_reduced is True.")
            if samples.ndim != 2:
                raise ValueError("When already_reduced is True, samples should be a 2D array.")
            if samples.shape[1] != self.fit_umap.n_components:
                raise ValueError(
                    f"Samples should have {self.fit_umap.n_components} dimensions, but got {samples.shape[1]} dimensions."
                )

        if isinstance(samples, np.ndarray):
            return self._predict_label_confidence(
                samples,
                already_reduced=already_reduced,
            )

        if not isinstance(samples, list):
            raise TypeError("Samples should be a list of strings or a numpy array.")

        for batch in batched(samples, batch_size):
            embeddings_raw = self.embedding_model.embed(list(batch), show_progress_bar=False, use_cache=True)
            embeddings = np.vstack(embeddings_raw)
            if embeddings.shape[0] != len(batch):
                raise ValueError("Mismatch between number of embeddings and batch size.")

            batch_predictions = self._predict_label_confidence(
                embeddings,
                already_reduced=False,
            )

            # Append the predictions to the main list
            predictions.extend(batch_predictions)

        return predictions

    def test(self, embeddings: NDArray[np.float32], true_labels: NDArray, already_reduced: bool = False) -> float:
        """
         Test the accuracy of the ConceptMap on a given set of embeddings and true labels.

         Args:
             embeddings: The input embeddings to test.
             true_labels: The ground-truth labels for the embeddings.
             already_reduced: Whether the embeddings are already reduced by UMAP.

        Returns:
             The accuracy score of the ConceptMap on the given embeddings and true labels.
        """
        predictions = self.predict(samples=embeddings, already_reduced=already_reduced)

        predicted_label_np = np.array([p.label or NOISE_CLUSTER for p in predictions], dtype=np.int32)

        correct = np.sum(predicted_label_np == true_labels)
        total = len(predictions)

        accuracy_score = correct / total

        return accuracy_score

    def _build_clusters(self, true_labels: NDArray[np.int32], noise_threshold: float = 0.2) -> list[ConceptCluster]:
        """
        Build clusters from the predicted labels and true labels.

        Args:
            true_labels: The ground-truth labels for the dataset.

        Returns:
            A list of ConceptCluster objects representing the clusters.
        """

        cluster_prob_matrix = hdbscan.all_points_membership_vectors(self.fit_hdbscan)
        cluster_ids = np.argmax(cluster_prob_matrix, axis=1)
        sorted_ids = sorted(set(cluster_ids.tolist()) - {NOISE_CLUSTER})
        cluster_prob = np.max(cluster_prob_matrix, axis=1)

        noise_mask = cluster_prob <= noise_threshold
        cluster_ids[noise_mask] = NOISE_CLUSTER

        def create_cluster(cluster_id: int):
            mask = cluster_ids == cluster_id
            cluster_size = len(cluster_ids[mask])
            assert cluster_size > 0, "Cluster size must be greater than 0"
            label_slice = true_labels[mask]

            label_counts = Counter(label_slice.tolist())  # type: ignore
            dominant_label, dominant_count = label_counts.most_common(1)[0]
            purity = dominant_count / cluster_size

            return ConceptCluster(
                cluster_id=cluster_id,
                size=cluster_size,
                dominant_label=int(dominant_label),
                label_purity=purity,
                label_counts=[label_counts.get(k, 0) for k in sorted(label_counts)],
            )

        return [create_cluster(cluster_id) for cluster_id in sorted_ids]

    def cluster_to_label(self, cluster_id: int) -> int | None:
        """
        Takes a cluster ID and returns the most common label within that cluster OR None if it's noise or not pure.

        Args:
            cluster_id: The cluster ID to map to a label.

        Returns:
            The most common label within the cluster, or None if the cluster is noise or not pure.
        """
        if cluster_id == NOISE_CLUSTER:
            return None
        if cluster_id not in self.cluster_by_id:
            raise ValueError(f"Cluster ID {cluster_id} not found in the cluster map.")
        return self.cluster_by_id[cluster_id].dominant_label

    async def _name_cluster(
        self, concept: ConceptualGroupInstance, context: DescribeConceptContext, retry_count: int = 3
    ) -> DescribeConceptResult:
        """
        Name a cluster based on the most common labels within the cluster.

        Args:
            concept: The conceptual group instance representing the cluster.
            context: The context for describing the concept.
            retry_count: Number of retries in case of failure.

        Returns:
            A tuple containing the name and description of the cluster.
        """
        for i in range(retry_count):
            try:
                result = await describe_concept_agent.run(
                    concept,
                    deps=context,
                )

                return result.data
            except json.JSONDecodeError as e:
                logging.error(f"Error naming cluster: {e}")
                if i == retry_count - 1:
                    raise
                continue
        else:
            raise RuntimeError("Failed to name cluster after multiple attempts.")

    def generate_cluster_names(
        self,
        memories: LabeledMemoryset,
        categorization_description: str,
        example_count: int = 7,
        contrast_count: int = 5,
    ):
        """
        Name clusters based on the most common labels within each cluster.

        Args:
            memories: The labeled memoryset containing data and embeddings.
            categorization_description: Description of the categorization task, e.g., "Categorizing news articles by topic"
            example_count: Number of examples to use for naming each cluster.
            contrast_count: Number of contrasting examples to use for naming each cluster.
        """
        cluster_details = self.cluster_by_id

        df: pd.DataFrame = memories.to_pandas()
        # df has columns: ["value", "label", "embedding"]
        predictions = self.predict(np.stack(df["embedding"]))  # type: ignore
        cluster_ids = [p.cluster.cluster_id if p.cluster else NOISE_CLUSTER for p in predictions]
        df["cluster_id"] = cluster_ids

        model_context = DescribeConceptContext(
            base_decision_description=categorization_description,
        )

        # Using the dataframe, find k examples that that have the same label and cluster_id.
        for cluster_id, cluster in tqdm(cluster_details.items()):
            # Get the examples from the dataframe
            examples = df[(df["label"] == cluster.dominant_label) & (df["cluster_id"] == cluster_id)]
            counter_examples = df[
                (df["label"] == cluster.dominant_label) & (df["cluster_id"] != cluster_id) & (df["cluster_id"] >= 0)
            ]
            examples = examples.head(example_count)
            counters = counter_examples.head(contrast_count)

            response = run_agent_safely(
                describe_concept_agent,
                ConceptualGroupInstance(
                    outer_concept_label=str(memories.get_label_name(cluster.dominant_label)),
                    representative_examples=examples["value"].tolist(),  # type: ignore
                    contrasting_examples=counters["value"].tolist(),  # type: ignore
                ),
                model_context,
            )

            if response is None:
                logging.error("Failed to generate cluster name and description.")
                cluster.name = f"Cluster {cluster_id}"
                cluster.description = "No description available."
                continue
            else:
                cluster.name = response.name
                cluster.description = response.description

    @staticmethod
    def build(
        memoryset: LabeledMemoryset,
        # TODO: Wrap these in a config basemodel to simplify
        max_sample_rows: int = 30_000,
        n_trials: int = 15,
        min_desired_clusters_per_class: int = 2,
        max_desired_clusters_per_class: int = 5,
        cluster_count_weight: float = 1.0,
        accuracy_weight: float = 3.0,
        noise_weight: float = 5.0,
        seed: int = 42,
    ) -> ConceptMap:
        """
        Builds a ConceptMap by optimizing clustering parameters using Optuna.

        Args:
            memoryset: The labeled memoryset containing data and embeddings.
            max_sample_rows: Maximum number of rows to sample from the dataset.
            n_trials: Number of trials for Optuna optimization.
            min_desired_clusters_per_class: Minimum number of clusters per class.
            max_desired_clusters_per_class: Maximum number of clusters per class.
            cluster_count_weight: Weight for the cluster count in the composite score.
            accuracy_weight: Weight for accuracy in the composite score.
            noise_weight: Weight for noise penalty in the composite score.
            seed: Random seed for reproducibility.

        Returns:
            A ConceptMap object containing the optimized clustering results.
        """
        data = (
            memoryset.to_dataset()
            .cast_column("label", ClassLabel(names=memoryset.label_names))
            .train_test_split(test_size=0.15, shuffle=True, seed=seed, stratify_by_column="label")
        )

        ds = subsample_dataset(data["train"], max_sample_rows)

        embeddings = torch.stack(
            [torch.tensor(cast(dict[str, Any], r)["embedding"]) for r in ds], dim=0
        )  # (num_train_samples, embedding_dim)
        true_labels = torch.tensor(ds["label"])  # (num_train_samples,)

        test_embeddings = torch.stack(
            [torch.tensor(cast(dict[str, Any], r)["embedding"]) for r in data["test"]], dim=0
        )  # (num_test_samples, embedding_dim)
        test_true_labels = torch.tensor(data["test"]["label"])  # (num_test_samples,)

        study = optuna.create_study(direction="maximize")

        # Wrap the objective function with additional fixed arguments.
        func = lambda trial: _cluster_trial(  # noqa: E731
            trial,
            memory_embeddings=embeddings,
            true_labels=true_labels,
            test_embeddings=test_embeddings,
            test_true_labels=test_true_labels,
            min_desired_clusters_per_class=min_desired_clusters_per_class,
            max_desired_clusters_per_class=max_desired_clusters_per_class,
            cluster_count_weight=cluster_count_weight,
            accuracy_weight=accuracy_weight,
            noise_weight=noise_weight,
            embedding_model=memoryset.embedding_model,
        )
        study.optimize(func, n_trials=n_trials, show_progress_bar=True)

        best_trial = study.best_trial
        log_str = "🎉 Best trial:\n"
        for key, value in best_trial.user_attrs.items():
            if isinstance(value, str) and len(value) > 200:
                continue
            log_str += f"   {key}: {value}\n"
        log_str += f"   Best composite score: {best_trial.value:.3f}\n"
        logging.info(log_str)

        # This seems weird, but due to how optuna works, the best trial's user attributes
        # will contain the serialized predictor. We can deserialize it here to get the
        # final predictor object which contains all the clustering information.
        predictor = unpickle_from_str(best_trial.user_attrs["predictor_byte_str"], ConceptMap)

        return predictor


def reduce_and_cluster(
    embeddings: NDArray[np.float32],
    umap_model: umap.UMAP,
    hdbscan_model: hdbscan.HDBSCAN,
    already_reduced: bool = False,
) -> tuple[NDArray[np.int32], NDArray[np.float32]]:
    """
    Shared utility function to perform UMAP reduction and HDBSCAN clustering.

    Args:
        embeddings: Input embeddings to process.
        umap_model: Trained UMAP model for dimensionality reduction.
        hdbscan_model: Trained HDBSCAN model for clustering.
        already_reduced: Whether the embeddings are already reduced by UMAP.

    Returns:
        A tuple containing cluster IDs and probabilities.
    """
    if not already_reduced:
        reduced_embeddings = umap_model.transform(embeddings, force_all_finite=True)  # type: ignore
    else:
        if embeddings.ndim != 2:
            raise ValueError("Embeddings should be a 2D array when already_reduced is True.")
        if embeddings.shape[1] != umap_model.n_components:
            raise ValueError(
                f"Embeddings should have {umap_model.n_components} dimensions, but got {embeddings.shape[1]} dimensions."
            )
        reduced_embeddings = embeddings

    result = hdbscan.approximate_predict(hdbscan_model, reduced_embeddings, return_connecting_points=False)
    cluster_ids, probabilities = result[:2]  # Unpack only the first two elements

    return cluster_ids, probabilities.astype(np.float32)


def _cluster_trial(
    trial: optuna.Trial,
    memory_embeddings: Tensor,  # (num_samples, embedding_dim)
    true_labels: Tensor,  # (num_samples,)
    test_embeddings: Tensor,  # (num_samples, embedding_dim)
    test_true_labels: Tensor,  # (num_samples,)
    embedding_model: EmbeddingModel,
    min_desired_clusters_per_class: int = 2,
    max_desired_clusters_per_class: int = 5,
    cluster_count_weight: float = 1.0,
    accuracy_weight: float = 3.0,
    noise_weight: float = 5.0,
) -> float:
    """
    Runs a single trial of clustering with specific parameters.

    Args:
        trial: The Optuna trial object.
        memory_embeddings: Embeddings for the training dataset.
        true_labels: Ground-truth labels for the training dataset.
        test_embeddings: Embeddings for the test dataset.
        test_true_labels: Ground-truth labels for the test dataset.
        embedding_model: The embedding model used for generating embeddings.
        min_desired_clusters_per_class: Minimum number of clusters per class.
        max_desired_clusters_per_class: Maximum number of clusters per class.
        cluster_count_weight: Weight for the cluster count in the composite score.
        accuracy_weight: Weight for accuracy in the composite score.
        noise_weight: Weight for noise penalty in the composite score.

    Returns:
        A composite score for the trial based on clustering performance.
    """
    if min_desired_clusters_per_class <= 0:
        raise ValueError("min_desired_clusters_per_class must be greater than 0")
    if max_desired_clusters_per_class <= min_desired_clusters_per_class:
        raise ValueError("max_desired_clusters_per_class must be greater than min_desired_clusters_per_class")
    if cluster_count_weight <= 0:
        raise ValueError("cluster_count_weight must be greater than 0")
    if accuracy_weight <= 0:
        raise ValueError("accuracy_weight must be greater than 0")
    if noise_weight <= 0:
        raise ValueError("noise_weight must be greater than 0")

    row_count = len(true_labels)
    unique, counts = np.unique(true_labels, return_counts=True)
    class_count = len(unique)

    # Define candidate parameters with Optuna suggestions.
    # You can modify the ranges as needed or use suggest_categorical if you have fixed candidate values.

    # Ensure dimensions are appropriate for the dataset size
    max_dims = min(10, row_count - 1)
    dim_options = [d for d in [2, 3, 5, 7, 10] if d <= max_dims]
    if not dim_options:
        dim_options = [min(2, max_dims)]
    umap_dims = trial.suggest_categorical("umap_dims", dim_options)

    # Ensure n_neighbors is appropriate for the dataset size
    max_neighbors = max(2, row_count - 1)
    neighbor_options = [n for n in [5, 10, 20, 30, 40, 50] if n < max_neighbors]
    if not neighbor_options:
        neighbor_options = [min(5, max(2, max_neighbors - 1))]
    umap_n_neighbors = trial.suggest_categorical("umap_n_neighbors", neighbor_options)

    umap_min_dist = trial.suggest_categorical("umap_min_dist", [0.0, 0.001, 0.005, 0.05, 0.01, 0.05])

    # For HDBSCAN, if you have candidate values in mind, use categorical suggestions.
    # Otherwise, define a reasonable range relative to dataset size.
    # Ensure min_cluster_size is reasonable for small datasets
    max_cluster_size = max(10, int(row_count / (class_count * max_desired_clusters_per_class * 2)))
    min_cluster_size_lower = max(2, row_count // 10)
    min_cluster_size_upper = min(max_cluster_size, row_count // 3)

    if min_cluster_size_lower >= min_cluster_size_upper:
        min_cluster_size_upper = min_cluster_size_lower + 1

    min_cluster_size = trial.suggest_int(
        "min_cluster_size",
        min_cluster_size_lower,
        min_cluster_size_upper,
        log=True,
    )

    # NOTE: This is disabled for now, because it creates a conflict with approximate_predict.
    # cluster_selection_epsilon = trial.suggest_float("cluster_selection_epsilon", 0.0, 0.2, step=0.025)
    min_samples_ratio = trial.suggest_float("min_samples_ratio", 0.30, 1.0, step=0.1)
    min_samples = max(1, int(min_samples_ratio * min_cluster_size))  # Ensure min_samples is at least 1

    # Compute sample weights: weight samples from smaller classes more heavily.
    class_weights = {label: max(counts) / count for label, count in zip(unique, counts)}
    sample_weights = np.array([class_weights[label.item()] for label in true_labels])

    # Log the trial's parameters for debugging.
    trial.set_user_attr("umap_n_neighbors", umap_n_neighbors)
    trial.set_user_attr("min_cluster_size", min_cluster_size)
    trial.set_user_attr("min_samples", min_samples)

    # Apply UMAP reduction.
    umap_reducer = umap.UMAP(
        n_components=umap_dims,
        metric="cosine",
        min_dist=umap_min_dist,
        n_neighbors=umap_n_neighbors,
        random_state=42,
    )
    reduced_data = umap_reducer.fit_transform(memory_embeddings, y=true_labels, sample_weight=sample_weights)
    reduced_data = np.array(reduced_data)

    # Apply HDBSCAN clustering.
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        prediction_data=True,
        # cluster_selection_epsilon=cluster_selection_epsilon,
    )

    # We're intentionally ignoring the output, because we are going to use the
    # soft clustering results instead.
    _ = clusterer.fit_predict(reduced_data)

    soft_memberships = hdbscan.all_points_membership_vectors(clusterer)
    is_degenerate = len(soft_memberships.shape) == 1
    if is_degenerate:
        # If the clustering is degenerate, we need to reshape it to 2D.
        trial.set_user_attr("num_clusters", 0)
        trial.set_user_attr("noise_ratio", 1)
        trial.set_user_attr("silhouette_score", -1)
        trial.set_user_attr("avg_cluster_stability", 0)
        trial.set_user_attr("accuracy", 0)
        trial.set_user_attr("cluster_count", 0)
        trial.set_user_attr("predictor_byte_str", "")

        return MINIMUM_SCORE

    soft_labels = np.argmax(soft_memberships, axis=1)

    # Evaluate clustering configuration.
    num_clusters = len(clusterer.prediction_data_.exemplars)
    soft_confidences = np.max(soft_memberships, axis=1)
    noise_ratio = np.sum(soft_confidences < 0.18) / len(reduced_data)

    # Compute silhouette score only if there are at least 2 clusters.
    if num_clusters > 1:
        try:
            sil = silhouette_score(reduced_data, soft_labels)
        except Exception:
            sil = -1
    else:
        sil = -1

    # Compute average cluster stability (HDBSCAN's persistence).
    if hasattr(clusterer, "cluster_persistence_") and clusterer.cluster_persistence_ is not None:
        valid_clusters = [lab for lab in set(soft_labels) if lab != NOISE_CLUSTER]
        if valid_clusters:
            stability_vals = [clusterer.cluster_persistence_[lab] for lab in valid_clusters]
            avg_stability = np.mean(stability_vals)
        else:
            avg_stability = 0
    else:
        avg_stability = 0

    predictor = ConceptMap(
        fit_hdbscan=clusterer,
        fit_umap=umap_reducer,
        true_labels=true_labels.numpy(),  # Pass the numpy array of true labels for classification
        embedding_model=embedding_model,
    )

    mapped_test_embeddings = predictor.fit_umap.transform(test_embeddings, force_all_finite=True)  # type: ignore
    mapped_test_embeddings = np.array(mapped_test_embeddings)
    accuracy_score = predictor.test(mapped_test_embeddings, test_true_labels.numpy(), already_reduced=True)

    cluster_score = 0
    min_desired_clusters = min_desired_clusters_per_class * class_count
    max_desired_clusters = max_desired_clusters_per_class * class_count
    if num_clusters < min_desired_clusters:
        cluster_score = (num_clusters - min_desired_clusters) / min_desired_clusters
    elif num_clusters > max_desired_clusters:
        cluster_score = (max_desired_clusters - num_clusters) / max_desired_clusters

    # Composite score: higher silhouette and stability are good; noise is penalized.
    composite_score = (
        accuracy_weight * accuracy_score
        + sil
        - (noise_weight * noise_ratio)
        + avg_stability
        + cluster_count_weight * cluster_score
    )

    # Log intermediate values for debugging:

    trial.set_user_attr("num_clusters", num_clusters)
    trial.set_user_attr("noise_ratio", noise_ratio)
    trial.set_user_attr("silhouette_score", sil)
    trial.set_user_attr("avg_cluster_stability", avg_stability)
    trial.set_user_attr("accuracy", accuracy_score)
    trial.set_user_attr("cluster_count", len(predictor.cluster_by_id))
    trial.set_user_attr("predictor_byte_str", object_to_pickle_str(predictor))

    logging.info(
        f"Trial {trial.number}: accuracy={accuracy_score:.4f}, noise_ratio={noise_ratio:.4f}, cluster_count={num_clusters}, cluster_score={cluster_score:.4f}"
    )
    # Log the trial's composite score

    return composite_score
