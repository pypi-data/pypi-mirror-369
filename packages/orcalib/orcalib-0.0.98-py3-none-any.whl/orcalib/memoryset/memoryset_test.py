import base64
import io
import logging
import math
import os
import tempfile
import time
from random import random
from unittest import mock

import numpy as np
import pytest
from datasets import ClassLabel, Dataset, Sequence, Value
from PIL import Image as pil
from uuid_utils.compat import uuid4, uuid7

from ..conftest import skip_in_ci
from ..embedding import EmbeddingModel
from .experimental_util import get_cascading_edits_suggestions
from .memory_types import (
    LabeledMemory,
    LabeledMemoryInsert,
    LabeledMemoryLookup,
    LabeledMemoryUpdate,
    LookupReturnType,
    MemoryMetrics,
    ScoredMemoryInsert,
    ScoredMemoryUpdate,
)
from .memoryset import LabeledMemoryset, ScoredMemoryset
from .repository import FilterItem
from .repository_memory import MemorysetInMemoryRepository
from .repository_milvus import MemorysetMilvusRepository

logging.basicConfig(level=logging.INFO)

LABEL_NAMES = ["even", "odd"]

SENTENCES = [
    "The chef flies over the moon.",
    "The cat fixes a theory.",
    "A bird brings the fence.",
    "The writer fixes the code.",
    "The student jumps over a mystery.",
    "A bird brings the mountain.",
    "The cat finds a theory.",
    "A bird teaches a new planet.",
    "The gardener cooks a puzzle.",
    "A bird throws a statue.",
    "A bird cooks a mystery.",
    "The artist finds a puzzle.",
    "A teacher throws the secret.",
    "The cat breaks a theory.",
    "A scientist finds the painting.",
    "The chef finds a statue.",
    "The robot paints an instrument.",
    "A dog sings to a new planet.",
    "The robot discovers the street.",
    "A scientist teaches a new planet.",
]

# To enable tests against a milvus server instance, set MILVUS_SERVER_URL = "http://localhost:19530"
# Keep this set to None by default to avoid requiring a dockerized milvus instance for tests
MILVUS_SERVER_URL = os.getenv("MILVUS_SERVER_URL")

BACKEND_TYPES = ["in-memory", "milvus-lite"] + (["milvus-server"] if MILVUS_SERVER_URL else [])

TEST_DATASET = Dataset.from_dict(
    {
        "value": SENTENCES,
        "label": [i % 2 for i in range(len(SENTENCES))],
    }
).cast_column("label", ClassLabel(names=["even", "odd"]))


def test_repository_from_uri():
    # Can parse a local Milvus URL
    assert LabeledMemoryset.repository_from_uri("./temp/milvus.db#my_collection") == MemorysetMilvusRepository(
        collection_name="my_collection", database_uri="./temp/milvus.db"
    )
    # Can parse a remote Milvus URL
    assert LabeledMemoryset.repository_from_uri(
        "http://milvus-standalone:19530#my_collection"
    ) == MemorysetMilvusRepository(collection_name="my_collection", database_uri="http://milvus-standalone:19530")
    # Can parse in memory collection name
    assert LabeledMemoryset.repository_from_uri("memory:#my_collection") == MemorysetInMemoryRepository(
        collection_name="my_collection"
    )
    # Can parse collection name with Milvus URL environment variable present
    with mock.patch.dict("os.environ", {"MILVUS_URL": "http://milvus-standalone:19530"}):
        assert LabeledMemoryset.repository_from_uri("my_collection") == MemorysetMilvusRepository(
            collection_name="my_collection", database_uri="http://milvus-standalone:19530"
        )
    # Throws when collection name is invalid
    with pytest.raises(ValueError):
        LabeledMemoryset.repository_from_uri("milvus.db#my-collection")
    with mock.patch.dict("os.environ", {"MILVUS_URL": "http://milvus-standalone:19530"}):
        with pytest.raises(ValueError):
            LabeledMemoryset.repository_from_uri("my/collection")


@pytest.fixture()
def temp_folder():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(params=BACKEND_TYPES)
def memoryset_uri(request, temp_folder) -> str:
    match request.param:
        case "in-memory":
            return f"memory:#{uuid4().hex[:8]}"
        case "milvus-lite":
            return f"{temp_folder}/milvus.db#memories"
        case "milvus-server":
            if MILVUS_SERVER_URL is None:
                raise ValueError("MILVUS_SERVER_URL is not set")

            collection_name = "collection_" + uuid4().hex[:8]

            if MILVUS_SERVER_URL.startswith("http"):
                return f"{MILVUS_SERVER_URL}#{collection_name}"
            else:
                return f"http://{MILVUS_SERVER_URL}#{collection_name}"
        case _:
            raise ValueError(f"Unknown storage backend type: {request.param}")


@pytest.fixture()
def memoryset() -> LabeledMemoryset:
    return LabeledMemoryset(
        f"memory:#memoryset_test_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_SMALL,
        label_names=LABEL_NAMES,
    )


def test_create_new_memoryset(memoryset_uri: str):
    # When we create a new memoryset
    memoryset = LabeledMemoryset(
        memoryset_uri,
        embedding_model=EmbeddingModel.CLIP_BASE,
        label_names=LABEL_NAMES,
    )
    # Then the correct storage backend is inferred from the URI
    if memoryset_uri.startswith("memory:"):
        from .repository_memory import MemorysetInMemoryRepository

        assert isinstance(memoryset.repository, MemorysetInMemoryRepository)
    else:
        from .repository_milvus import MemorysetMilvusRepository

        assert isinstance(memoryset.repository, MemorysetMilvusRepository)
    # And the embedding model is used
    assert memoryset.embedding_model.path == EmbeddingModel.CLIP_BASE.path
    # And the memoryset is empty
    assert len(memoryset) == 0
    # And the label names are correct
    assert memoryset.label_names == LABEL_NAMES


def test_memoryset_with_contextual_embedding_model():
    # When a memoryset with a contextual embedding model is created
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.CDE_SMALL,
        label_names=LABEL_NAMES,
    )
    pre_context_embedding = memoryset.embedding_model.embed([SENTENCES[0]])[0]
    # And some memories are inserted
    memoryset.insert(TEST_DATASET)
    assert len(memoryset) == len(TEST_DATASET)
    # Then the context is initialized
    assert memoryset.embedding_model.uses_context
    assert memoryset._embedding_context is not None
    # And embeddings are different from those computed without context
    assert not np.allclose(
        memoryset._embed([SENTENCES[0]], value_kind="document", use_cache=False)[0], pre_context_embedding
    )


def test_connect_to_existing_memoryset(memoryset: LabeledMemoryset):
    # Given a memoryset that has some memories
    memoryset.insert(TEST_DATASET)
    assert len(memoryset) == len(TEST_DATASET)
    memoryset_uri = memoryset.uri
    # When we reconnect to the memoryset
    del memoryset
    reconnected_memoryset = LabeledMemoryset.connect(memoryset_uri)
    # Then the memoryset with the correct embedding model is loaded
    assert reconnected_memoryset.embedding_model == EmbeddingModel.GTE_SMALL
    # And it has the same number of memories
    assert len(reconnected_memoryset) == len(TEST_DATASET)
    # And the label names are correct
    assert reconnected_memoryset.label_names == LABEL_NAMES


def test_error_on_connect_to_deleted_memoryset():
    # When trying to connect to a memoryset that does not exist
    with pytest.raises(ValueError):
        LabeledMemoryset.connect("file://tmp/non-existent-memoryset.db#non-existent-memoryset")


def test_drop_and_exists(memoryset: LabeledMemoryset):
    # Given a memoryset
    assert LabeledMemoryset.exists(memoryset.uri)
    # When we drop the memoryset
    LabeledMemoryset.drop(memoryset.uri)
    # Then the memoryset no longer exists
    assert not LabeledMemoryset.exists(memoryset.uri)


