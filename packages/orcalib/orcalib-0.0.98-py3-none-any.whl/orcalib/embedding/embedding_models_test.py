import base64
import math
import tempfile
from io import BytesIO
from random import random
from time import perf_counter

import numpy as np
import pytest
from datasets import Dataset, DatasetDict
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import AutoConfig

from ..embedding import (
    EmbeddingFinetuningMethod,
    EmbeddingModel,
    EmbeddingTrainingArguments,
)
from ..utils.fs import is_using_blob_storage, list_dir, upload_dir
from .embedding_finetuning_triplet_loss import finetune_with_triplets
from .embedding_timeseries import TimeseriesEmbeddingTrainingArguments
from .finetuning_proxy_loss import finetune_with_proxy_loss


def test_default_embedding_models():
    # When a default embedding model is instantiated
    embedding_model = EmbeddingModel.GTE_BASE
    # Then it has the correct name
    assert embedding_model.path == "OrcaDB/gte-base-en-v1.5"


def test_embedding_model_singleton():
    # Given an embedding model instance
    model_1 = EmbeddingModel.CLIP_BASE
    # When instantiating another embedding model with the same arguments
    model_2 = EmbeddingModel("OrcaDB/clip-ViT-L-14", max_seq_length_override=None)
    # Then the same instance is returned
    assert model_1 is model_2
    assert model_1._embedder is model_2._embedder
    # When instantiating another embedding model with different arguments
    model_3 = EmbeddingModel("OrcaDB/clip-ViT-L-14", max_seq_length_override=15)
    # Then a different instance is returned
    assert model_1 is not model_3


def test_embed_text():
    # When generating embeddings for a single string
    embeddings = EmbeddingModel.GTE_SMALL.embed("Hello, world!")
    # Then a 1-dimensional array of floats is returned
    assert embeddings.shape == (EmbeddingModel.GTE_SMALL.embedding_dim,)
    assert embeddings.dtype == np.float32
    # And the embedding is normalized
    assert np.isclose(np.linalg.norm(embeddings), 1.0)


def test_embed_image():
    # Given an image
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg=="
    image = Image.open(BytesIO(base64.b64decode(base64_image)))
    # When embedding the image
    embeddings = EmbeddingModel.CLIP_BASE.embed(image)
    # Then a 1-dimensional array of floats is returned
    assert embeddings.shape == (768,)
    assert embeddings.dtype == np.float32
    # And the embedding is normalized
    assert np.isclose(np.linalg.norm(embeddings), 1.0)


def test_embed_batch(dataset: Dataset):
    # When generating embeddings for a batch of strings
    embeddings = EmbeddingModel.GTE_BASE.embed(dataset["text"][:30], batch_size=8)
    # Then a list of 1-dimensional arrays of floats is returned
    assert isinstance(embeddings, list)
    assert len(embeddings) == 30
    assert all(e.shape == (EmbeddingModel.GTE_BASE.embedding_dim,) for e in embeddings)
    assert all(e.dtype == np.float32 for e in embeddings)


def test_embedding_model_from_path(location: str, temp_dir: str):
    # Given a saved embedding model
    assert isinstance(EmbeddingModel.CLIP_BASE._embedder, SentenceTransformer)
    if is_using_blob_storage(location):
        EmbeddingModel.CLIP_BASE._embedder.save_pretrained(temp_dir)
        upload_dir(temp_dir, location)
    else:
        EmbeddingModel.CLIP_BASE._embedder.save_pretrained(location)
    # When instantiating the embedding model from the folder
    model = EmbeddingModel(location)
    # Then the model config is loaded from the folder
    assert model.config is not None
    # And the model can embed strings
    embeddings = model.embed(["Hello, world!"])
    assert len(embeddings) == 1
    assert embeddings[0].shape == (768,)
    assert embeddings[0].dtype == np.float32


@pytest.mark.parametrize(
    "base_model_name,expected_embedding_dim",
    [
        ("OrcaDB/gte-base-en-v1.5", 768),
        ("distilbert-base-uncased", 768),
        ("OrcaDB/gte-small", 384),
    ],
)
def test_classification_finetuning(base_model_name, expected_embedding_dim, location, dataset):
    # When finetuning a classification model
    finetuned_model = EmbeddingModel(base_model_name).finetune(
        save_dir=location,
        train_dataset=dataset,
        value_column="text",
        method="classification",
        training_args=EmbeddingTrainingArguments.for_classification(
            max_steps=1,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
        ),
    )
    # Then a finetuned model is returned
    assert finetuned_model is not None
    # And the model can embed strings
    embeddings = finetuned_model.embed(["Hello, world!"])
    assert len(embeddings) == 1
    assert embeddings[0].shape == (expected_embedding_dim,)
    assert embeddings[0].dtype == np.float32
    # And training checkpoints are saved
    files_at_location = list_dir(location)
    assert len(files_at_location) > 0
    assert any("checkpoint" in f for f in files_at_location)


