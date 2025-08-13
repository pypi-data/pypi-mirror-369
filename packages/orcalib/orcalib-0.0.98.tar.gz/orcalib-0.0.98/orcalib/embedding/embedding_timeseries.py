from __future__ import annotations

import logging
import os
from typing import Literal

import numpy as np
import torch
from datasets import Dataset
from numpy.typing import NDArray
from tqdm.auto import tqdm
from transformers import AutoConfig
from transformers.configuration_utils import PretrainedConfig
from transformers.training_args import TrainingArguments
from ts2vec import TS2Vec

from ..utils.dataset import parse_dataset
from ..utils.fs import dir_context
from ..utils.progress import OnLogCallback, OnProgressCallback
from ..utils.pydantic import Timeseries, Vector


class TS2VecConfig(PretrainedConfig):
    model_type = "ts2vec"

    num_features: int = 1
    embedding_dim: int = 320
    hidden_dim: int = 64
    num_hidden_layers: int = 10
    max_seq_length: int = 0
    temporal_unit: int = 0


AutoConfig.register("ts2vec", TS2VecConfig)


class TimeseriesEmbeddingTrainingArguments(TrainingArguments):
    def __init__(
        self,
        per_device_train_batch_size: int = 16,
        num_train_epochs: int = 2,
        max_steps: int = -1,
        save_strategy: Literal["epoch", "no"] = "epoch",
        learning_rate: float = 0.001,
    ):
        super().__init__(
            "",
            per_device_train_batch_size=per_device_train_batch_size,
            num_train_epochs=num_train_epochs,
            max_steps=max_steps,
            learning_rate=learning_rate,
            save_strategy=save_strategy,
        )


class TimeseriesEmbeddingGenerator:
    def __init__(
        self,
        config: TS2VecConfig | None = None,
        **kwargs,
    ):
        self.config = config or TS2VecConfig(**kwargs)
        self.max_seq_length = self.config.max_seq_length
        self.model = TS2Vec(
            input_dims=self.config.num_features,
            output_dims=self.config.embedding_dim,
            hidden_dims=self.config.hidden_dim,
            depth=self.config.num_hidden_layers,
            temporal_unit=self.config.temporal_unit,
            device="cuda" if torch.cuda.is_available() else "cpu",  # TS2VEC does not support MPS
            max_train_length=None,  # we don't want to chunk the data but truncate it instead
        )

    def _pad_and_truncate(self, timeseries: list[Timeseries], max_seq_length: int) -> np.ndarray:
        for i, t in enumerate(timeseries):
            if t.shape[1] != self.config.num_features:
                raise ValueError(
                    f"Received timeseries with {t.shape[1]} features, expected {self.config.num_features}."
                )
            if t.shape[0] > max_seq_length:
                timeseries[i] = t[:max_seq_length]
            elif t.shape[0] < max_seq_length:
                timeseries[i] = np.vstack(
                    [t, np.full((max_seq_length - t.shape[0], t.shape[1]), np.nan, dtype=t.dtype)]
                )
        return np.array(timeseries)

    def encode(
        self,
        values: list[Timeseries],
        normalize_embeddings: bool = True,
        batch_size: int = 32,
    ) -> list[Vector]:
        embeddings: NDArray[np.float32] = self.model.encode(
            self._pad_and_truncate(values, self.max_seq_length or max(v.shape[0] for v in values)),
            encoding_window="full_series",
            batch_size=batch_size,
        )
        assert len(embeddings.shape) == 2 and embeddings.shape[0] == len(values)
        if normalize_embeddings:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return [e for e in embeddings]

    @classmethod
    def from_pretrained(cls, path: str) -> TimeseriesEmbeddingGenerator:
        with dir_context(path, "read") as location:
            config = AutoConfig.from_pretrained(location)
            instance = cls(config)
            instance.model.load(os.path.join(location, "model.pth"))
            return instance

    def save_pretrained(self, path: str) -> None:
        with dir_context(path, "write") as location:
            self.config.save_pretrained(location)
            self.model.save(os.path.join(location, "model.pth"))

    def train(
        self,
        *,
        save_dir: str | None = None,
        train_dataset: Dataset,
        eval_dataset: Dataset | None = None,
        value_column: str = "value",
        training_args: TimeseriesEmbeddingTrainingArguments | None = None,
        on_progress: OnProgressCallback | None = None,
        on_log: OnLogCallback | None = None,
    ) -> None:
        training_args = training_args or TimeseriesEmbeddingTrainingArguments()
        train_dataset = parse_dataset(train_dataset, value_column=value_column)
        train_data = self._pad_and_truncate(
            list(train_dataset["value"]), self.max_seq_length or max(v.shape[0] for v in train_dataset["value"])
        )

        if eval_dataset is not None:
            logging.warning("Eval dataset is not supported for timeseries embedding models yet")
            # TODO: enable evals, this will require reverse engineering the TS2VEC internals,
            # since ts2vec does not have a forward method to enable computing eval loss

        if save_dir is not None:
            with dir_context(save_dir, "write") as location:
                self.config.save_pretrained(location)

        def epoch_callback(model, _):
            if save_dir is not None and training_args.save_strategy == "epoch":
                with dir_context(
                    os.path.join(save_dir, f"checkpoint-{model.n_iters}"), "write", create=True
                ) as location:
                    self.model.save(os.path.join(location, "model.pth"))

        steps_total = (
            training_args.max_steps
            if training_args.max_steps > 0
            else training_args.num_train_epochs * len(train_data) // training_args.per_device_train_batch_size
        )
        pbar = tqdm(total=(steps_total))

        def step_callback(model, loss):
            pbar.update(1)
            if on_progress:
                on_progress(model.n_iters, model.n_epochs)
            if on_log:
                on_log({"loss": loss})

        self.model.after_iter_callback = step_callback
        self.model.after_epoch_callback = epoch_callback
        self.model.lr = training_args.learning_rate
        self.model.batch_size = training_args.per_device_train_batch_size
        self.model.fit(
            train_data,
            n_epochs=training_args.num_train_epochs,
            n_iters=training_args.max_steps if training_args.max_steps > 0 else None,
            verbose=False,
        )
        pbar.update(steps_total - pbar.n)
        pbar.close()
        if save_dir is not None:
            self.save_pretrained(save_dir)