def test_insert_list(memoryset: LabeledMemoryset):
    # When we insert memories into the memoryset
    memoryset.insert(
        [
            LabeledMemoryInsert(value="hello", label=0),
            LabeledMemoryInsert(value="world", label=1),
        ]
    )
    # Then the memoryset has the correct number of memories
    memoryset_length = 2
    assert len(memoryset) == memoryset_length
    # And all the memories are present
    contents = sorted(memoryset, key=lambda x: x.label)
    assert len(contents) == memoryset_length
    assert contents[0].value == "hello"
    assert contents[0].label == 0
    assert contents[0].memory_version is not None
    assert contents[1].value == "world"
    assert contents[1].label == 1
    assert contents[1].label_name == LABEL_NAMES[1]
    # And the memories have the correct metadata added
    assert contents[0].source_id is None
    assert contents[0].label_name == LABEL_NAMES[0]
    assert contents[0].embedding is not None
    assert contents[0].memory_id is not None
    assert contents[0].created_at is not None
    assert contents[0].updated_at is not None
    assert contents[1].source_id is None
    assert contents[1].embedding is not None
    assert contents[1].memory_id is not None
    assert contents[1].memory_version is not None
    assert contents[1].created_at is not None
    assert contents[1].updated_at is not None


def test_insert_list_of_dicts(memoryset: LabeledMemoryset):
    # When we insert a list of dicts into the memoryset
    memoryset.insert(
        [
            {"value": "hello", "label": 0, "other": "foo", "id": "1"},
            {"value": "world", "label": 1, "other": "bar", "id": "2"},
        ],
        source_id_column="id",
        other_columns_as_metadata=True,
    )
    # Then the memoryset has the correct number of memories
    assert len(memoryset) == 2
    # And the memories have the correct label names
    assert memoryset[0].label == 0
    assert memoryset[0].value == "hello"
    assert memoryset[1].label == 1
    assert memoryset[1].value == "world"
    # And the memories have the correct metadata
    assert memoryset[0].metadata == {"other": "foo"}
    assert memoryset[1].metadata == {"other": "bar"}
    # And the memories have the correct source ids
    assert memoryset[0].source_id == "1"
    assert memoryset[1].source_id == "2"


def test_insert_dataset(memoryset: LabeledMemoryset):
    # When a dataset is inserted into the memoryset
    memoryset.insert(TEST_DATASET)
    # Then the memoryset has the correct number of memories
    assert len(memoryset) == len(TEST_DATASET)
    # And the labels are correct
    assert all(memory.label in [0, 1, 2] for memory in memoryset)
    # And the label names are correct
    assert all(memory.label_name in LABEL_NAMES for memory in memoryset)


def test_insert_infers_label_names(memoryset: LabeledMemoryset):
    # Given a memoryset with no label names
    memoryset.label_names = []
    assert memoryset.label_names == []
    # And a dataset with a class label column
    dataset = Dataset.from_list(
        [
            {"text": "hello", "label": "even"},
            {"text": "world", "label": "odd"},
            {"text": "!", "label": "even"},
        ]
    ).cast_column("label", ClassLabel(names=["even", "odd"]))
    # When we insert the dataset into the memoryset
    memoryset.insert(dataset, value_column="text")
    # Then the label names are inferred
    assert memoryset.label_names == ["even", "odd"]
    # And the memories have the correct label names
    assert all(memory.label_name in ["even", "odd"] for memory in memoryset)


def test_iterate_memoryset(memoryset: LabeledMemoryset):
    # When we iterate over the memoryset
    el_count = 0
    for memory in memoryset:
        el_count += 1
        # Then we get all labeled memories
        assert isinstance(memory, LabeledMemory)
        assert memory.value in SENTENCES
        assert memory.label in [0, 1]
        assert memory.label_name in LABEL_NAMES
    # And all memories are iterated over
    assert el_count == len(memoryset)


def test_slice_memoryset(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET.select(range(5)))
    # When we slice the memoryset
    slice_length = 2
    sliced_memoryset = memoryset[1 : 1 + slice_length]
    # Then we get an iterator
    assert isinstance(sliced_memoryset, list)
    # And the iterator contains the correct memories
    el_count = 0
    for memory in sliced_memoryset:
        el_count += 1
        assert memory.label_name in LABEL_NAMES
    assert el_count == slice_length


def test_memoryset_to_dataset(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET.select(range(3)), show_progress_bar=False)
    # When a memoryset is converted to a dataset
    dataset = memoryset.to_dataset(value_column="text", label_column="sentiment")
    # Then the dataset has the correct length
    assert len(dataset) == len(memoryset)
    # And the correct features
    assert isinstance(dataset.features["text"], Value)
    assert dataset.features["text"].dtype == "string"
    assert isinstance(dataset.features["sentiment"], ClassLabel)
    assert dataset.features["sentiment"].dtype == "int64"
    assert dataset.features["sentiment"].names == memoryset.label_names
    assert isinstance(dataset.features["memory_id"], Value)
    assert dataset.features["memory_id"].dtype == "string"
    assert isinstance(dataset.features["memory_version"], Value)
    assert dataset.features["memory_version"].dtype == "int64"
    assert dataset.features["embedding"] is not None
    assert isinstance(dataset.features["embedding"], Sequence)
    assert dataset.features["embedding"].feature.dtype == "float32"
    assert isinstance(dataset.features["source_id"], Value)
    assert dataset.features["source_id"].dtype == "string"
    assert isinstance(dataset.features["metadata"], dict)
    assert isinstance(dataset.features["metrics"], dict)
    # And the memories are correct
    for i, sample in enumerate(dataset):
        memory = memoryset[i]
        assert isinstance(sample, dict)
        assert sample["text"] == memory.value
        assert sample["sentiment"] == memory.label
        assert isinstance(sample["embedding"], list)
        assert len(sample["embedding"]) == memoryset.embedding_model.embedding_dim
        assert np.allclose(np.array(sample["embedding"]), memory.embedding)
        assert sample["memory_id"] == str(memory.memory_id)
        assert sample["memory_version"] == memory.memory_version
        assert sample["source_id"] == memory.source_id
        assert sample["metadata"] == memory.metadata
        assert sample["metrics"] == memory.metrics or {}