@pytest.mark.parametrize(
    "method,create_training_args",
    [
        (EmbeddingFinetuningMethod.CLASSIFICATION, EmbeddingTrainingArguments.for_classification),
        (EmbeddingFinetuningMethod.BATCH_TRIPLET_LOSS, EmbeddingTrainingArguments.for_triplet_loss),
    ],
)
def test_finetuning_models_multiple_times(dataset: Dataset, method, create_training_args):
    with tempfile.TemporaryDirectory() as temp_dir:
        # When finetuning a classification model
        finetuned_model = EmbeddingModel("OrcaDB/gte-base-en-v1.5").finetune(
            save_dir=temp_dir,
            train_dataset=dataset,
            value_column="text",
            method=method,
            training_args=create_training_args(
                max_steps=1, per_device_train_batch_size=2, per_device_eval_batch_size=2
            ),
        )
        # Then a finetuned model is returned
        assert finetuned_model is not None
        # And the model can embed strings
        embeddings = finetuned_model.embed(["Hello, world!"])
        assert len(embeddings) == 1
        assert embeddings[0].shape == (768,)
        assert embeddings[0].dtype == np.float32
        # And training checkpoints are saved
        files_at_location = list_dir(temp_dir)
        assert len(files_at_location) > 0
        assert any("checkpoint" in f for f in files_at_location)

    with tempfile.TemporaryDirectory() as temp_dir:
        # When finetuning a classification model
        finetuned_model = EmbeddingModel("OrcaDB/gte-base-en-v1.5").finetune(
            save_dir=temp_dir,
            train_dataset=dataset,
            value_column="text",
            method=method,
            training_args=create_training_args(
                max_steps=2, per_device_train_batch_size=2, per_device_eval_batch_size=2
            ),
        )
        # Then a finetuned model is returned
        assert finetuned_model is not None
        # And the model can embed strings
        embeddings = finetuned_model.embed(["Hello, world!"])
        assert len(embeddings) == 1
        assert embeddings[0].shape == (768,)
        assert embeddings[0].dtype == np.float32
        # And training checkpoints are saved
        files_at_location = list_dir(temp_dir)
        assert len(files_at_location) > 0
        assert any("checkpoint" in f for f in files_at_location)


@pytest.mark.parametrize(
    "base_model_name,expected_embedding_dim",
    [
        ("OrcaDB/gte-base-en-v1.5", 768),
        ("distilbert-base-uncased", 768),
        ("OrcaDB/gte-small", 384),
    ],
)
def test_triplet_finetuning(location: str, dataset_dict: DatasetDict, base_model_name, expected_embedding_dim):
    # Given an embedding model with a max sequence length override
    model = EmbeddingModel(base_model_name, max_seq_length_override=15)
    assert model.max_seq_length == 15
    # When finetuning the model with triplets
    finetuned_model = model.finetune(
        save_dir=location,
        train_dataset=dataset_dict["train"],
        eval_dataset=dataset_dict["test"],
        value_column="text",
        method=EmbeddingFinetuningMethod.BATCH_TRIPLET_LOSS,
        training_args=EmbeddingTrainingArguments.for_triplet_loss(
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            max_steps=1,
        ),
    )
    # Then a finetuned model is returned
    assert finetuned_model is not None
    # And the model has the same max sequence length override as the original model
    assert finetuned_model.max_seq_length == 15
    # And the model can embed strings
    embeddings = finetuned_model.embed(["Hello, world!"])
    assert len(embeddings) == 1
    assert embeddings[0].shape == (expected_embedding_dim,)
    assert embeddings[0].dtype == np.float32
    # And training checkpoints are saved
    files_at_location = list_dir(location)
    assert len(files_at_location) > 0
    assert any("checkpoint" in f for f in files_at_location)


@pytest.mark.parametrize(
    "finetune_fn,create_training_args",
    [
        (finetune_with_triplets, EmbeddingTrainingArguments.for_triplet_loss),
        (finetune_with_proxy_loss, EmbeddingTrainingArguments.for_proxy_loss),
    ],
)
def test_experimental_finetuning(temp_dir: str, dataset_dict: DatasetDict, finetune_fn, create_training_args):
    # Given an embedding model with a max sequence length override
    model = EmbeddingModel("distilbert-base-uncased", max_seq_length_override=15)
    assert model.max_seq_length == 15
    # When finetuning the model with triplets
    finetune_fn(
        base_model_name="distilbert-base-uncased",
        output_dir=temp_dir,
        train_dataset=dataset_dict["train"].rename_column("text", "value"),
        eval_dataset=dataset_dict["test"].rename_column("text", "value"),
        training_args=create_training_args(
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            max_steps=10,
        ),
    )
    finetuned_model = EmbeddingModel(temp_dir)
    # Then a finetuned model is returned
    assert finetuned_model is not None
    # And the model can embed strings
    embeddings = finetuned_model.embed(["Hello, world!"])
    assert len(embeddings) == 1
    assert embeddings[0].shape == (768,)
    assert embeddings[0].dtype == np.float32


