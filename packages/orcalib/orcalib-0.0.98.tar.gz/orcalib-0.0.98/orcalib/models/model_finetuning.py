from dataclasses import asdict
from tempfile import TemporaryDirectory
from typing import Any, Literal

import torch
from datasets import Dataset
from torch import nn
from transformers.trainer import Trainer
from transformers.trainer_utils import EvalPrediction
from transformers.training_args import TrainingArguments

from ..memoryset import Memoryset, MemoryType
from ..shared.metrics import (
    calculate_classification_metrics,
    calculate_regression_metrics,
    transform_eval_pred,
)
from ..utils.fs import is_using_blob_storage, upload_dir
from ..utils.trainer import (
    LoggingCallback,
    OnLogCallback,
    OnProgressCallback,
    ProgressCallback,
    optional_callbacks,
)
from .base_model import MemoryAugmentedModel, MemoryAugmentedModelInput


class MemoryAugmentedTrainingArguments(TrainingArguments):
    """Training arguments for finetuning a memory augmented models."""

    def __init__(
        self,
        output_dir: None = None,
        per_device_train_batch_size: int = 32,
        per_device_eval_batch_size: int = 32,
        gradient_accumulation_steps: int = 1,
        num_train_epochs: int = 1,
        eval_strategy: str = "epoch",
        save_strategy: str = "epoch",
        logging_steps: int = 5,
        warmup_steps: int = 10,
        label_names: list[str] = ["labels"],
        compute_lookups_first: bool = False,
        remove_unused_columns: bool = False,  # this is needed for the memory lookup collator
        **kwargs,
    ):
        """
        Initialize training arguments for finetuning a RAC model.

        Note:
            This class extends HuggingFace's [`TrainingArguments`][transformers.TrainingArguments],
            with sensible defaults and additional arguments for finetuning RAC models.
            For documentation of all available arguments, see that class.

        Args:
            output_dir: Do not set this, pass it as the first argument to the finetune method instead.
            compute_lookups_first: whether to pre-compute lookups for the training and evaluation datasets
        """
        if output_dir is not None:
            raise ValueError(
                "output_dir of training_args must not be set. Pass it as the first argument to the finetune method instead."
            )
        super().__init__(
            output_dir="/dev/null",
            per_device_train_batch_size=per_device_train_batch_size,
            per_device_eval_batch_size=per_device_eval_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            num_train_epochs=num_train_epochs,
            eval_strategy=eval_strategy,
            save_strategy=save_strategy,
            logging_steps=logging_steps,
            warmup_steps=warmup_steps,
            label_names=label_names,
            remove_unused_columns=remove_unused_columns,
            **kwargs,
        )
        self.compute_lookups_first = compute_lookups_first


class MemoryLookupDataCollator:
    def __init__(self, memoryset: Memoryset[MemoryType], memory_lookup_count: int):
        self.memoryset = memoryset
        self.memory_lookup_count = memory_lookup_count

    def __call__(self, batch: list[dict[str, Any]]) -> MemoryAugmentedModelInput:
        input_values = [s["value"] for s in batch]
        lookup_results = self.memoryset.lookup(input_values, count=self.memory_lookup_count, return_type="columns")
        if self.memoryset.memory_type == "labeled":
            labels = torch.tensor([s["label"] for s in batch])
            assert "memories_labels" in lookup_results
            memories_labels = torch.tensor(lookup_results["memories_labels"])
        elif self.memoryset.memory_type == "scored":
            labels = torch.tensor([s["score"] for s in batch])
            assert "memories_scores" in lookup_results
            memories_labels = torch.tensor(lookup_results["memories_scores"])
        else:
            raise ValueError(f"Memory type {self.memoryset.memory_type} not supported")
        return MemoryAugmentedModelInput(
            input_embeddings=torch.tensor(lookup_results["input_embeddings"]),
            memories_labels=memories_labels,
            memories_embeddings=torch.tensor(lookup_results["memories_embeddings"]),
            memories_weights=torch.tensor(lookup_results["memories_lookup_scores"]),
            labels=labels,
        )


def finetune(
    model: MemoryAugmentedModel,
    checkpoint_dir: str | None,
    train_dataset: Dataset,
    eval_dataset: Dataset | None = None,
    training_args: MemoryAugmentedTrainingArguments = MemoryAugmentedTrainingArguments(),
    on_progress: OnProgressCallback | None = None,
    on_log: OnLogCallback | None = None,
):
    assert isinstance(model, nn.Module)
    if checkpoint_dir is None:
        temp_dir = TemporaryDirectory()
        training_args.save_strategy = "no"
        training_args.output_dir = temp_dir.name
    elif is_using_blob_storage(checkpoint_dir):
        temp_dir = TemporaryDirectory()
        training_args.output_dir = temp_dir.name
    else:
        temp_dir = None
        training_args.output_dir = checkpoint_dir

    if training_args.compute_lookups_first:
        train_dataset = train_dataset.map(
            lambda batch: model.memoryset.lookup(
                batch["value"], count=model.memory_lookup_count, return_type="columns", use_cache=False
            ),
            batched=True,
            batch_size=training_args.per_device_train_batch_size,
        )
        if eval_dataset is not None:
            eval_dataset = eval_dataset.map(
                lambda batch: model.memoryset.lookup(
                    batch["value"], count=model.memory_lookup_count, return_type="columns", use_cache=False
                ),
                batched=True,
                batch_size=training_args.per_device_eval_batch_size,
            )

    def compute_metrics(eval_pred: EvalPrediction) -> dict[str, float]:
        references, logits = transform_eval_pred(eval_pred)
        if model.memoryset.memory_type == "labeled":
            return asdict(calculate_classification_metrics(references, logits))
        elif model.memoryset.memory_type == "scored":
            return asdict(calculate_regression_metrics(references, logits))
        else:
            raise ValueError(f"Memory type {model.memoryset.memory_type} not supported")

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
        data_collator=(
            MemoryLookupDataCollator(model.memoryset, model.memory_lookup_count)
            if not training_args.compute_lookups_first
            else None
        ),
        callbacks=optional_callbacks(
            ProgressCallback(on_progress, "train") if on_progress else None,
            LoggingCallback(on_log) if on_log else None,
        ),
    )

    try:
        trainer.train()
    finally:
        if temp_dir is not None:
            if checkpoint_dir:
                upload_dir(temp_dir.name, checkpoint_dir, recursive=True)
            temp_dir.cleanup()