def test_getitem_at_index(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory
    memoryset.insert(TEST_DATASET.select(range(1)))
    # When we get a memory at index 0
    memory = memoryset[0]
    # Then the memory is returned
    assert memory is not None
    assert memory.value == SENTENCES[0]
    assert memory.label == 0
    assert memory.label_name == LABEL_NAMES[0]


def test_query(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET)
    # When we query the first two even memories
    result = memoryset.query(filters=[("label", "==", 0)], limit=2)
    # Then we get the correct memories
    assert len(result) == 2
    assert all(memory.label == 0 for memory in result)
    assert result[0].value == SENTENCES[0]
    assert result[1].value == SENTENCES[2]


def test_lookup(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET)
    # When we lookup 3 similar memories
    query = SENTENCES[0]
    lookup_count = 3
    result = memoryset.lookup(query, count=lookup_count)
    # Then we get 3 similar memories
    assert len(result) == lookup_count
    for lookup in result:
        assert isinstance(lookup, LabeledMemoryLookup)
        assert lookup.value in SENTENCES
        assert lookup.lookup_score > 0.5
        assert lookup.embedding.shape == (memoryset.embedding_model.embedding_dim,)
        assert lookup.embedding.dtype == np.float32
        assert lookup.label in [0, 1]
        assert lookup.label_name in LABEL_NAMES
    # And one exact match
    assert result[0].value == query
    assert result[0].lookup_score >= 0.999


def test_lookup_exclude_exact_match(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET)
    # When we lookup a query and exclude the exact match
    query = SENTENCES[0]
    result = memoryset.lookup(query, count=3, exclude_exact_match=True)
    # Then the correct number of memories are returned
    assert len(result) == 3
    # And the exact match is not included
    assert all(lookup.value != query for lookup in result)


def test_lookup_columns(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET)
    # When we lookup a batch of queries and request columnar results
    queries = SENTENCES[2:5]
    batch_size = len(queries)
    memory_count = 5
    results = memoryset.lookup(queries, count=memory_count, return_type=LookupReturnType.COLUMNS)
    # Then we get back a dictionary containing the input embeddings as a numpy array
    assert isinstance(results["input_embeddings"], np.ndarray)
    assert results["input_embeddings"].shape == (batch_size, memoryset.embedding_model.embedding_dim)
    assert results["input_embeddings"].dtype == np.float32
    # And the memories embeddings as a numpy tensor
    assert isinstance(results["memories_embeddings"], np.ndarray)
    assert results["memories_embeddings"].shape == (batch_size, memory_count, memoryset.embedding_model.embedding_dim)
    assert results["memories_embeddings"].dtype == np.float32
    # And the memory labels as a numpy array
    assert isinstance(results["memories_labels"], np.ndarray)
    assert results["memories_labels"].shape == (batch_size, memory_count)
    assert results["memories_labels"].dtype == np.int64
    # And the memory lookup scores as a numpy arrays
    assert isinstance(results["memories_lookup_scores"], np.ndarray)
    assert results["memories_lookup_scores"].shape == (batch_size, memory_count)
    assert results["memories_lookup_scores"].dtype == np.float32
    # And the values for the memories for each query
    assert isinstance(results["memories_values"], list)
    assert len(results["memories_values"]) == batch_size
    assert len(results["memories_values"][0]) == memory_count
    assert all(isinstance(value, str) for value in results["memories_values"][0])
    assert all(value in SENTENCES for value in results["memories_values"][0])
    # And the label names for the memories for each query
    assert isinstance(results["memories_label_names"], list)
    assert len(results["memories_label_names"]) == batch_size
    assert len(results["memories_label_names"][0]) == memory_count
    assert all(label_name in LABEL_NAMES for label_name in results["memories_label_names"][0])
    # And the memories ids for each query
    assert isinstance(results["memories_ids"], list)
    assert len(results["memories_ids"]) == batch_size
    assert len(results["memories_ids"][0]) == memory_count
    # And the memory versions for each query
    assert isinstance(results["memories_versions"], list)
    assert len(results["memories_versions"]) == batch_size
    assert len(results["memories_versions"][0]) == memory_count
    assert all(isinstance(memory_version, int) for memory_version in results["memories_versions"][0])
    # And the metadata for the memories for each query
    assert isinstance(results["memories_metadata"], list)
    assert len(results["memories_metadata"]) == batch_size
    assert len(results["memories_metadata"][0]) == memory_count
    assert all(isinstance(metadata, dict) for metadata in results["memories_metadata"][0])


def test_lookup_input_embedding_only(memoryset: LabeledMemoryset):
    # When a lookup is requested with a count of 0
    query = SENTENCES[:2]
    result = memoryset.lookup(query, count=0, return_type="columns")
    # Then the input embeddings are returned as a numpy array
    assert isinstance(result["input_embeddings"], np.ndarray)
    assert result["input_embeddings"].shape == (2, memoryset.embedding_model.embedding_dim)
    assert result["input_embeddings"].dtype == np.float32
    # And other memory fields are empty
    assert isinstance(result["memories_embeddings"], np.ndarray)
    assert result["memories_embeddings"].shape == (2, 0)
    assert result["memories_embeddings"].dtype == np.float32
    assert isinstance(result["memories_labels"], np.ndarray)
    assert result["memories_labels"].shape == (2, 0)
    assert result["memories_labels"].dtype == np.int64
    assert isinstance(result["memories_lookup_scores"], np.ndarray)
    assert result["memories_lookup_scores"].shape == (2, 0)
    assert result["memories_lookup_scores"].dtype == np.float32
    assert result["memories_values"] == [[], []]
    assert result["memories_label_names"] == [[], []]
    assert result["memories_ids"] == [[], []]
    assert result["memories_versions"] == [[], []]
    assert result["memories_metadata"] == [[], []]


def test_lookup_images():
    # Given a memoryset with an image
    memoryset = ScoredMemoryset(
        f"memory:#memoryset_test_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.CLIP_BASE,
    )
    image = pil.open(
        io.BytesIO(
            base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg=="  # red circle
            )
        )
    )
    memoryset.insert([{"value": image, "score": 0.1}])
    assert memoryset.value_type == "image"
    # When we lookup an image
    result = memoryset.lookup(image, count=1)
    # Then we get the correct image
    assert len(result) == 1
    assert result[0].value == image
    assert result[0].score == 0.1


def test_lookup_with_filters():
    # Given a memoryset with some memories
    memoryset = LabeledMemoryset(
        f"memory:#memoryset_test_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.CLIP_BASE,
    )
    memoryset.insert(TEST_DATASET)

    query_sentence = "The bird is flying in the night sky"
    count = 4

    # When we lookup with a filter
    result = memoryset.lookup(query_sentence, count=count, filters=[FilterItem(field=("label",), op="==", value=0)])

    # Then we get the correct memory
    assert len(result) == count

    assert isinstance(result[0].value, str)

    assert "bird" in result[0].value

    for r in result:
        assert r.label == 0
        assert r.label_name == LABEL_NAMES[0]

    # When we lookup with a filter
    result = memoryset.lookup(query_sentence, count=count, filters=[FilterItem(field=("label",), op="==", value=1)])

    # Then we get the correct memory
    assert len(result) == count

    assert isinstance(result[0].value, str)

    assert "bird" in result[0].value

    for r in result:
        assert r.label == 1
        assert r.label_name == LABEL_NAMES[1]


def test_timeseries_lookup():
    # Given a memoryset with a few images
    sequence_length = 20

    def make_timeseries(fn):
        return np.array([[fn(2 * math.pi * i / sequence_length) + random() / 2] for i in range(sequence_length)])

    dataset = Dataset.from_list(
        [{"value": make_timeseries(math.sin), "label": 0} for _ in range(3)]
        + [{"value": make_timeseries(lambda x: -x), "label": 1} for _ in range(3)]
    )
    memoryset = LabeledMemoryset(
        f"memory:#memoryset_test_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel("ts2vec", max_seq_length_override=sequence_length),
        label_names=["sin", "-x"],
    )
    memoryset.insert(dataset)
    assert memoryset.value_type == "timeseries"
    # When we lookup a timeseries
    result = memoryset.lookup(make_timeseries(math.sin), count=2)
    # Then we get the correct timeseries
    assert len(result) == 2
    for lookup in result:
        assert lookup.label_name == "sin"


