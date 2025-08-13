from __future__ import annotations

from collections import Counter
from functools import partial
from typing import cast

import torch
import torch.nn as nn
import torch.nn.functional as F
from datasets import Dataset
from sentence_transformers import SentenceTransformer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from transformers.trainer import Trainer

from ..utils.trainer import (
    LoggingCallback,
    OnLogCallback,
    OnProgressCallback,
    ProgressCallback,
    optional_callbacks,
)
from .embedding_finetuning import EmbeddingTrainingArguments


def initialize_proxies(
    train_dataset: Dataset, model: SentenceTransformer, num_classes: int, embedding_dim: int, batch_size: int = 32
):
    """
    Initialize class proxies by computing the mean embedding for each class in the training dataset.
    """
    proxies = torch.zeros(num_classes, embedding_dim, dtype=torch.float32, device=model.device)
    class_counts = torch.zeros(num_classes, dtype=torch.float32, device=model.device)

    dataloader = DataLoader(
        train_dataset,  # type: ignore -- data loader has bad types
        batch_size=batch_size,
        shuffle=False,
    )

    for batch in tqdm(dataloader, desc="Computing class proxies", unit="batch", leave=False):
        texts = batch["value"]
        labels = torch.tensor(batch["label"], dtype=torch.long, device=model.device)

        embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
        proxies.index_add_(0, labels, embeddings)
        class_counts.index_add_(0, labels, torch.ones_like(labels, dtype=torch.float32))

    proxies /= class_counts.unsqueeze(1)

    proxies = F.normalize(proxies, p=2, dim=1)
    return nn.Parameter(proxies)


class ProxyNCALoss(nn.Module):
    """
    ProxyNCA loss function for training with proxies.

    This loss is computed as the cross-entropy between the pairwise distances of the embeddings and proxies.
    The closer the embeddings are to the correct proxy, the lower the loss.
    """

    def __init__(self, proxies: nn.Parameter, scale: float = 30.0):
        super().__init__()
        self.proxies = proxies
        self.scale = scale

    def forward(self, embeddings: torch.Tensor, labels: torch.Tensor):
        # Normalize embeddings and proxies
        embeddings = F.normalize(embeddings, p=2, dim=1)
        proxies = F.normalize(self.proxies, p=2, dim=1)

        # Compute distances between embeddings and proxies
        similarity = torch.matmul(embeddings, proxies.T)  # Pairwise distances
        logits = self.scale * similarity  # Scale distances for softmax
        loss = F.cross_entropy(logits, labels)
        return loss


class ProxyNCAWrapper(nn.Module):
    """
    When fine tuning with proxy loss, we need to wrap the SentenceTransformer model with a logistic regression head
    to predict the class labels. This model will output the embeddings and compute the proxy loss using the
    trained proxies.
    """

    def __init__(
        self, model_name: str, num_classes: int, embedding_dim: int, proxies: nn.Parameter, scale: float = 30.0
    ):
        super().__init__()
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
        self.proxy_loss = ProxyNCALoss(proxies, scale)
        self.num_classes = num_classes
        self.embedding_dim = embedding_dim

    def forward(self, value: list[str], label: torch.Tensor | None = None):
        embeddings = self.model.encode(value, convert_to_tensor=True, show_progress_bar=False)
        if label is not None:
            loss = self.proxy_loss(embeddings, label)
            # embeddings are being returned as "logits" to make sure they are included in inputs to compute_proxy_metrics
            return {"loss": loss, "logits": embeddings}
        return {"logits": embeddings}


def proxy_collate_fn(batch):
    """
    Data collator for proxy-based training. This collator will group samples into batches and return the text values
    """
    texts = [item["value"] for item in batch]
    labels = torch.tensor([item["label"] for item in batch], dtype=torch.long)
    return {"value": texts, "label": labels}


def compute_proxy_metrics(eval_pred, proxies: nn.Parameter):
    """
    Compute classification metrics for proxy-based training.
    """
    embeddings = eval_pred.predictions
    labels = eval_pred.label_ids

    similarities = torch.mm(torch.tensor(embeddings).to(proxies.device), proxies.T)  # shape: (batch_size, num_classes)
    predictions = torch.argmax(similarities, dim=1).cpu().numpy()

    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="weighted")
    accuracy = accuracy_score(labels, predictions)

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1}


def create_weighted_sampler(train_dataset: Dataset):
    """
    Determines the class weights for each sample in the training dataset based on their frequency
    and creates a weighted sampler.
    """
    class_counts = Counter(train_dataset["label"])
    total_samples = len(train_dataset)
    class_weights = [total_samples / count for label, count in class_counts.items()]

    sample_weights = [class_weights[label] for label in train_dataset["label"]]
    return torch.utils.data.WeightedRandomSampler(sample_weights, len(train_dataset))


class ProxyTrainer(Trainer):
    """
    Specialized Trainer for training with the ProxyNCA loss function. This is required to handle the custom loss
    function and data collator.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_train_dataloader(self):
        dataset = self.train_dataset
        if not isinstance(dataset, Dataset):
            raise ValueError(f"train_dataset must be a Dataset, got {type(dataset)}")
        return DataLoader(
            self.train_dataset,  # type: ignore -- data loader has bad types
            batch_size=self.args.per_device_train_batch_size,
            collate_fn=self.data_collator,
            sampler=create_weighted_sampler(dataset),
        )


def finetune_with_proxy_loss(
    base_model_name: str,
    output_dir: str,
    train_dataset: Dataset,
    eval_dataset: Dataset,
    training_args: EmbeddingTrainingArguments = EmbeddingTrainingArguments.for_triplet_loss(),
    on_progress: OnProgressCallback | None = None,
    on_log: OnLogCallback | None = None,
) -> None:
    """
    Finetune the embedding model using the ProxyNCA loss function. This will save the finetuned model and any
    checkpoints to the provided output directory.

    Args:
        base_model_name: name of the base model to finetune
        output_dir: the directory to save the finetuned model to
        train_dataset: the dataset to use for training, must contain "value" and "label" features
        eval_dataset: the dataset to use for evaluation, must contain "value" and "label" features
        training_args: training arguments to use, if not given a default will be used
        on_progress: callback to call with progress updates
        on_log: callback to call with log messages
    """

    try:
        model = SentenceTransformer(base_model_name, trust_remote_code=True)
    except Exception as e:
        raise ValueError(
            "Proxy-based finetuning only works with models that are compatible with SentenceTransformer", e
        )

    training_args.output_dir = output_dir
    training_args.prediction_loss_only = False

    if (train_dataset.features["value"].dtype != "string" or "label" not in train_dataset.features) or (
        eval_dataset is not None
        and (eval_dataset.features["value"].dtype != "string" or "label" not in eval_dataset.features)
    ):
        raise ValueError("fine tuning is only supported for text samples with labels")

    embedding_dim = model.get_sentence_embedding_dimension()
    assert embedding_dim is not None
    num_labels = len(set(train_dataset["label"]))
    proxies = initialize_proxies(train_dataset, model, num_labels, embedding_dim)
    proxy_model = ProxyNCAWrapper(base_model_name, num_labels, embedding_dim, proxies)

    trainer = ProxyTrainer(
        model=proxy_model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=partial(compute_proxy_metrics, proxies=proxies),
        data_collator=proxy_collate_fn,
        callbacks=optional_callbacks(
            ProgressCallback(on_progress, "train") if on_progress else None,
            LoggingCallback(on_log) if on_log else None,
        ),
    )

    trainer.train()

    model.save(output_dir)
