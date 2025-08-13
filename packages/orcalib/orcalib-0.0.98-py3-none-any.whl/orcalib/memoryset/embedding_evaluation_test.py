import os
import tempfile
from unittest import mock

import pytest
from datasets import Dataset

from .embedding_evaluation import EmbeddingEvaluation, _sanitize_collection_name


@pytest.fixture()
def test_datasource():
    list_data = [
        {"text": "This sentence is about cats", "label": 1},
        {"text": "This sentence is about dogs", "label": 2},
        {"text": "This sentence is about cats", "label": 1},
        {"text": "This sentence is about dogs", "label": 2},
        {"text": 'This is another sentence about "cats"', "label": 1},
        {"text": 'This is another sentence about "dogs"', "label": 2},
        {"text": "This is yet another sentence about 'cats'", "label": 1},
        {"text": "This is yet another sentence about 'dogs'", "label": 2},
    ]

    return Dataset.from_list(list_data)


@pytest.fixture()
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory for Milvus databases
        milvus_dir = os.path.join(temp_dir, "milvus")
        os.makedirs(milvus_dir)

        # Set MILVUS_URL environment variable to point to the local database
        with mock.patch.dict("os.environ", {"MILVUS_URL": os.path.join(milvus_dir, "milvus.db")}):
            yield milvus_dir


def test_embedding_evaluation(test_datasource, temp_dir):
    result = EmbeddingEvaluation.run(
        dataset=test_datasource,
        run_name="test_embedding_evaluation",
        label_names=["empty", "cats", "dogs"],
        value_column="text",
        label_column="label",
        neighbor_count=3,
    )
    assert result is not None

    assert result.evaluation_results is not None
    assert len(result.evaluation_results) == 2

    assert result.evaluation_results[0].embedding_model_name == "GTE_BASE"
    assert result.evaluation_results[0].embedding_model_path == "OrcaDB/gte-base-en-v1.5"

    assert result.evaluation_results[1].embedding_model_name == "CDE_SMALL"
    assert result.evaluation_results[1].embedding_model_path == "OrcaDB/cde-small-v1"

    for i in range(len(result.evaluation_results)):
        assert result.evaluation_results[i].analysis_result.neighbor_prediction_accuracy >= 0.0
        assert result.evaluation_results[i].analysis_result.mean_neighbor_label_confidence >= 0.0
        assert result.evaluation_results[i].analysis_result.mean_neighbor_label_entropy >= 0.0
        assert result.evaluation_results[i].analysis_result.mean_neighbor_predicted_label_ambiguity >= 0.0


def test_sanitize_collection_name():
    """Test that collection name sanitization handles all invalid characters."""
    # Basic replacements
    assert _sanitize_collection_name("model-123-abc") == "model_123_abc"
    assert _sanitize_collection_name("model.with.dots") == "model_with_dots"
    assert _sanitize_collection_name("model with spaces") == "model_with_spaces"

    # Special characters and paths
    assert _sanitize_collection_name("model:123") == "model_123"
    assert _sanitize_collection_name("path/to/model") == "path_to_model"
    assert _sanitize_collection_name("http://example.com/model") == "http___example_com_model"
    assert _sanitize_collection_name("model@version!2") == "model_version_2"

    # Mixed invalid characters
    assert _sanitize_collection_name("model#1:test/v2.0") == "model_1_test_v2_0"

    # Valid characters should remain unchanged
    assert _sanitize_collection_name("model_123_ABC") == "model_123_ABC"
    assert _sanitize_collection_name("UPPERCASE_lower_123") == "UPPERCASE_lower_123"