def test_get(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory
    memoryset.insert(TEST_DATASET.select(range(1)))
    m = memoryset[0]
    # When we get a memory by its id
    memory = memoryset.get(m.memory_id)
    # Then we get the correct memory
    assert memory is not None
    assert memory.memory_id == m.memory_id
    assert memory.value == m.value
    assert memory.label == m.label
    assert memory.label_name == LABEL_NAMES[m.label]


def test_getitem_by_id(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory
    memoryset.insert(TEST_DATASET.select(range(1)))
    # When we get a memory by its id
    memory = memoryset[memoryset[0].memory_id]
    # Then we get the correct memory
    assert memory is not None
    assert isinstance(memory, LabeledMemory)
    assert memory.memory_id == memoryset[0].memory_id


def test_get_not_found(memoryset: LabeledMemoryset):
    # When we get a memory that doesn't exist
    memory = memoryset.get(uuid7())
    # Then we get None
    assert memory is None


def test_get_list(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory
    memoryset.insert(TEST_DATASET.select(range(1)))

    memories_to_insert = memoryset[0:2]

    # When we get a memory by its id
    memories_retrieved = memoryset.get([m.memory_id for m in memories_to_insert])

    for i, memory in enumerate(memories_retrieved):
        m = memoryset[i]

        # Then we get the correct memory
        assert memory is not None
        assert memory.memory_id == m.memory_id
        assert memory.value == m.value
        assert memory.label == m.label
        assert memory.label_name == LABEL_NAMES[m.label]


def test_delete(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 2
    memoryset.insert(TEST_DATASET.select(range(memoryset_length)))
    assert len(memoryset) == memoryset_length
    m = memoryset[0]
    # When we delete a memory
    delete_success = memoryset.delete(m.memory_id)
    # Then True is returned
    assert delete_success is True
    # Then the memory is no longer in the memoryset
    assert memoryset.get(m.memory_id) is None
    assert len(memoryset) == memoryset_length - 1


def test_delete_not_found(memoryset: LabeledMemoryset):
    # When we try to delete a memory that doesn't exist
    delete_success = memoryset.delete(uuid7())
    # Then False is returned
    assert delete_success is False
    # And nothing is deleted
    assert len(memoryset) == 0


def test_update(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory
    memoryset.insert([LabeledMemoryInsert(value="My new sentence", label=0, source_id="t:1", metadata={"a": "b"})])
    time.sleep(0.01)
    memory = memoryset[0]
    prev_embedding = memory.embedding
    # When we update a memory
    metrics = MemoryMetrics(
        neighbor_predicted_label=0,
        is_duplicate=True,
        neighbor_label_logits=np.array([0.1, 0.9], dtype=np.float32),
        neighbor_predicted_label_ambiguity=0.124,
    )
    memoryset.update(
        LabeledMemoryUpdate(
            memory_id=memory.memory_id,
            label=1,
            value="updated_value",
            source_id="t:1",
            metadata={"a": "b"},
            metrics=metrics,
        ),
    )
    # Then the memory is updated
    updated_memory = memoryset.get(memory.memory_id)
    assert updated_memory is not None
    assert updated_memory.label == 1
    assert updated_memory.value == "updated_value"
    assert updated_memory.source_id == "t:1"
    assert updated_memory.metadata == {"a": "b"}
    # And the metrics are updated
    assert updated_memory.metrics is not None
    assert updated_memory.metrics.get("neighbor_predicted_label") == metrics.get("neighbor_predicted_label")
    assert updated_memory.metrics.get("is_duplicate") == metrics.get("is_duplicate")
    assert isinstance(updated_memory.metrics.get("neighbor_label_logits"), np.ndarray)
    assert (updated_memory.metrics.get("neighbor_label_logits") == metrics.get("neighbor_label_logits")).all()
    assert updated_memory.metrics.get("neighbor_predicted_label_ambiguity") == metrics.get(
        "neighbor_predicted_label_ambiguity"
    )
    # And the memory version is incremented
    assert updated_memory.memory_version == memory.memory_version + 1
    # And the updated at timestamp is updated
    assert updated_memory.updated_at > memory.updated_at
    # And the edited at timestamp is updated
    assert updated_memory.edited_at > memory.updated_at
    # And the memory is re-embedded
    assert updated_memory.embedding is not None
    assert not np.allclose(updated_memory.embedding, prev_embedding)
    # And the label name is updated
    assert updated_memory.label_name == LABEL_NAMES[1]


def test_update_merges_metrics(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory and existing metrics
    memoryset.insert([LabeledMemoryInsert(value="My new sentence", label=0, source_id="t:1", metadata={"a": "b"})])
    memory = memoryset[0]
    memoryset.update(
        LabeledMemoryUpdate(memory_id=memory.memory_id, metrics={"neighbor_predicted_label": 0, "is_duplicate": True})
    )
    # When we update the memory with new metrics
    memoryset.update(
        LabeledMemoryUpdate(
            memory_id=memory.memory_id, metrics={"is_duplicate": False, "cluster": 1, "neighbor_predicted_label": 1}
        )
    )
    # Then the metrics are merged
    assert memoryset[0].metrics is not None
    assert memoryset[0].metrics.get("neighbor_predicted_label") == 1
    assert memoryset[0].metrics.get("is_duplicate") is False
    assert memoryset[0].metrics.get("cluster") == 1


def test_updating_value_or_label_resets_metrics(memoryset: LabeledMemoryset):
    # Given a memoryset with two memories with metrics
    memoryset.insert(
        [
            LabeledMemoryInsert(value="My new sentence", label=0, source_id="t:1", metadata={"a": "b"}),
            LabeledMemoryInsert(value="My new sentence", label=0, source_id="t:1", metadata={"a": "b"}),
        ]
    )
    memoryset.update(
        [
            LabeledMemoryUpdate(
                memory_id=memoryset[0].memory_id,
                metrics=MemoryMetrics(neighbor_predicted_label=0, is_duplicate=True),
            ),
            LabeledMemoryUpdate(
                memory_id=memoryset[1].memory_id,
                metrics=MemoryMetrics(neighbor_predicted_label=1, is_duplicate=False),
            ),
        ]
    )
    assert memoryset[0].metrics is not None
    assert memoryset[1].metrics is not None
    # When we update the value or label
    updated_memories = memoryset.update(
        [
            LabeledMemoryUpdate(memory_id=memoryset[0].memory_id, value="new value"),
            LabeledMemoryUpdate(memory_id=memoryset[1].memory_id, label=1),
        ]
    )
    # Then the metrics are reset
    assert updated_memories[0] is not None
    assert updated_memories[0].metrics == {}
    assert updated_memories[1] is not None
    assert updated_memories[1].metrics == {}


def test_update_not_found(memoryset: LabeledMemoryset):
    # When we update a memory that doesn't exist
    updated_memory = memoryset.update(LabeledMemoryUpdate(memory_id=uuid7(), label=1))
    # Then none is returned
    assert updated_memory is None
    # And the memoryset is unchanged
    assert len(memoryset) == 0


def test_update_with_unset_fields(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory
    memoryset.insert([LabeledMemoryInsert(value="My new sentence", label=0, source_id="t:1", metadata={"a": "b"})])
    memory = memoryset[0]
    time.sleep(0.01)
    # When we update a memory with unset fields
    memoryset.update(LabeledMemoryUpdate(memory_id=memory.memory_id))
    # Then the memory is unchanged
    updated_memory = memoryset.get(memory.memory_id)
    assert updated_memory is not None
    assert updated_memory.value == memory.value
    assert updated_memory.label == memory.label
    assert updated_memory.label_name == LABEL_NAMES[memory.label]
    assert updated_memory.source_id == memory.source_id
    assert updated_memory.metadata == memory.metadata
    # And the memory version is not incremented
    assert updated_memory.memory_version == memory.memory_version
    # And the updated at timestamp is updated
    assert updated_memory.updated_at > memory.updated_at
    # But the edited at timestamp is not updated
    assert updated_memory.edited_at == memory.edited_at


def test_update_merges_metadata(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory with metadata
    memoryset.insert([LabeledMemoryInsert(value="My new sentence", label=0, source_id="t:1", metadata={"a": 1})])
    memory = memoryset[0]
    time.sleep(0.01)
    # When we update a memory with a new metadata
    updated_memory = memoryset.update(LabeledMemoryUpdate(memory_id=memory.memory_id, metadata={"b": 2}))
    # Then the metadata is merged
    assert updated_memory is not None
    assert updated_memory.metadata == {"a": 1, "b": 2}
    # And the memory version is not incremented
    assert updated_memory.memory_version == memory.memory_version
    # And the updated at timestamp is updated
    assert updated_memory.updated_at > memory.updated_at
    # But the edited at timestamp is not updated
    assert updated_memory.edited_at == memory.edited_at


def test_update_set_to_none(memoryset: LabeledMemoryset):
    # Given a memoryset with a memory
    memoryset.insert([LabeledMemoryInsert(value="My new sentence", label=0, source_id="t:1", metadata={"a": 1})])
    memory = memoryset[0]
    time.sleep(0.01)
    # When we set nullable fields to None
    updated_memory = memoryset.update(
        LabeledMemoryUpdate(memory_id=memory.memory_id, source_id=None, metadata=None, metrics=None)
    )
    # Then they are updated
    assert updated_memory is not None
    assert updated_memory.source_id is None
    assert updated_memory.metadata == {}
    assert updated_memory.metrics == {}
    # And the memory version is not incremented
    assert updated_memory.memory_version == memory.memory_version
    # And the updated at timestamp is updated
    assert updated_memory.updated_at > memory.updated_at
    # But the edited at timestamp is not updated
    assert updated_memory.edited_at == memory.edited_at


def test_filter(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET)
    assert len(memoryset) == len(TEST_DATASET)
    # When we filter the memoryset to only include memories with the word "bird"
    filtered_memoryset = memoryset.filter(
        lambda x: "bird" in x.value if isinstance(x.value, str) else True,
        "filtered_collection",
    )
    # Then we get a new memoryset with the correct number of memories
    assert filtered_memoryset.uri == f"{memoryset.repository.database_uri}#filtered_collection"
    assert len(filtered_memoryset) == 5
    # And the old memoryset is unchanged
    assert len(memoryset) == len(TEST_DATASET)


def test_map(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 3
    memoryset.insert(TEST_DATASET.select(range(memoryset_length)))
    time.sleep(0.01)
    assert len(memoryset) == memoryset_length
    # When we map the memoryset to a new memoryset with the words reversed
    reverse_words = lambda sentence: " ".join(reversed(sentence.split()))  # noqa: E731
    mapped_memoryset = memoryset.map(
        lambda x: dict(value=reverse_words(x.value) if isinstance(x.value, str) else x.value),
        "mapped_collection",
    )
    # Then we get a new memoryset with the correct number of memories
    assert mapped_memoryset.uri == f"{memoryset.repository.database_uri}#mapped_collection"
    assert len(mapped_memoryset) == memoryset_length
    # And the memories have the correct values
    assert all(x.value in [reverse_words(s) for s in SENTENCES] for x in mapped_memoryset)
    # And the label names are correct
    assert all(x.label_name in LABEL_NAMES for x in mapped_memoryset)
    # And the old memoryset is unchanged
    assert len(memoryset) == memoryset_length
    assert all(x.value in SENTENCES for x in memoryset)
    # And the changed memories have been re-embedded
    assert all(x.embedding is not None for x in mapped_memoryset)
    # And the ids of the memories are preserved
    assert all(memoryset.get(x.memory_id) is not None for x in mapped_memoryset)
    # And the memory versions are incremented
    assert all(x.memory_version == memoryset[x.memory_id].memory_version + 1 for x in mapped_memoryset)
    # And the updated at timestamps are updated
    assert all(x.updated_at > memoryset[x.memory_id].updated_at for x in mapped_memoryset)
    # And the edited at timestamps are updated
    assert all(x.edited_at > memoryset[x.memory_id].updated_at for x in mapped_memoryset)
    # When we lookup a query that matches a mapped value exactly
    exact_match_query = "moon. the over flies chef The"
    assert exact_match_query in [x.value for x in mapped_memoryset]
    # Then we get a perfect lookup score
    exact_match_result = mapped_memoryset.lookup(exact_match_query)
    assert exact_match_result[0].value == exact_match_query
    assert exact_match_result[0].lookup_score >= 0.999
    # When we lookup a query that doesn't match any of the mapped values
    other_query = "The chef flies over the moon."
    assert other_query not in [x.value for x in mapped_memoryset]


def test_clone(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 3
    memoryset.insert(TEST_DATASET.select(range(memoryset_length)))
    assert len(memoryset) == memoryset_length
    # When we clone it to a new memoryset
    destination_uri = memoryset.repository.database_uri + "#destination_collection"
    cloned_memoryset = memoryset.clone(destination_uri)
    # Then we get a new memoryset with the same number of memories
    assert cloned_memoryset.repository == memoryset.repository_from_uri(destination_uri)
    assert len(cloned_memoryset) == memoryset_length
    # And the new memoryset has the same embedding model
    assert cloned_memoryset.embedding_model == memoryset.embedding_model
    # And the new memoryset has the same label names
    assert cloned_memoryset.label_names == memoryset.label_names
    # And all memories are copied over with the same values
    for memory in cloned_memoryset:
        assert memory == memoryset.get(memory.memory_id)
    # When we insert a new memory into the cloned memoryset
    cloned_memoryset.insert([LabeledMemoryInsert(value="My new sentence", label=0)])
    # Then the new memoryset has one more memory than the original memoryset
    assert len(cloned_memoryset) == memoryset_length + 1
    # And the original memoryset is unchanged
    assert len(memoryset) == memoryset_length


def test_clone_to_different_repository(memoryset, temp_folder):

    # Given an in memory memoryset with some memories
    memoryset_length = 3
    memoryset.insert(TEST_DATASET.select(range(memoryset_length)))
    assert len(memoryset) == memoryset_length
    # When we clone it to a Milvus memoryset
    milvus_memoryset = memoryset.clone(
        MemorysetMilvusRepository(collection_name="cloned_memoryset", database_uri=f"{temp_folder}/milvus.db")
    )
    # Then we get a new memoryset with the same number of memories
    assert len(milvus_memoryset) == memoryset_length
    # And the label names are cloned as well
    assert milvus_memoryset.label_names == memoryset.label_names
    assert milvus_memoryset.embedding_model == memoryset.embedding_model
    assert milvus_memoryset.uri == f"{temp_folder}/milvus.db#cloned_memoryset"


def test_update_embedding_model(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 2
    memoryset.insert(TEST_DATASET.select(range(memoryset_length)))
    assert len(memoryset) == memoryset_length
    # When we clone it to a new memoryset and update the embedding model
    new_embedding_model = EmbeddingModel.DISTILBERT
    cloned_memoryset = memoryset.clone(
        memoryset.repository.__class__(
            collection_name="memoryset_distilbert", database_uri=memoryset.repository.database_uri
        ),
        embedding_model=new_embedding_model,
    )
    # Then the new memoryset has the correct embedding model
    assert cloned_memoryset.embedding_model == new_embedding_model
    # And the embedding model is unchanged for the original memoryset
    assert memoryset.embedding_model == EmbeddingModel.GTE_SMALL
    # And the new memoryset has the correct number of memories
    assert len(cloned_memoryset) == memoryset_length
    # And the memories have been re-embedded
    assert all(x.embedding is not None for x in cloned_memoryset)
    assert memoryset.embedding_model.embedding_dim != new_embedding_model.embedding_dim
    for new_memory in cloned_memoryset:
        assert new_memory.embedding.shape == (new_embedding_model.embedding_dim,)


def test_reset(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 2
    memoryset.insert(TEST_DATASET.select(range(memoryset_length)))
    assert len(memoryset) == memoryset_length
    # When we reset the memoryset
    memoryset.reset()
    # Then the memoryset is empty
    assert len(memoryset) == 0
    # But we still have the same embedding model
    assert memoryset.embedding_model == EmbeddingModel.GTE_SMALL
    # And we can insert new memories
    memoryset.insert([LabeledMemoryInsert(value="My new sentence", label=0)])
    assert len(memoryset) == 1


def test_lookup_count_too_large(memoryset: LabeledMemoryset):
    # When we lookup more memories than the memoryset contains
    with pytest.raises(ValueError):
        memoryset.lookup(SENTENCES[0], count=len(TEST_DATASET) + 1)


def test_update_label_names(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 3
    memoryset.insert(TEST_DATASET.select(range(memoryset_length)))
    assert len(memoryset) == memoryset_length
    # When we update the label names
    new_label_names = ["positive", "negative"]
    memoryset.label_names = new_label_names
    # Then the label names are updated
    assert memoryset.label_names == new_label_names
    # And the config is updated
    assert memoryset.config.label_names == new_label_names
    # And the memories have the new label names when retrieved
    for memory in memoryset:
        assert memory.label_name in new_label_names
        if memory.label == 0:
            assert memory.label_name == "positive"
        else:
            assert memory.label_name == "negative"


# Use the same sentences as in labeled tests for simplicity
SCORED_SENTENCES = SENTENCES
TEST_SCORED_DATASET = Dataset.from_dict(
    {"value": SCORED_SENTENCES, "score": [0.9 + 0.01 * i for i in range(len(SCORED_SENTENCES))]}
)


@pytest.fixture()
def scored_memoryset() -> ScoredMemoryset:
    return ScoredMemoryset(f"memory:#scored_{uuid4().hex[:8]}", embedding_model=EmbeddingModel.CLIP_BASE)


def test_create_new_scored_memoryset(memoryset_uri: str):
    # Create a new scored memoryset
    scored = ScoredMemoryset(memoryset_uri, embedding_model=EmbeddingModel.CLIP_BASE)
    if memoryset_uri.startswith("memory:"):
        assert isinstance(scored.repository, MemorysetInMemoryRepository)
    else:
        assert isinstance(scored.repository, MemorysetMilvusRepository)

    assert scored.embedding_model.path == EmbeddingModel.CLIP_BASE.path
    assert len(scored) == 0


def test_connect_to_existing_scored_memoryset(scored_memoryset: ScoredMemoryset):
    scored_memoryset.insert(TEST_SCORED_DATASET)
    assert len(scored_memoryset) == len(TEST_SCORED_DATASET)
    uri = scored_memoryset.uri
    del scored_memoryset
    reconnected = ScoredMemoryset.connect(uri)
    assert reconnected.embedding_model.path == EmbeddingModel.CLIP_BASE.path
    assert len(reconnected) == len(TEST_SCORED_DATASET)


def test_drop_and_exists_scored(scored_memoryset: ScoredMemoryset):
    assert ScoredMemoryset.exists(scored_memoryset.uri)
    ScoredMemoryset.drop(scored_memoryset.uri)
    assert not ScoredMemoryset.exists(scored_memoryset.uri)


def test_insert_list_scored(scored_memoryset: ScoredMemoryset):
    scored_memoryset.insert(
        [
            ScoredMemoryInsert(value="hello", score=0.95),
            ScoredMemoryInsert(value="world", score=0.85),
        ]
    )
    assert len(scored_memoryset) == 2
    memories = sorted(list(scored_memoryset), key=lambda m: m.score, reverse=True)
    assert memories[0].value == "hello"
    assert memories[0].score == 0.95
    assert memories[1].value == "world"
    assert memories[1].score == 0.85


def test_insert_list_of_dicts_scored(scored_memoryset: ScoredMemoryset):
    scored_memoryset.insert(
        [
            {"value": "hello", "score": 0.95, "other": "foo", "id": "1"},
            {"value": "world", "score": 0.85, "other": "bar", "id": "2"},
        ],
        source_id_column="id",
        other_columns_as_metadata=True,
    )
    assert len(scored_memoryset) == 2
    for mem in scored_memoryset:
        assert mem.source_id is not None
        assert mem.embedding is not None


def test_lookup_scored(scored_memoryset: ScoredMemoryset):
    scored_memoryset.insert(TEST_SCORED_DATASET)
    # Lookup a query matching one of the sentences
    result = scored_memoryset.lookup("The chef flies over the moon.", count=1)
    # result should be a list of ScoredMemoryLookup objects
    if isinstance(result, list):
        lookup_mem = result[0]
    else:
        lookup_mem = result
    assert hasattr(lookup_mem, "lookup_score")
    assert lookup_mem.score is not None


def test_iterate_scored_memoryset(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    scored_memoryset.insert(TEST_SCORED_DATASET)
    # When we iterate over the memoryset
    el_count = 0
    for memory in scored_memoryset:
        el_count += 1
        # Then we get all scored memories
        assert memory.value in SCORED_SENTENCES
        assert isinstance(memory.score, float)
        assert 0.9 <= memory.score <= 1.1  # Based on test dataset scores
    # And all memories are iterated over
    assert el_count == len(scored_memoryset)


def test_slice_scored_memoryset(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(5)))
    # When we slice the memoryset
    slice_length = 2
    sliced_memoryset = scored_memoryset[1 : 1 + slice_length]
    # Then we get a list
    assert isinstance(sliced_memoryset, list)
    # And the list contains the correct number of memories
    assert len(sliced_memoryset) == slice_length
    # And each memory has a score
    for memory in sliced_memoryset:
        assert isinstance(memory.score, float)
        assert 0.9 <= memory.score <= 1.1


def test_get_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with a memory
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(1)))
    m = scored_memoryset[0]
    # When we get a memory by its id
    memory = scored_memoryset.get(m.memory_id)
    # Then we get the correct memory
    assert memory is not None
    assert memory.memory_id == m.memory_id
    assert memory.value == m.value
    assert memory.score == m.score


def test_getitem_by_id_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with a memory
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(1)))
    # When we get a memory by its id
    memory = scored_memoryset[scored_memoryset[0].memory_id]
    # Then we get the correct memory
    assert memory is not None
    assert memory.memory_id == scored_memoryset[0].memory_id


def test_get_not_found_scored(scored_memoryset: ScoredMemoryset):
    # When we get a memory that doesn't exist
    memory = scored_memoryset.get(uuid7())
    # Then we get None
    assert memory is None


def test_delete_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 2
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(memoryset_length)))
    assert len(scored_memoryset) == memoryset_length
    m = scored_memoryset[0]
    # When we delete a memory
    delete_success = scored_memoryset.delete(m.memory_id)
    # Then True is returned
    assert delete_success is True
    # Then the memory is no longer in the memoryset
    assert scored_memoryset.get(m.memory_id) is None
    assert len(scored_memoryset) == memoryset_length - 1


def test_delete_not_found_scored(scored_memoryset: ScoredMemoryset):
    # When we try to delete a memory that doesn't exist
    delete_success = scored_memoryset.delete(uuid7())
    # Then False is returned
    assert delete_success is False
    # And nothing is deleted
    assert len(scored_memoryset) == 0


def test_update_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with a memory
    scored_memoryset.insert(
        [ScoredMemoryInsert(value="My new sentence", score=0.95, source_id="t:1", metadata={"a": "b"})]
    )
    memory = scored_memoryset[0]
    time.sleep(0.01)
    prev_embedding = memory.embedding
    # When we update a memory
    scored_memoryset.update(
        ScoredMemoryUpdate(
            memory_id=memory.memory_id,
            score=0.85,
            value="updated_value",
            source_id="t:1",
            metadata={"a": "b"},
        ),
    )
    # Then the memory is updated
    updated_memory = scored_memoryset.get(memory.memory_id)
    assert updated_memory is not None
    assert updated_memory.score == 0.85
    assert updated_memory.value == "updated_value"
    assert updated_memory.source_id == "t:1"
    assert updated_memory.metadata == {"a": "b"}
    # And the memory version is incremented
    assert updated_memory.memory_version == memory.memory_version + 1
    # And the updated at timestamp is updated
    assert updated_memory.updated_at > memory.updated_at
    # And the edited at timestamp is updated
    assert updated_memory.edited_at > memory.updated_at
    # And the memory is re-embedded
    assert updated_memory.embedding is not None
    assert not np.allclose(updated_memory.embedding, prev_embedding)


def test_update_not_found_scored(scored_memoryset: ScoredMemoryset):
    # When we update a memory that doesn't exist
    updated_memory = scored_memoryset.update(ScoredMemoryUpdate(memory_id=uuid7(), score=0.95))
    # Then none is returned
    assert updated_memory is None
    # And nothing is inserted
    assert len(scored_memoryset) == 0


def test_filter_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    scored_memoryset.insert(TEST_SCORED_DATASET)
    assert len(scored_memoryset) == len(TEST_SCORED_DATASET)
    # When we filter the memoryset to only include memories with the word "bird"
    filtered_memoryset = scored_memoryset.filter(
        lambda x: "bird" in x.value if isinstance(x.value, str) else True,
        "scored_filtered_collection",
    )
    # Then we get a new memoryset with the correct number of memories
    assert filtered_memoryset.uri == f"{scored_memoryset.repository.database_uri}#scored_filtered_collection"
    assert len(filtered_memoryset) == 5
    # And the old memoryset is unchanged
    assert len(scored_memoryset) == len(TEST_SCORED_DATASET)


def test_map_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 3
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(memoryset_length)))
    assert len(scored_memoryset) == memoryset_length
    time.sleep(0.01)
    # When we map the memoryset to a new memoryset with the words reversed
    reverse_words = lambda sentence: " ".join(reversed(sentence.split()))  # noqa: E731
    mapped_memoryset = scored_memoryset.map(
        lambda x: dict(value=reverse_words(x.value) if isinstance(x.value, str) else x.value),
        "scored_mapped_collection",
    )
    # Then we get a new memoryset with the correct number of memories
    assert mapped_memoryset.uri == f"{scored_memoryset.repository.database_uri}#scored_mapped_collection"
    assert len(mapped_memoryset) == memoryset_length
    # And the memories have the correct values
    assert all(x.value in [reverse_words(s) for s in SCORED_SENTENCES] for x in mapped_memoryset)
    # And the old memoryset is unchanged
    assert len(scored_memoryset) == memoryset_length
    assert all(x.value in SCORED_SENTENCES for x in scored_memoryset)
    # And the changed memories have been re-embedded
    assert all(x.embedding is not None for x in mapped_memoryset)
    # And the ids of the memories are preserved
    assert all(scored_memoryset.get(x.memory_id) is not None for x in mapped_memoryset)
    # And the memory versions are incremented
    assert all(x.memory_version == scored_memoryset[x.memory_id].memory_version + 1 for x in mapped_memoryset)
    # And the updated at timestamps are updated
    assert all(x.updated_at > scored_memoryset[x.memory_id].updated_at for x in mapped_memoryset)
    # And the edited at timestamps are updated
    assert all(x.edited_at > scored_memoryset[x.memory_id].updated_at for x in mapped_memoryset)


def test_clone_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 3
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(memoryset_length)))
    assert len(scored_memoryset) == memoryset_length
    # When we clone it to a new memoryset
    destination_uri = scored_memoryset.repository.database_uri + "#scored_destination_collection"
    cloned_memoryset = scored_memoryset.clone(destination_uri)
    # Then we get a new memoryset with the same number of memories
    assert cloned_memoryset.repository == scored_memoryset.repository_from_uri(destination_uri)
    assert len(cloned_memoryset) == memoryset_length
    # And the new memoryset has the same embedding model
    assert cloned_memoryset.embedding_model == scored_memoryset.embedding_model
    # And all memories are copied over with the same values and scores
    for memory in cloned_memoryset:
        original = scored_memoryset.get(memory.memory_id)
        assert original is not None
        assert memory.value == original.value
        assert memory.score == original.score
    # When we insert a new memory into the cloned memoryset
    cloned_memoryset.insert([ScoredMemoryInsert(value="My new sentence", score=0.95)])
    # Then the new memoryset has one more memory than the original memoryset
    assert len(cloned_memoryset) == memoryset_length + 1
    # And the original memoryset is unchanged
    assert len(scored_memoryset) == memoryset_length


def test_clone_to_different_repository_scored(scored_memoryset, temp_folder):
    # Given an in memory memoryset with some memories
    memoryset_length = 3
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(memoryset_length)))
    assert len(scored_memoryset) == memoryset_length
    # When we clone it to a Milvus memoryset
    milvus_memoryset = scored_memoryset.clone(
        MemorysetMilvusRepository(collection_name="cloned_memoryset", database_uri=f"{temp_folder}/milvus.db")
    )
    # Then we get a new memoryset with the same number of memories
    assert len(milvus_memoryset) == memoryset_length
    assert milvus_memoryset.embedding_model == scored_memoryset.embedding_model
    assert milvus_memoryset.uri == f"{temp_folder}/milvus.db#cloned_memoryset"


def test_reset_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    memoryset_length = 2
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(memoryset_length)))
    assert len(scored_memoryset) == memoryset_length
    # When we reset the memoryset
    scored_memoryset.reset()
    # Then the memoryset is empty
    assert len(scored_memoryset) == 0
    # But we still have the same embedding model
    assert scored_memoryset.embedding_model.path == EmbeddingModel.CLIP_BASE.path
    # And we can insert new memories
    scored_memoryset.insert([ScoredMemoryInsert(value="My new sentence", score=0.95)])
    assert len(scored_memoryset) == 1