def test_contextual_embedding_model(dataset: Dataset):
    # Given a contextual embedding model
    model = EmbeddingModel.CDE_SMALL
    # Then we can compute an embedding context
    embedding_context = model.compute_context(dataset["text"])
    assert embedding_context is not None
    assert embedding_context.embeddings.shape == (model.config.transductive_context_length, model.config.embedding_dim)
    assert embedding_context.hash is not None
    # And when we use the context to embed a string
    test_string = "I'm over the moon with how things turned out!"
    embeddings = model.embed([test_string], context=embedding_context)
    # Then a list of 1-dimensional arrays of floats is returned
    assert isinstance(embeddings, list)
    assert len(embeddings) == 1
    assert embeddings[0].shape == (model.embedding_dim,)
    assert embeddings[0].dtype == np.float32
    # And the result is different from the result of a non-contextual embedding
    assert not np.allclose(embeddings, model.embed([test_string]))


def test_embed_caching(dataset: Dataset):
    # Given an embedding model
    model = EmbeddingModel("distilbert-base-uncased", max_seq_length_override=15)
    # When we embed a string
    values = dataset["text"][:4]
    embeddings = model.embed(values, use_cache=True)
    assert len(embeddings) == len(values)
    # Then the results are stored in the cache
    assert len(model._cache) == len(values)
    assert all(model._cache.get(model._get_cache_key(v, None, None)) is not None for v in values)
    # When we embed a subset of those values again with a cached value
    start = perf_counter()
    cached_embeddings = model.embed(values[:2], use_cache=True)
    cached_duration = perf_counter() - start
    # And without a cached value
    model._cache.clear()
    assert len(model._cache) == 0
    start = perf_counter()
    uncached_embeddings = model.embed(
        values[:2], use_cache=True
    )  # Note: we want to use the cache here but without a cached value
    uncached_duration = perf_counter() - start
    # Then the embedding generation is faster when there is a cached value
    assert cached_duration < uncached_duration
    # And the cached results are the same as the uncached results
    assert np.allclose(cached_embeddings, uncached_embeddings, rtol=0.005)


def test_timeseries_embedding_model():
    # Given a timeseries embedding model
    model = EmbeddingModel("ts2vec", max_seq_length_override=0)
    # Then the model can embed a timeseries
    embeddings = model.embed(np.random.randn(20, 1).astype(np.float32))
    assert embeddings.shape == (model.embedding_dim,)
    # And the embedding is normalized
    assert np.isclose(np.linalg.norm(embeddings), 1.0)


def test_timeseries_finetuning(location):
    # Given a dataset with timeseries of two different shapes
    sequence_length = 20

    def make_timeseries(fn):
        return np.array([[fn(2 * math.pi * i / sequence_length) + random() / 2] for i in range(sequence_length)])

    fn1, fn2 = math.sin, lambda x: x
    dataset = Dataset.from_dict({"value": [make_timeseries(fn1), make_timeseries(fn2)] * 32, "label": [0, 1] * 32})
    # And an untrained timeseries embedding model
    model = EmbeddingModel("ts2vec", max_seq_length_override=sequence_length)
    # When we finetune the model
    finetuned_model = model.finetune(
        save_dir=location,
        train_dataset=dataset,
        value_column="value",
        training_args=TimeseriesEmbeddingTrainingArguments(
            num_train_epochs=2,
        ),
    )
    # Then the finetuned model creates embeddings that are more differentiated between the two types of timeseries
    trained_similarity = np.dot(
        finetuned_model.embed(make_timeseries(fn1)), finetuned_model.embed(make_timeseries(fn2))
    )
    untrained_similarity = np.dot(model.embed(make_timeseries(fn1)), model.embed(make_timeseries(fn2)))
    assert trained_similarity < untrained_similarity


def test_instruction_tuned_embedding_model():
    # Given an instruction tuned embedding model
    model = EmbeddingModel.BGE_BASE
    # And some text to embed
    text = "This is a test document"
    # When generating embeddings with the default and an overwritten prompts
    embedding_default = model.embed(text)
    embedding_with_override = model.embed(text, prompt="Instruct: Find text with similar sentiment\nQuery: ")
    # Then the embeddings are different
    assert not np.array_equal(embedding_default, embedding_with_override)
