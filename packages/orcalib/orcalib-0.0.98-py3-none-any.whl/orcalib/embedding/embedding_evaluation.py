from typing import overload

import numpy as np
import torch
from datasets import Dataset
from faiss import METRIC_INNER_PRODUCT
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from ..shared.metrics import (
    ClassificationMetrics,
    RegressionMetrics,
    calculate_classification_metrics,
    calculate_regression_metrics,
)
from ..torch_layers.classification_heads import NearestMemoriesClassificationHead
from ..torch_layers.regression_heads import NearestMemoriesRegressionHead
from ..utils.dataset import parse_dataset
from ..utils.progress import OnProgressCallback, safely_call_on_progress
from ..utils.pydantic import Vector
from .embedding_models import EmbeddingModel


@overload
def evaluate_embedding_model(
    embedding_model: EmbeddingModel,
    memory_dataset: Dataset,
    *,
    sample: int | float | None = None,
    eval_dataset: Dataset | None = None,
    value_column: str = "value",
    label_column: str,
    score_column: None = None,
    neighbor_count: int = 5,
    batch_size: int = 32,
    weigh_memories: bool = True,
    show_progress_bar: bool = True,
    on_progress: OnProgressCallback | None = None,
) -> ClassificationMetrics:
    pass


@overload
def evaluate_embedding_model(
    embedding_model: EmbeddingModel,
    memory_dataset: Dataset,
    *,
    sample: int | float | None = None,
    eval_dataset: Dataset | None = None,
    value_column: str = "value",
    label_column: None = None,
    score_column: str,
    neighbor_count: int = 5,
    batch_size: int = 32,
    weigh_memories: bool = True,
    show_progress_bar: bool = True,
    on_progress: OnProgressCallback | None = None,
) -> RegressionMetrics:
    pass


@overload
def evaluate_embedding_model(
    embedding_model: EmbeddingModel,
    memory_dataset: Dataset,
    *,
    sample: int | float | None = None,
    eval_dataset: Dataset | None = None,
    value_column: str = "value",
    label_column: str | None = None,
    score_column: str | None = None,
    neighbor_count: int = 5,
    batch_size: int = 32,
    weigh_memories: bool = True,
    show_progress_bar: bool = True,
    on_progress: OnProgressCallback | None = None,
) -> ClassificationMetrics | RegressionMetrics:
    pass