def test_to_dataset_scored(scored_memoryset: ScoredMemoryset):
    # Given a memoryset with some memories
    scored_memoryset.insert(TEST_SCORED_DATASET.select(range(3)), show_progress_bar=False)
    # When a memoryset is converted to a dataset
    dataset = scored_memoryset.to_dataset(value_column="text", score_column="confidence")
    # Then the dataset has the correct length
    assert len(dataset) == len(scored_memoryset)
    # And the correct features
    assert isinstance(dataset.features["text"], Value)
    assert dataset.features["text"].dtype == "string"
    assert isinstance(dataset.features["confidence"], Value)
    assert dataset.features["confidence"].dtype == "float32"
    assert isinstance(dataset.features["memory_id"], Value)
    assert dataset.features["memory_id"].dtype == "string"
    assert isinstance(dataset.features["memory_version"], Value)
    assert dataset.features["memory_version"].dtype == "int64"
    assert dataset.features["embedding"] is not None
    assert isinstance(dataset.features["embedding"], Sequence)
    assert dataset.features["embedding"].feature.dtype == "float32"
    assert isinstance(dataset.features["source_id"], Value)
    assert dataset.features["source_id"].dtype == "string"
    assert isinstance(dataset.features["metadata"], dict)
    # And the memories are correct
    for i, sample in enumerate(dataset):
        assert isinstance(sample, dict)
        assert sample["text"] == scored_memoryset[i].value
        assert np.allclose(sample["confidence"], scored_memoryset[i].score)
        assert isinstance(sample["embedding"], list)
        assert len(sample["embedding"]) == scored_memoryset.embedding_model.embedding_dim
        assert np.allclose(np.array(sample["embedding"]), scored_memoryset[i].embedding)
        assert sample["memory_id"] == str(scored_memoryset[i].memory_id)
        assert sample["memory_version"] == scored_memoryset[i].memory_version
        assert sample["source_id"] == scored_memoryset[i].source_id
        assert sample["metadata"] == scored_memoryset[i].metadata


