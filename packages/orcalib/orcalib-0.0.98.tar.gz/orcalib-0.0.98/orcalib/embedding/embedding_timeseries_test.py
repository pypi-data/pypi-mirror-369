import math
import os
from random import random
from tempfile import TemporaryDirectory
from typing import Callable

import numpy as np
import pytest
from datasets import Dataset

from ..utils.pydantic import Timeseries
from .embedding_timeseries import (
    TimeseriesEmbeddingGenerator,
    TimeseriesEmbeddingTrainingArguments,
)


def make_timeseries(fn: Callable[[float], float], n: int = 20) -> Timeseries:
    return np.array([[fn(2 * math.pi * i / n) + random() / 2] for i in range(n)])


def compute_similarity(model: TimeseriesEmbeddingGenerator, ts1: Timeseries, ts2: Timeseries) -> float:
    return float(np.dot(model.encode([ts1])[0], model.encode([ts2])[0]))


def test_encode_timeseries():
    # Given a timeseries embedding model
    model = TimeseriesEmbeddingGenerator(num_features=1, embedding_dim=10, max_seq_length=20)
    # When we encode a few timeseries
    embeddings = model.encode([make_timeseries(math.sin), make_timeseries(math.cos)])
    # Then embedding of the correct shape are returned
    assert embeddings is not None
    assert len(embeddings) == 2
    assert embeddings[0].shape == (10,)
    assert embeddings[1].shape == (10,)
    # And the embeddings are normalized
    assert np.allclose(np.linalg.norm(embeddings[0]), 1)
    assert np.allclose(np.linalg.norm(embeddings[1]), 1)


def test_encode_timeseries_wrong_num_features():
    # Given a timeseries embedding model
    model = TimeseriesEmbeddingGenerator(num_features=2)
    # When we encode a timeseries with the wrong number of features
    with pytest.raises(ValueError):
        model.encode([make_timeseries(math.sin)])


def test_train_timeseries_embedder(temp_dir):
    # Given a dataset with timeseries of two different shapes
    fn1, fn2 = math.sin, lambda x: x
    dataset = Dataset.from_dict({"value": [make_timeseries(fn1), make_timeseries(fn2)] * 32, "label": [0, 1] * 32})
    # And an untrained timeseries embedding model
    model = TimeseriesEmbeddingGenerator(num_features=1, embedding_dim=32, max_seq_length=20)
    untrained_similarity = compute_similarity(model, make_timeseries(fn1), make_timeseries(fn2))
    # When we train the model
    batch_size = 8
    num_epochs = 2
    model.train(
        save_dir=temp_dir,
        train_dataset=dataset,
        value_column="value",
        training_args=TimeseriesEmbeddingTrainingArguments(
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
        ),
    )
    # Then the trained model config and model weights are saved
    assert os.path.exists(os.path.join(temp_dir, "config.json"))
    assert os.path.exists(os.path.join(temp_dir, "model.pth"))
    # And checkpoints are saved
    for i in [(e + 1) * dataset.num_rows // batch_size for e in range(num_epochs)]:
        assert os.path.exists(os.path.join(temp_dir, f"checkpoint-{i}", "model.pth"))
    # And the trained model creates embeddings that are more differentiated between the two types of timeseries
    trained_similarity = compute_similarity(model, make_timeseries(fn1), make_timeseries(fn2))
    assert trained_similarity < untrained_similarity
