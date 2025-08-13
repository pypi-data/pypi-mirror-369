import logging
from typing import Generator, cast
from uuid import uuid4

import numpy as np
import pytest
from datasets import ClassLabel, Dataset, load_dataset

from ..conftest import skip_in_ci
from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset
from .concept_layer import (
    ConceptMap,
    object_to_pickle_str,
    subsample_dataset,
    unpickle_from_str,
)


@pytest.fixture(scope="module")
def concept_map() -> Generator[ConceptMap, None, None]:
    dataset = cast(Dataset, load_dataset("fancyzhx/ag_news", split="train")).shuffle(seed=42)
    dataset = subsample_dataset(dataset, max_rows=500, stratify_by_column="label", seed=42)
    # dataset.to_json("./ag_news_train_500.jsonl")
    # dataset = cast(Dataset, Dataset.from_json("./ag_news_train_500.jsonl"))
    memoryset = LabeledMemoryset(
        f"memory:#ag_news_test_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_SMALL,
        label_names=["World", "Sports", "Business", "Sci/Tech"],
    )
    memoryset.insert(dataset, value_column="text")
    concept_map = ConceptMap.build(memoryset=memoryset, max_sample_rows=20_000)
    yield concept_map
    memoryset.drop(memoryset.uri)


@skip_in_ci("downloading the dataset from the hub does not work in CI for some reason")
def test_concept_map_builder(concept_map: ConceptMap) -> None:
    """
    Test the ConceptMapBuilder with the AG News dataset.
    """
    results = concept_map.predict(
        [
            "Apple releases its new iPhone model",
            "The stock market crashed today",
            "The local football team won their game",
            "NASA announces a new mission to Mars",
            "The economy is recovering after the recession",
        ]
    )
    print(results)
    pass


def test_reduce_dataset() -> None:
    """
    Test the reduce_dataset function to ensure it reduces the dataset correctly.
    """
    dataset = Dataset.from_dict({"text": ["sample"] * 100, "label": [0] * 100}).cast_column(
        "label", ClassLabel(names=["sample"])
    )
    reduced = subsample_dataset(dataset, max_rows=50, stratify_by_column="label", seed=42)
    assert len(reduced) == 50, "Dataset was not reduced to the correct size."


def test_object_to_pickle_str_and_unpickle_from_str() -> None:
    """
    Test the object_to_pickle_str and unpickle_from_str functions for serialization and deserialization.
    """
    original_object = {"key": "value", "number": 42}
    serialized = object_to_pickle_str(original_object)
    deserialized = unpickle_from_str(serialized, dict)
    assert deserialized == original_object, "Deserialized object does not match the original."


@skip_in_ci("downloading the dataset from the hub does not work in CI for some reason")
def test_concept_map_initialization(concept_map: ConceptMap) -> None:
    """
    Test the initialization of the ConceptMap class.
    """
    assert concept_map.fit_hdbscan is not None, "HDBSCAN model was not initialized."
    assert concept_map.fit_umap is not None, "UMAP model was not initialized."
    assert len(concept_map.cluster_by_id) > 0, "No clusters were identified."


@skip_in_ci("downloading the dataset from the hub does not work in CI for some reason")
def test_classify_with_soft_clustering(concept_map: ConceptMap) -> None:
    """
    Test the classify_with_soft_clustering method of ConceptMap.
    """
    samples = [
        "Apple releases its new iPhone model",
        "The stock market crashed today",
    ]
    predictions = concept_map.predict(samples)

    assert len(predictions) == len(samples), "Number of predictions does not match number of samples."


@skip_in_ci("downloading the dataset from the hub does not work in CI for some reason")
def test_is_noise(concept_map: ConceptMap) -> None:
    """
    Test the is_noise method of ConceptMap.
    """
    samples = [
        # Gibberish
        "%$#@$%!#@",
        "asd filjkasndlkcnZC?ZXCV labsdhasd",
        # Random phrases
        "There were shadows where the light forgot to land, and nobody seemed to mind or notice anymore.",
        "Every corner of the morning felt heavier than the night, like waiting for something that never learned how to arrive.",
        "They kept talking about the weather, but it wasn’t really about the weather at all, just a way to fill the quiet.",
        "Moments like these drift past the window, carrying thoughts that never bother to settle anywhere meaningful.",
        "The room smelled faintly of old decisions and unopened letters, lingering like guests who missed their chance to leave.",
        # News articles
        "Apple releases its new iPhone model",
        "The stock market crashed today",
        "The local football team won their game",
        "NASA announces a new mission to Mars",
        "The economy is recovering after the recession",
    ]

    samples = [
        f"Determine the category of the following news article or mark is as noise: {sample}" for sample in samples
    ]
    noise_flags = concept_map.is_noise(samples)
    predictions = concept_map.predict(samples)
    logging.info(f"Noise flags: {noise_flags}")
    logging.info(f"Labels: {[pred.label for pred in predictions]}")
    logging.info(f"Confidence: {[pred.probability for pred in predictions]}")

    # NOTE: Uncomment the following lines to help in debugging
    # class_icons = ["🌎", "🏀", "💰", "🧬"]
    # noise_icon = "🚨"

    # labeled = [ f"{class_icons[p.label]} {sample}" if p.label is not None and p.label != -1 else f"{noise_icon} {sample}" for sample, p in zip(samples, predictions)]
    # logging.info("\n".join(labeled))

    assert len(noise_flags) == len(samples), "Number of noise flags does not match number of samples."
    assert all(isinstance(flag, np.bool) for flag in noise_flags), "Noise flags are not boolean values."
    # TODO: Verify that the noise samples are being flagged as noise. This isn't happening currently.