def test_lookup_count_too_large_scored(scored_memoryset: ScoredMemoryset):
    # When we lookup more memories than the memoryset contains
    with pytest.raises(ValueError):
        scored_memoryset.lookup(SCORED_SENTENCES[0], count=len(TEST_SCORED_DATASET) + 1)


@pytest.fixture()
def cascade_memoryset(memoryset: LabeledMemoryset) -> LabeledMemoryset:
    memoryset.insert(
        [
            # birds
            LabeledMemoryInsert(value="Birds fly south in the winter.", label=0),
            LabeledMemoryInsert(value="Many geese eat bugs from the pond.", label=0),
            LabeledMemoryInsert(value="Canaries are not normally found in coal mines.", label=0),
            LabeledMemoryInsert(value="Baby swans are called cygnets.", label=0),
            LabeledMemoryInsert(value="Cardinals and bluejays stand out in the snow.", label=0),
            # cats
            LabeledMemoryInsert(value="Tigers act like lazy housecats.", label=1),
            LabeledMemoryInsert(value="My cat prefers wet food.", label=1),
            LabeledMemoryInsert(value="Cat videos are the backbone of the internet.", label=1),
            LabeledMemoryInsert(value="Cats were once worshipped as gods.", label=1),
            LabeledMemoryInsert(value="Keep your cat's litter fresh to avoid accidents.", label=1),
        ]
    )

    return memoryset


