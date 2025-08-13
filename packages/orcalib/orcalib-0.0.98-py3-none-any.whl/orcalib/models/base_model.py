from __future__ import annotations

import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import NotRequired, Self, TypedDict, Unpack, cast

import numpy as np
from torch import Tensor
from transformers.configuration_utils import PretrainedConfig
from transformers.modeling_outputs import SequenceClassifierOutput
from transformers.modeling_utils import PreTrainedModel

from ..memoryset import MemoryLookupColumnResult, Memoryset
from ..utils import dir_context, exists_dir, is_using_blob_storage


class MemoryAugmentedModelInput(TypedDict):
    input_embeddings: Tensor | None
    memories_labels: Tensor | None
    memories_embeddings: Tensor | None
    memories_weights: Tensor | None
    labels: NotRequired[Tensor | None]


class MemoryAugmentedModel(PreTrainedModel, ABC):
    """A retrieval augmented model that uses a memoryset to make predictions."""

    config_class = PretrainedConfig
    base_model_prefix: str
    memory_lookup_count: int
    memoryset: Memoryset

    @property
    def num_trainable_parameters(self) -> int:
        """Number of trainable parameters in the model"""
        return self.num_parameters(only_trainable=True)

    @abstractmethod
    def reset(self) -> None:
        """Reset the model weights to their initial state"""
        raise NotImplementedError

    @abstractmethod
    def forward(
        self,
        **kwargs: Unpack[MemoryAugmentedModelInput],
    ) -> SequenceClassifierOutput:
        raise NotImplementedError

    def attach(self, memoryset: Memoryset | str):
        """
        Attach a memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset
        """
        self.memoryset = memoryset if isinstance(memoryset, Memoryset) else Memoryset.connect(memoryset)

    def use(self, memoryset: Memoryset | str):
        """
        Temporarily attach a different memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset

        Examples:
            with model.use(memoryset):
                model.predict("test input")
        """

        @contextmanager
        def ctx_manager():
            previous_memoryset = self.memoryset
            try:
                self.attach(memoryset)
                yield
            finally:
                if previous_memoryset:
                    self.attach(previous_memoryset)

        return ctx_manager()

    @staticmethod
    def estimate_anomaly_score(
        lookup_res: MemoryLookupColumnResult,
        idx: int,
    ) -> float:
        # Get index of memory with highest lookup score for this prediction
        memory_lookup_scores = lookup_res["memories_lookup_scores"][idx]
        if memory_lookup_scores.size == 0:
            return 1.0

        max_score_idx = np.argmax(memory_lookup_scores)

        # Get input embedding and corresponding top memory embedding
        input_emb = lookup_res["input_embeddings"][idx]
        top_memory_emb = lookup_res["memories_embeddings"][idx][max_score_idx]

        # Compute inner product between input and top memory embedding
        input_memory_similarity = float(np.inner(input_emb, top_memory_emb))

        if input_memory_similarity < 0:
            return 1.0
        else:
            return 1.0 - input_memory_similarity

    def save_pretrained(self, save_directory: str, **kwargs):  # type: ignore
        """
        Save the model to a local or remote directory

        Args:
            save_directory: The directory to save the model to

        Examples:
            model.save_pretrained("./temp/my-model)
            model.save_pretrained("gs:/orca-internal/models/my-model")
        """
        with dir_context(save_directory, "write") as location:
            return super().save_pretrained(location, **kwargs)

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str) -> Self:
        """
        Load the model from a local or remote directory

        Args:
            pretrained_model_name_or_path: The directory to load the model from

        Returns:
            The loaded model

        Examples:
            model = RACModel.from_pretrained("./temp/my-model")
            model = RACModel.from_pretrained("gs:/orca-internal/models/my-model")
        """
        with dir_context(pretrained_model_name_or_path, "read") as location:
            return cast(Self, super().from_pretrained(location))

    @classmethod
    def exists(cls, pretrained_model_path: str) -> bool:
        """
        Check if a pretrained model exists at a given path

        Args:
            pretrained_model_path: The path to the pretrained model

        Returns:
            `True` if the pretrained model exists, `False` otherwise
        """
        if is_using_blob_storage(pretrained_model_path):
            return exists_dir(pretrained_model_path)
        else:
            return os.path.exists(pretrained_model_path)
