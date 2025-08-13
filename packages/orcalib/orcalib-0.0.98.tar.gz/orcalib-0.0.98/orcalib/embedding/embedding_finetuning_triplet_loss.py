from collections import Counter, defaultdict
from typing import Any, Iterable, cast

import numpy as np
from datasets import Dataset
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

from ..utils.trainer import OnLogCallback, OnProgressCallback
from .embedding_finetuning import EmbeddingTrainingArguments


class _TripletSampler:
    """Helper class to sample negative examples for triplet loss

    NOTE: This is a helper class that is not meant to be used directly.

    TODO: Expand this class to support hard negative mining and other strategies
    """

    dataset: Dataset
    """The number of classes in the dataset"""
    class_count: int
    """The number of samples for each class"""
    class_counts: Counter
    """The data grouped by label"""
    data_by_label: defaultdict
    """The number of negative samples for each class"""
    negative_counts: dict[int, int]

    def __init__(self, dataset: Dataset, class_count: int, seed: int = 42):
        self.dataset = dataset
        self.class_count = class_count
        self.class_counts = Counter(dataset["label"])
        self.data_by_label = defaultdict(list)
        self.rng = np.random.default_rng(seed)
        for item in cast(Iterable[dict], dataset):
            self.data_by_label[item["label"]].append(item)

        total_count = len(dataset)

        self.negative_counts = {i: total_count - class_count for i, class_count in self.class_counts.items()}
        pass

    def get_positive_sample(self, label: int, text: str) -> dict[str, Any]:
        """
        Get a random positive (but not identical) sample for a given label

        Args:
            label: The label to get a positive sample for
            text: The text of the sample to find a positive match
        """
        MAX_TRIES = 100
        attempts = 1
        samples = self.data_by_label[label]

        pick = self.rng.choice(samples)
        while pick["value"] == text:
            attempts += 1
            pick = self.rng.choice(samples)
            if attempts > MAX_TRIES:
                raise ValueError(
                    f"Failed to find a non-matching positive sample for label {label} after {MAX_TRIES} tries"
                )

        return pick

    def get_negative_sample(self, label: int) -> dict[str, Any]:
        """
        Get a random negative sample for a given label

        Args:
            label: The label to get a negative sample for
        """
        # We're picking an index as if all the negative classes were in one big list.
        # If we have 3 classes with 10, 20, and 30 samples (60 total), we're picking
        # an index in [0, 60).
        pick = self.rng.integers(0, self.negative_counts[label])

        # We'll look through each other class to see if the current value of pick falls
        # within the range of indexes for that class.
        for i in range(self.class_count):
            if i == label:
                continue  # Skip the given label since we're selecting a negative sample
            if pick < self.class_counts[i]:
                # If the pick falls within this class's sample range, return the corresponding sample
                return self.data_by_label[i][pick]

            # Adjust pick to account for the samples we've passed (all the ones in the current class)
            pick -= self.class_counts[i]

        raise ValueError(f"Failed to find a negative sample for label {label}")

    def create_triplets(self) -> list[InputExample]:
        """Create triplets from a dataset

        Args:
            dataset: The dataset to create triplets from
            class_count: The number of classes in the dataset
        """
        return [
            InputExample(
                texts=[
                    item["value"],
                    self.get_positive_sample(item["label"], item["value"])["value"],
                    self.get_negative_sample(item["label"])["value"],
                ],
                label=item["label"],
            )
            for item in cast(Iterable[dict], self.dataset)
        ]


def finetune_with_triplets(
    base_model_name: str,
    output_dir: str,
    train_dataset: Dataset,
    eval_dataset: Dataset,
    training_args: EmbeddingTrainingArguments | None = None,
    on_progress: OnProgressCallback | None = None,
    on_log: OnLogCallback | None = None,
) -> None:
    """
    Finetune the embedding model via contrastive triplet loss based on labels. This will save the
    finetuned model to the given output directory.

    Args:
        base_model_name: name of the base model to finetune
        output_dir: the directory to save the finetuned model to
        train_dataset: the dataset to use for training, must contain "value" and "label" features
        eval_dataset: the dataset to use for evaluation, must contain "value" and "label" features
        training_args: training arguments to use, if not given a default will be used
        on_progress: callback to call with progress updates
        on_log: callback to call with log messages
    """
    training_args = training_args or EmbeddingTrainingArguments()

    try:
        model = SentenceTransformer(base_model_name, trust_remote_code=True)
    except Exception as e:
        raise ValueError("triplet finetuning only works with models that are compatible with SentenceTransformer", e)

    training_args.output_dir = output_dir
    training_args.prediction_loss_only = False  # reverse sentence transformer training args default

    if (train_dataset.features["value"].dtype != "string" or "label" not in train_dataset.features) or (
        eval_dataset is not None
        and (eval_dataset.features["value"].dtype != "string" or "label" not in eval_dataset.features)
    ):
        raise ValueError("fine tuning is only supported for text samples with labels")

    triplet_sampler = _TripletSampler(train_dataset, len(set(train_dataset["label"])))
    train_triplets = triplet_sampler.create_triplets()

    train_loss = losses.TripletLoss(model, losses.TripletDistanceMetric.COSINE, triplet_margin=0.2)
    train_loader = DataLoader(
        train_triplets,  # type: ignore -- data loader has bad types
        batch_size=training_args.per_device_train_batch_size,
        shuffle=True,
    )

    # NOTE: Because we're using model.fit (which is deprecated), we are limited in the arguments we can pass
    # to the trainer.
    # NOTE: We need to update this to use the Trainer class directly.
    total_steps_count = int(training_args.max_steps or training_args.num_train_epochs * len(train_loader))
    model.fit(
        train_objectives=[(train_loader, train_loss)],
        epochs=int(training_args.num_train_epochs),
        warmup_steps=training_args.warmup_steps,
        output_path=output_dir,
        checkpoint_path=output_dir,
        checkpoint_save_total_limit=2,
        checkpoint_save_steps=50,
        callback=lambda score, epoch, steps: on_progress(steps, total_steps_count) if on_progress else None,
        # # TODO: add back after upgrading to proper sentence transformer training
        # callbacks=optional_callbacks(
        #     ProgressCallback(on_progress, "train") if on_progress else None,
        #     LoggingCallback(on_log) if on_log else None,
        # ),
    )

    model.save(output_dir)