def test_get_cascading_edits_suggestions(cascade_memoryset: LabeledMemoryset):
    """
    Test the `get_cascading_edits_suggestions` function to ensure it provides correct cascading edit suggestions.
    """
    # Given a memoryset with some labeled memories
    query_text = "Birds fly south in the winter."
    mislabeled_bird_text = "Eagles soar high in the sky."
    BIRD = 0
    CAT = 1
    cascade_memoryset.insert(
        [
            LabeledMemoryInsert(value=mislabeled_bird_text, label=CAT),  # mislabeled memory
        ]
    )
    memory = cascade_memoryset.query(filters=[("value", "==", query_text)])[0]  # Select the mislabeled memory

    # When we call `get_cascading_edits_suggestions` after changing the label of the first memory
    suggestions = get_cascading_edits_suggestions(
        cascade_memoryset,
        memory,
        old_label=CAT,
        new_label=BIRD,
        max_neighbors=8,
        max_validation_neighbors=4,
        similarity_threshold=0.5,
        only_if_has_old_label=True,
        exclude_if_new_label=True,
    )

    # Then the suggestions should include neighbors with the old label
    assert len(suggestions) == 1
    assert suggestions[0].neighbor.value == mislabeled_bird_text  # The original label of the mislabeled memory


def test_get_cascading_edits_suggestions_exclude_new_label(cascade_memoryset: LabeledMemoryset):
    """
    Test that `get_cascading_edits_suggestions` excludes neighbors with the new label when `exclude_if_new_label` is True.
    """
    query_text = "Birds fly south in the winter."
    mislabeled_bird_text = "Eagles soar high in the sky."
    mislabeled_cat_text = "Cats are great companions."
    BIRD = 0
    CAT = 1
    cascade_memoryset.insert(
        [
            LabeledMemoryInsert(value=mislabeled_bird_text, label=CAT),  # mislabeled BIRD memory
            LabeledMemoryInsert(value=mislabeled_cat_text, label=BIRD),  # mislabeled CAT memory
        ]
    )
    memory = cascade_memoryset.query(filters=[("value", "==", query_text)])[0]  # Select the mislabeled memory

    # When we call `get_cascading_edits_suggestions` after changing the label of the first memory
    suggestions = get_cascading_edits_suggestions(
        cascade_memoryset,
        memory,
        old_label=CAT,
        new_label=BIRD,
        max_neighbors=8,
        max_validation_neighbors=5,
        only_if_has_old_label=False,
        exclude_if_new_label=True,
    )

    # Then the suggestions should not include neighbors with the new label
    assert len(suggestions) == 1
    assert suggestions[0].neighbor.value == mislabeled_bird_text  # The original label of the mislabeled memory