def evaluate_embedding_model(
    embedding_model: EmbeddingModel,
    memory_dataset: Dataset,
    *,
    sample: int | float | None = None,
    eval_dataset: Dataset | None = None,
    value_column: str = "value",
    label_column: str | None = None,
    score_column: str | None = None,
    neighbor_count: int = 5,
    batch_size: int = 32,
    weigh_memories: bool = True,
    show_progress_bar: bool = True,
    on_progress: OnProgressCallback | None = None,
) -> ClassificationMetrics | RegressionMetrics:
    """
    Evaluate the performance of an embedding model as a KNN classifier or regressor.

    Warning:
        This method is intended for small datasets, make sure to subsample your dataset. For a
        more scalable approach, create a proper memoryset and RAC model instead.

    Notes:
        This method does not rely on infrastrucutre for memorysets. It instead computes embeddings
        internally and uses FAISS with a flat index (i.e. not ANN) to compute nearest neighbors.

    Args:
        embedding_model: embedding model to evaluate
        memory_dataset: dataset containing the memories for the KNN classifier/regressor
        sample: if provided, subsample the memory_dataset to this number or percentage of rows
        eval_dataset: Optional dataset to evaluate the KNN classifier/regressor on, if not provided a random
            20% subset of the memory_dataset will be split off for evaluation
        value_column: column containing the values to embed
        label_column: column containing the labels (for classification mode)
        score_column: column containing the scores (for regression mode)
        neighbor_count: number of neighbors to use for the KNN classifier/regressor
        batch_size: batch size for the dataloader
        weigh_memories: whether to weigh the memories by their lookup scores
        show_progress_bar: whether to show a progress bar for the evaluation
        on_progress: callback function that is called to report the progress of the evaluation
    """
    if label_column is not None and score_column is not None:
        raise ValueError("Cannot provide both label_column and score_column. Please provide only one.")
    if label_column is None and score_column is None:
        raise ValueError("Must provide either label_column for classification or score_column for regression.")

    mode = "classification" if label_column is not None else "regression"

    memory_dataset = parse_dataset(
        memory_dataset,
        value_column=value_column,
        label_column=label_column,
        score_column=score_column,
        sample=sample,
    )

    # if no eval dataset is provided, split a 20% random subset off the memory_dataset for evaluation
    if eval_dataset is not None:
        eval_dataset = parse_dataset(
            eval_dataset, value_column=value_column, label_column=label_column, score_column=score_column
        )
    else:
        split_dataset = memory_dataset.train_test_split(
            0.2, shuffle=True, seed=42, stratify_by_column="label" if mode == "classification" else None
        )
        eval_dataset = split_dataset["test"]
        memory_dataset = split_dataset["train"]

    total_steps = len(memory_dataset) // batch_size + len(eval_dataset) // batch_size
    current_step = 0

    # create a pseudo memoryset by adding a faiss index to the memory dataset
    context = embedding_model.compute_context(memory_dataset["value"]) if embedding_model.uses_context else None

    def embed_batch(batch: dict):
        nonlocal current_step
        safely_call_on_progress(on_progress, current_step, total_steps)
        current_step += 1
        return {"embedding": embedding_model.embed(batch["value"], prompt="document", context=context)}

    # uses flat index (i.e. not ANN) by default, we could pass a custom index like HNSW (but it would need to be trained first)
    embedded_memory_dataset = memory_dataset.map(embed_batch, batched=True, batch_size=batch_size).add_faiss_index(
        column="embedding", metric_type=METRIC_INNER_PRODUCT
    )

    # instantiate the appropriate head based on mode
    match mode:
        case "classification":
            num_classes = len(set(memory_dataset["label"]))
            head = NearestMemoriesClassificationHead(num_classes, weigh_memories=weigh_memories)
        case "regression":
            head = NearestMemoriesRegressionHead(weigh_memories=weigh_memories)

    # create a collator that computes the nearest neighbors for a batch of values
    def memory_lookup_collator(batch: list[dict]):
        values = [item["value"] for item in batch]
        embeddings = embedding_model.embed(values, prompt="query", context=context)

        memory_weights = []
        memory_targets = []
        memory_embeddings = []
        for embedding in embeddings:
            scores, neighbors = embedded_memory_dataset.get_nearest_examples("embedding", embedding, k=neighbor_count)
            memory_weights.append(scores)
            memory_targets.append(
                neighbors["label" if mode == "classification" else "score"]
            )  # Use the appropriate column name
            memory_embeddings.append(neighbors["embedding"])

        match mode:
            case "classification":
                return {
                    "input_embeddings": torch.tensor(np.stack(embeddings)),
                    "memories_labels": torch.tensor(memory_targets),
                    "memories_weights": torch.tensor(np.stack(memory_weights)),
                    "memories_embeddings": torch.tensor(np.stack(memory_embeddings)),
                    "labels": torch.tensor([item["label"] for item in batch]),
                }
            case "regression":
                return {
                    "input_embeddings": torch.tensor(np.stack(embeddings)),
                    "memories_scores": torch.tensor(memory_targets, dtype=torch.float),
                    "memories_weights": torch.tensor(np.stack(memory_weights)),
                    "memories_embeddings": torch.tensor(np.stack(memory_embeddings)),
                    "scores": torch.tensor([item["score"] for item in batch], dtype=torch.float),
                }

    # compute the predictions
    predictions: list[Vector] = []
    targets_list: list[float] = []

    for batch in tqdm(
        DataLoader(eval_dataset, batch_size=batch_size, collate_fn=memory_lookup_collator),  # type: ignore
        disable=not show_progress_bar,
    ):
        safely_call_on_progress(on_progress, current_step, total_steps)
        current_step += 1
        match mode:
            case "classification":
                logits_batch = head(
                    input_embeddings=batch["input_embeddings"],
                    memories_weights=batch["memories_weights"],
                    memories_labels=batch["memories_labels"],
                    memories_embeddings=batch["memories_embeddings"],
                )
                predictions.extend([np.array(logit) for logit in logits_batch])
                targets_list.extend(batch["labels"].tolist())
            case "regression":
                scores_batch = head(
                    input_embeddings=batch["input_embeddings"],
                    memories_weights=batch["memories_weights"],
                    memories_scores=batch["memories_scores"],
                    memories_embeddings=batch["memories_embeddings"],
                )
                predictions.extend(scores_batch.tolist())
                targets_list.extend(batch["scores"].tolist())

    # calculate metrics based on mode
    match mode:
        case "classification":
            metrics = calculate_classification_metrics(
                expected_labels=[int(label) for label in targets_list],
                logits=predictions,
            )
        case "regression":
            metrics = calculate_regression_metrics(
                expected_scores=targets_list,
                predicted_scores=[float(score) for score in predictions],
            )

    safely_call_on_progress(on_progress, current_step, total_steps)
    return metrics