def test_get_cascading_edits_suggestions_only_if_has_old_label(cascade_memoryset: LabeledMemoryset):
    """
    Test that `get_cascading_edits_suggestions` excludes neighbors with the new label when `exclude_if_new_label` is True.
    """
    query_text = "Birds fly south in the winter."
    mislabeled_bird_text = "Eagles soar high in the sky."
    mislabeled_cat_text = "Cats are great companions."
    BIRD = 0
    CAT = 1
    cascade_memoryset.insert(
        [
            LabeledMemoryInsert(value=mislabeled_bird_text, label=CAT),  # mislabeled BIRD memory
            LabeledMemoryInsert(value=mislabeled_cat_text, label=BIRD),  # mislabeled CAT memory
        ]
    )
    memory = cascade_memoryset.query(filters=[("value", "==", query_text)])[0]  # Select the mislabeled memory

    # When we call `get_cascading_edits_suggestions` after changing the label of the first memory
    suggestions = get_cascading_edits_suggestions(
        cascade_memoryset,
        memory,
        old_label=CAT,
        new_label=BIRD,
        max_neighbors=8,
        max_validation_neighbors=5,
        only_if_has_old_label=True,
        exclude_if_new_label=False,
    )

    # Then the suggestions should not include neighbors with the new label
    assert len(suggestions) == 1
    assert suggestions[0].neighbor.value == mislabeled_bird_text  # The original label of the mislabeled memory


def test_get_cascading_edits_suggestions_similarity_threshold(cascade_memoryset: LabeledMemoryset):
    """
    Test that `get_cascading_edits_suggestions` respects the similarity threshold.
    """
    query_text = "Birds fly south in the winter."
    mislabeled_similar_bird_text = "Birds migrate south during the winter months."
    mislabeled_dissimilar_bird_text = "Penguins are flightless birds that swim in the ocean."
    BIRD = 0
    CAT = 1
    cascade_memoryset.insert(
        [
            LabeledMemoryInsert(value=mislabeled_similar_bird_text, label=CAT),  # mislabeled BIRD memory
            LabeledMemoryInsert(value=mislabeled_dissimilar_bird_text, label=CAT),  # mislabeled BIRD memory
        ]
    )
    memory = cascade_memoryset.query(filters=[("value", "==", query_text)])[0]  # Select the mislabeled memory

    # When we call `get_cascading_edits_suggestions` after changing the label of the first memory
    suggestions = get_cascading_edits_suggestions(
        cascade_memoryset,
        memory,
        old_label=CAT,
        new_label=BIRD,
        max_neighbors=9,
        max_validation_neighbors=5,
        similarity_threshold=0.9,  # Set a high similarity threshold
    )

    # Then the suggestions should not include neighbors with the new label
    assert len(suggestions) == 1
    assert suggestions[0].neighbor.value == mislabeled_similar_bird_text  # The original label of the mislabeled memory


def test_get_cascading_edits_suggestions_cooldown(cascade_memoryset: LabeledMemoryset):
    """
    Test that `get_cascading_edits_suggestions` respects the suggestion cooldown time.
    """
    query_text = "Birds fly south in the winter."
    mislabeled_bird_text = "Eagles soar high in the sky."
    BIRD = 0
    CAT = 1
    cascade_memoryset.insert(
        [
            LabeledMemoryInsert(value=mislabeled_bird_text, label=CAT),  # mislabeled memory
        ]
    )
    memory = cascade_memoryset.query(filters=[("value", "==", query_text)])[0]  # Select the mislabeled memory

    # When we call `get_cascading_edits_suggestions` after changing the label of the first memory
    suggestions = get_cascading_edits_suggestions(
        cascade_memoryset,
        memory,
        old_label=CAT,
        new_label=BIRD,
        max_neighbors=8,
        max_validation_neighbors=5,
    )

    # Then the suggestions should include neighbors with the old label
    assert len(suggestions) == 1
    assert suggestions[0].neighbor.value == mislabeled_bird_text  # The original label of the mislabeled memory

    # Wait for cooldown time to expire
    time.sleep(1)

    # Call again to ensure suggestions are still valid after cooldown
    suggestions_after_cooldown = get_cascading_edits_suggestions(
        cascade_memoryset,
        memory,
        old_label=CAT,
        new_label=BIRD,
        max_neighbors=8,
        max_validation_neighbors=5,
        suggestion_cooldown_time=3600,  # Set a cooldown time of 1 second
    )

    assert len(suggestions_after_cooldown) == 0


@skip_in_ci("downloading e5-large fails in CI")
def test_custom_prompts():
    # Given memorysets that use the same embedding model but different prompts

    embedding_model = EmbeddingModel.BGE_BASE

    memoryset_with_prompts = LabeledMemoryset(
        "memory:#test_custom_prompts",
        embedding_model=embedding_model,
        document_prompt="Represent this document for retrieval: ",
        query_prompt="Represent this query for retrieval: ",
    )

    memoryset_without_prompts = LabeledMemoryset(
        "memory:#test_custom_prompts_no_prompts",
        embedding_model=embedding_model,
    )

    # Verify that both memorysets share the same embedding model instance
    assert memoryset_with_prompts.embedding_model is memoryset_without_prompts.embedding_model

    # When we insert some memories
    memories = [
        LabeledMemoryInsert(value=SENTENCES[2], label=0),  # "A bird brings the fence."
        LabeledMemoryInsert(value=SENTENCES[5], label=0),  # "A bird brings the mountain."
        LabeledMemoryInsert(value=SENTENCES[1], label=1),  # "The cat fixes a theory."
        LabeledMemoryInsert(value=SENTENCES[6], label=1),  # "The cat finds a theory."
    ]
    memoryset_with_prompts.insert(memories)
    memoryset_without_prompts.insert(memories)

    # Then the memories should be stored with different embeddings due to custom prompts
    results_with_prompts = memoryset_with_prompts.lookup("A bird flying", count=2)
    results_without_prompts = memoryset_without_prompts.lookup("A bird flying", count=2)

    # Verify that both memorysets return semantically relevant results
    assert len(results_with_prompts) == 2
    assert len(results_without_prompts) == 2
    assert "bird" in str(results_with_prompts[0].value)
    assert "bird" in str(results_with_prompts[1].value)
    assert "bird" in str(results_without_prompts[0].value)
    assert "bird" in str(results_without_prompts[1].value)

    # Verify that the embeddings are different due to custom prompts
    assert not np.array_equal(results_with_prompts[0].embedding, results_without_prompts[0].embedding)
    assert not np.array_equal(results_with_prompts[1].embedding, results_without_prompts[1].embedding)
