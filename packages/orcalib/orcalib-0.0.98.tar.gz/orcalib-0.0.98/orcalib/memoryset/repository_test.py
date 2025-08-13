import base64
import io
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Generator, cast, get_args

import numpy as np
import pytest
from PIL import Image, ImageChops
from pymilvus import DataType, MilvusClient
from uuid_utils.compat import UUID, uuid4, uuid7

from ..embedding import EmbeddingModel
from .memory_types import InputType, LabeledMemory, MemoryMetrics, ScoredMemory, Vector
from .repository import FilterItem, IndexType, MemorysetConfig, MemorysetRepository
from .repository_memory import MemorysetInMemoryRepository
from .repository_milvus import MemorysetMilvusRepository

# To enable tests against a milvus server instance, set MILVUS_SERVER_URL = "http://localhost:19530"
# Keep this set to None by default to avoid requiring a dockerized milvus instance for tests
MILVUS_SERVER_URL = os.getenv("MILVUS_SERVER_URL")

MILVUS_LITE_INDEX_TYPES = ["FLAT", "IVF_FLAT"]
MILVUS_SERVER_INDEX_TYPES = get_args(IndexType)

BACKEND_TYPES = ["in-memory", "milvus-lite"] + (["milvus-server"] if MILVUS_SERVER_URL else [])

BACKEND_TYPES_WITH_INDEX_TYPES = (
    [("in-memory", "FLAT")]
    + [("milvus-lite", index_type) for index_type in MILVUS_LITE_INDEX_TYPES]
    + ([("milvus-server", index_type) for index_type in MILVUS_SERVER_INDEX_TYPES] if MILVUS_SERVER_URL else [])
)

MEMORYSET_CONFIG = MemorysetConfig(
    memory_type="labeled",
    label_names=["positive", "negative", "neutral"],
    embedding_dim=EmbeddingModel.CLIP_BASE.embedding_dim,
    embedding_model_name=EmbeddingModel.CLIP_BASE.path,
    embedding_model_max_seq_length_override=None,
    schema_version=-1,  # will be set by the repository, this is to test that it is overridden
)


def _create_labeled_memory(
    value: InputType,
    label: int,
    *,
    embedding: Vector | None = None,
    source_id: str | None = None,
    label_name: str | None = None,
    metadata: dict = {},
    metrics: MemoryMetrics | None = None,
    memory_id: UUID | None = None,
    memory_version: int = 1,
    created_at: datetime | None = None,
) -> LabeledMemory:
    return LabeledMemory(
        value=value,
        label=label,
        embedding=embedding if embedding is not None else EmbeddingModel.CLIP_BASE.embed(value),
        memory_id=memory_id or uuid7(),
        memory_version=memory_version,
        source_id=source_id,
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=created_at or datetime.now(timezone.utc),
        edited_at=created_at or datetime.now(timezone.utc),
        label_name=label_name,
        metrics=metrics if metrics is not None else MemoryMetrics(),
        metadata=metadata,
    )


TEXT_DATA: list[LabeledMemory] = [
    _create_labeled_memory(text, label, metadata={"text": text, "label": label}, source_id=str(i))
    for i, (text, label) in enumerate(
        [
            ("I'm over the moon with how things turned out!", 0),
            ("This is the happiest I've felt in a long time.", 0),
            ("My heart feels so full and content.", 0),
            ("Everything feels perfect right now, I couldn't ask for more.", 0),
            ("I am so fed up with dealing with this over and over.", 1),
            ("Why does it always feel like I'm hitting a brick wall?", 1),
            ("I'm getting really tired of this never-ending cycle.", 1),
            ("It's so frustrating when things just never go my way.", 1),
        ]
    )
]


@pytest.fixture()
def temp_folder() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(params=[f"{repo_type}::{index_type}" for repo_type, index_type in BACKEND_TYPES_WITH_INDEX_TYPES])
def repo_params(temp_folder, request) -> tuple[str, str, str, str]:
    repo_type, index_type = request.param.split("::")

    match repo_type:
        case "in-memory":
            # need a unique collection name here since we don't use the temp_folder
            return repo_type, "", f"test_{uuid4().hex[:8]}", index_type
        case "milvus-lite":
            return repo_type, f"{temp_folder}/milvus.db", f"test_milvus_lite_{index_type}", index_type
        case "milvus-server":
            assert MILVUS_SERVER_URL is not None
            # need a unique collection name here since we don't use the temp_folder
            return repo_type, MILVUS_SERVER_URL, f"test_milvus_server_{index_type}_{uuid4().hex[:8]}", index_type
        case _:
            raise ValueError(f"Invalid repository type: {request.param}")


@pytest.fixture()
def disconnected_repository_with_config(
    repo_params,
) -> Generator[tuple[MemorysetRepository, MemorysetConfig], None, None]:
    repo_type, database_uri, collection_name, index_type = repo_params

    match repo_type:
        case "in-memory":
            repository = MemorysetInMemoryRepository(collection_name=collection_name)
        case "milvus-lite":
            repository = MemorysetMilvusRepository(database_uri=database_uri, collection_name=collection_name)
        case "milvus-server":
            # For tests, we use "Session" consistency level to ensure all writes from the same session are visible.
            repository = MemorysetMilvusRepository(
                database_uri=database_uri,
                collection_name=collection_name,
                consistency_level="Session",
            )
        case _:
            raise ValueError(f"Invalid repository type: {repo_type}")

    config = MEMORYSET_CONFIG.model_copy(
        update={
            "index_type": index_type,
            "index_params": {},
        }
    )

    yield repository, config
    repository.drop()


@pytest.fixture()
def repository(disconnected_repository_with_config) -> MemorysetRepository:
    disconnected_repository, config = disconnected_repository_with_config
    return disconnected_repository.connect(config)


def test_config_collection(disconnected_repository_with_config):
    disconnected_repository, disconnected_config = disconnected_repository_with_config

    # When getting config for a new storage backend that has never been connected
    config = disconnected_repository.get_config()
    # Then the config is None
    assert config is None
    assert disconnected_repository.collection_name not in disconnected_repository.get_collection_names()
    # When the storage backend is connected
    connected_repository = disconnected_repository.connect(disconnected_config)
    # Then the config is not None anymore
    config = connected_repository.get_config()
    assert config is not None
    for m in disconnected_config.__dict__.keys():
        # And the schema version cannot be overwritten
        if m == "schema_version":
            assert disconnected_config.schema_version != connected_repository.SCHEMA_VERSION
            assert getattr(config, m) == connected_repository.SCHEMA_VERSION
        else:
            # And the other config attributes are set as passed
            assert getattr(config, m) == getattr(disconnected_config, m)

    # check index_type is set
    assert connected_repository.get_config().index_type == disconnected_config.index_type
    assert connected_repository.get_config().index_params == disconnected_config.index_params

    # And the collection name is set
    assert connected_repository.collection_name in connected_repository.get_collection_names()
    # When reconnecting to the storage backend without connecting
    RepositoryImplementation = connected_repository.__class__
    database_uri = connected_repository.database_uri
    collection_name = connected_repository.collection_name
    del disconnected_repository
    del connected_repository
    reconnected_repository = RepositoryImplementation(database_uri=database_uri, collection_name=collection_name)
    # Then the config is not None
    config = reconnected_repository.get_config()
    assert config is not None


def test_reload_repository(disconnected_repository_with_config):
    disconnected_repository, config = disconnected_repository_with_config

    repository = disconnected_repository.connect(config)

    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    RepositoryImplementation = repository.__class__
    database_uri = repository.database_uri
    collection_name = repository.collection_name
    del repository
    # When we reconnect to the storage backend
    reconnected_repository = RepositoryImplementation(
        database_uri=database_uri, collection_name=collection_name
    ).connect(config)
    # Then we can access its memories
    assert reconnected_repository.count() == len(TEXT_DATA)


def test_drop_collection(disconnected_repository_with_config):
    disconnected_repository, disconnected_config = disconnected_repository_with_config
    repository = disconnected_repository.connect(disconnected_config)

    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    # When we drop the storage backend
    repository.drop()
    # Then we can no longer access its memories
    with pytest.raises(RuntimeError):
        repository.count()
    # When we re instantiate the storage backend
    RepositoryImplementation = repository.__class__
    database_uri = repository.database_uri
    collection_name = repository.collection_name
    del repository
    reconnected_repository = RepositoryImplementation(database_uri=database_uri, collection_name=collection_name)
    # Then the storage backend does not exist anymore
    config = reconnected_repository.get_config()
    assert config is None
    # And it has no memories after reconnecting
    assert reconnected_repository.connect(disconnected_config).count() == 0


def test_reset_repository(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    # When we reset the storage backend
    repository.reset(MEMORYSET_CONFIG)
    # Then the storage backend is empty
    assert repository.count() == 0


def test_get(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    # When we get a memory by its memory_id
    memory = repository.get(TEXT_DATA[0].memory_id)
    # Then we get the correct memory
    assert isinstance(memory, LabeledMemory)
    assert memory.value == TEXT_DATA[0].value
    assert memory.label == TEXT_DATA[0].label
    assert memory.label_name == MEMORYSET_CONFIG.label_names[TEXT_DATA[0].label]
    assert memory.source_id == "0"
    assert np.allclose(memory.embedding, TEXT_DATA[0].embedding)


def test_get_multi(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    # When we get memories by their memory_ids
    memory_ids = [m.memory_id for m in TEXT_DATA] + [uuid7()]  # add a non-existent memory_id
    memories = repository.get_multi(memory_ids)
    # Then we get the correct memories
    assert len(memories) == len(TEXT_DATA)

    for uuid, memory in memories.items():
        i = int(memory.source_id)
        assert isinstance(memory, LabeledMemory)
        assert memory.memory_id == uuid
        assert memory.value == TEXT_DATA[i].value
        assert memory.label == TEXT_DATA[i].label
        assert memory.label_name == MEMORYSET_CONFIG.label_names[TEXT_DATA[i].label]
        assert memory.source_id == str(i)
        assert np.allclose(memory.embedding, TEXT_DATA[i].embedding)


def test_get_not_found(repository):
    # When trying to get a memory that does not exist
    memory = repository.get(uuid7())
    # Then None is returned
    assert memory is None


def test_insert(repository):
    # When we insert a memory
    repository.insert(
        [
            _create_labeled_memory(
                value=TEXT_DATA[0].value,
                label=TEXT_DATA[0].label,
                memory_id=TEXT_DATA[0].memory_id,
                embedding=TEXT_DATA[0].embedding,
            ),
            _create_labeled_memory(
                value="åß∂ƒ©" + "a" * 59995,  # 60000 characters, more bytes than the max text length
                label=TEXT_DATA[1].label,
                memory_id=TEXT_DATA[1].memory_id,
                embedding=TEXT_DATA[1].embedding,
            ),
        ]
    )
    # Then the memory is inserted
    assert repository.count() == 2
    # And the inserted memory is returned and has the correct values
    inserted_memory = repository.get(TEXT_DATA[0].memory_id)
    assert inserted_memory is not None
    assert inserted_memory.value == TEXT_DATA[0].value
    assert inserted_memory.label == TEXT_DATA[0].label
    assert inserted_memory.label_name == MEMORYSET_CONFIG.label_names[TEXT_DATA[0].label]
    assert inserted_memory.memory_version == 1
    assert inserted_memory.memory_id == TEXT_DATA[0].memory_id
    if isinstance(repository, MemorysetMilvusRepository):
        # On Milvus, the second memory is trimmed to be <= the MAX_TEXT_LENGTH
        trimmed_memory = repository.get(TEXT_DATA[1].memory_id)
        assert trimmed_memory is not None
        assert len((str(trimmed_memory.value).encode("utf-8"))) <= MemorysetMilvusRepository.MAX_TEXT_LENGTH


def test_insert_error(repository):
    # Given a storage backend with no data
    assert repository.count() == 0
    # When we attempt upsert a list of memories with bad data
    memories = [
        _create_labeled_memory(
            value="new_value",
            label=2,
            memory_id=TEXT_DATA[0].memory_id,
            source_id="new_source_id",
            memory_version=2,
            embedding=TEXT_DATA[0].embedding,
        ),
        _create_labeled_memory(
            embedding=np.array([1.0], dtype=np.float32),
            value="new_value_2",
            label=2,
            memory_id=uuid7(),
            source_id="new_source_id_2",
        ),
    ]

    # Then an error is raised
    with pytest.raises(Exception):
        repository.insert(memories)

    # Milvus-lite does not handle upsert failures correctly
    # The failing row gets deleted, so skip the test if we are using milvus-lite
    # This is not a priority for us to fix atm
    if (isinstance(repository, MemorysetMilvusRepository) and not repository.is_local_database) or isinstance(
        repository, MemorysetInMemoryRepository
    ):
        # and none of the memories are inserted or updated
        memories = repository.list()
        assert len(memories) == 0
        for i, m in enumerate(memories):
            assert m.value == TEXT_DATA[i].value
            assert m.memory_id == TEXT_DATA[i].memory_id
            assert m.memory_version == TEXT_DATA[i].memory_version
            assert isinstance(m, LabeledMemory)
            assert m.label == TEXT_DATA[i].label
            assert m.label_name == MEMORYSET_CONFIG.label_names[TEXT_DATA[i].label]


def test_upsert_multi(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    # When we upsert a list of memories
    memories = [
        _create_labeled_memory(
            value="new_value",
            label=2,
            memory_id=TEXT_DATA[0].memory_id,
            source_id="new_source_id",
            embedding=TEXT_DATA[0].embedding,
            memory_version=2,
            metrics={"is_duplicate": True},
        ),
        _create_labeled_memory(
            value="new_value_2",
            label=2,
            source_id="new_source_id_2",
            embedding=TEXT_DATA[0].embedding,
        ),
    ]

    updated_memories_dict = repository.upsert_multi(memories)

    updated_memories = [updated_memories_dict[m.memory_id] for m in memories]

    # Then the memories are updated
    assert repository.count() == len(TEXT_DATA) + 1
    assert len(updated_memories) == 2
    assert updated_memories[0].value == "new_value"
    assert updated_memories[0].source_id == "new_source_id"
    assert updated_memories[0].memory_version == 2
    assert updated_memories[0].metrics == {"is_duplicate": True}
    assert updated_memories[1].value == "new_value_2"
    assert updated_memories[1].source_id == "new_source_id_2"
    assert updated_memories[1].memory_version == 1


def test_upsert_multi_error(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    # When we attempt upsert a list of memories with bad data
    memories = [
        _create_labeled_memory(
            value="new_value",
            label=2,
            memory_id=TEXT_DATA[0].memory_id,
            source_id="new_source_id",
            memory_version=2,
            embedding=TEXT_DATA[0].embedding,
        ),
        _create_labeled_memory(
            embedding=np.array([1.0], dtype=np.float32),
            value="new_value_2",
            label=2,
            memory_id=uuid7(),
            source_id="new_source_id_2",
        ),
    ]

    # Then an error is raised
    with pytest.raises(Exception):
        repository.upsert_multi(memories)

    # Milvus-lite does not handle upsert failures correctly
    # The failing row gets deleted, so skip the test if we are using milvus-lite
    # This is not a priority for us to fix atm
    if (isinstance(repository, MemorysetMilvusRepository) and not repository.is_local_database) or isinstance(
        repository, MemorysetInMemoryRepository
    ):
        # and none of the memories are inserted or updated
        memories = repository.list()
        assert len(memories) == len(TEXT_DATA)
        for i, m in enumerate(memories):
            assert m.value == TEXT_DATA[i].value
            assert m.memory_id == TEXT_DATA[i].memory_id
            assert m.memory_version == TEXT_DATA[i].memory_version
            assert isinstance(m, LabeledMemory)
            assert m.label == TEXT_DATA[i].label
            assert m.label_name == MEMORYSET_CONFIG.label_names[TEXT_DATA[i].label]


def test_update(repository):
    # Given a memory already in the storage backend
    existing_memory = repository.upsert(TEXT_DATA[0])
    assert repository.count() == 1
    assert existing_memory is not None
    # When we update the memory
    updated_memory = repository.upsert(
        LabeledMemory(**{**existing_memory.model_dump(), "value": "updated_value", "label": 2, "memory_version": 2})
    )
    # Then no new memory is inserted
    assert repository.count() == 1
    # And the memory has the updated value
    assert updated_memory is not None
    assert updated_memory.value == "updated_value"
    assert updated_memory.label == 2
    assert updated_memory.label_name == MEMORYSET_CONFIG.label_names[2]
    assert updated_memory.memory_version == 2


def test_delete(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    # When we delete a memory
    res = repository.delete(TEXT_DATA[0].memory_id)
    # Then the memory is deleted
    assert res is True
    assert repository.get(TEXT_DATA[0].memory_id) is None
    assert repository.count() == len(TEXT_DATA) - 1


def test_delete_not_found(repository):
    # When we delete a memory that does not exist
    res = repository.delete(uuid7())
    # Then False is returned
    assert res is False


def test_delete_multi(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    # When we delete a memory
    res = repository.delete_multi([TEXT_DATA[0].memory_id, TEXT_DATA[1].memory_id])
    # Then the memory is deleted
    assert res is True
    assert repository.get(TEXT_DATA[0].memory_id) is None
    assert repository.get(TEXT_DATA[1].memory_id) is None
    assert repository.count() == len(TEXT_DATA) - 2


def test_insert_and_lookup_text(repository):
    # Given a storage backend with some text memories
    repository.insert(TEXT_DATA)
    # When we look up the query vector
    memory_lookups = repository.lookup([TEXT_DATA[0].embedding], 4, use_cache=False)
    # Then we get a list of lists of memories
    assert isinstance(memory_lookups, list)
    assert len(memory_lookups) == 1
    assert isinstance(memory_lookups[0], list)
    assert len(memory_lookups[0]) == 4
    # And the first memory in the list is the one with the matching text
    assert isinstance(memory_lookups[0][0].value, str)
    assert memory_lookups[0][0].value == TEXT_DATA[0].value
    # And the lookup score is high
    assert memory_lookups[0][0].lookup_score >= 0.99
    # And the embedding is a numpy array of the correct shape and type
    assert isinstance(memory_lookups[0][0].embedding, np.ndarray)
    assert memory_lookups[0][0].embedding.shape == (MEMORYSET_CONFIG.embedding_dim,)
    assert memory_lookups[0][0].embedding.dtype == np.float32
    # And the label and label name are correct
    assert memory_lookups[0][0].label == TEXT_DATA[0].label
    assert memory_lookups[0][0].label_name == MEMORYSET_CONFIG.label_names[TEXT_DATA[0].label]


def test_lookup_caching(repository):
    if isinstance(repository, MemorysetInMemoryRepository):
        pytest.skip("In-memory repository does not support caching")

    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    # When we lookup a few queries
    k = 4
    queries = [m.embedding for m in TEXT_DATA]
    memory_lookups = repository.lookup(queries, k, use_cache=True)
    assert len(memory_lookups) == len(queries)
    # Then the results are stored in the cache
    assert repository._cache_size() == len(queries)
    assert all(repository._get_cache_item(repository._get_cache_key(q, k)) is not None for q in queries)
    # When we lookup a subset of those queries again
    start = perf_counter()
    cached_memory_lookups = repository.lookup(queries[:6], k, use_cache=True)
    cached_duration = perf_counter() - start
    repository._clear_cache()
    assert repository._cache_size() == 0
    start = perf_counter()
    uncached_memory_lookups = repository.lookup(queries[:6], k, use_cache=True)
    uncached_duration = perf_counter() - start
    # Then the lookup is faster
    assert cached_duration < uncached_duration
    # And the cached results are the same as the uncached results
    assert all(
        all(
            cached_memory_lookups[i][j].value == uncached_memory_lookups[i][j].value
            for j in range(len(cached_memory_lookups[i]))
        )
        for i in range(len(cached_memory_lookups))
    )
    # When we make a lookup that can be resolved from the cache entirely
    assert all(repository._get_cache_item(repository._get_cache_key(q, k)) is not None for q in queries[:4])
    cached_memory_lookups = repository.lookup(queries[:4], k, use_cache=True)
    # Then it works as expected
    assert len(cached_memory_lookups) == 4


def test_insert_and_lookup_image(repository):
    # Given a storage backend with a few PNG images
    images = [
        Image.open(io.BytesIO(base64.b64decode(base64_string)))
        for base64_string in [
            "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg==",  # red circle
            "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAALUlEQVR4nGP8//8/Aw7AhMxhbGTEKYdTH0QTslYi9CErh7MJ6UNzHsJuPP4DANsWCaCKZRMuAAAAAElFTkSuQmCC",  # green triangle
            "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAKElEQVR4nM2PsQ0AMAyDcJX/XyYP1HtYEQNRKQyQfITyWgSn3ADtcAGzGQcROl7AigAAAABJRU5ErkJggg==",  # blue square
        ]
    ]
    repository.insert([_create_labeled_memory(value=image, label=i) for i, image in enumerate(images)])
    # When we look up the first image by its embedding
    memory_lookups = repository.lookup(EmbeddingModel.CLIP_BASE.embed([images[0]]), 2, use_cache=False)
    # Then we get a list of lists of memories
    assert isinstance(memory_lookups, list)
    assert len(memory_lookups) == 1
    assert isinstance(memory_lookups[0], list)
    assert len(memory_lookups[0]) == 2
    # And the first memory in the list is the one with the matching image
    assert memory_lookups[0][0].label == 0
    assert memory_lookups[0][0].label_name == MEMORYSET_CONFIG.label_names[0]
    # And the lookup score is high
    assert memory_lookups[0][0].lookup_score >= 0.99
    # And the image value is returned properly
    assert isinstance(memory_lookups[0][0].value, Image.Image)
    assert ImageChops.difference(memory_lookups[0][0].value, images[0]).getbbox() is None


def test_insert_and_lookup_timeseries(repository):
    # Given a storage backend with some timeseries memories
    timeseries_memories = [
        _create_labeled_memory(
            value=np.random.rand(10, 2).astype(np.float32),
            label=i,
            embedding=np.random.rand(EmbeddingModel.CLIP_BASE.embedding_dim).astype(np.float32),
        )
        for i in range(3)
    ]
    repository.insert(timeseries_memories)
    # When we look up the query vector
    memory_lookups = repository.lookup([timeseries_memories[0].embedding], 2, use_cache=False)
    # Then we get a list of lists of memories
    assert isinstance(memory_lookups, list)
    assert len(memory_lookups) == 1
    assert isinstance(memory_lookups[0], list)
    assert len(memory_lookups[0]) == 2
    # And the first memory in the list is the one with the matching timeseries
    assert memory_lookups[0][0].label == 0
    assert memory_lookups[0][0].label_name == MEMORYSET_CONFIG.label_names[0]
    # And the timeseries value is returned properly
    assert isinstance(memory_lookups[0][0].value, np.ndarray)
    assert memory_lookups[0][0].value.shape == (10, 2)
    assert memory_lookups[0][0].value.dtype == np.float32
    assert np.allclose(memory_lookups[0][0].value, cast(np.ndarray, timeseries_memories[0].value))


def test_count_filters(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    # When we count the memories with a filter
    count = repository.count(filters=[FilterItem(field=("label",), op="==", value=0)])
    # Then the count is correct
    assert count == 4


def test_repository_equality():
    # Given two storage backends with the same database URI and collection name
    repository1 = MemorysetInMemoryRepository(database_uri="memory:", collection_name="test")
    repository2 = MemorysetInMemoryRepository(database_uri="memory:", collection_name="test")
    # And a repository of a different type
    repository3 = MemorysetMilvusRepository(database_uri="test", collection_name="test")
    # And a repository with a different database URI
    repository4 = MemorysetMilvusRepository(database_uri="test2", collection_name="test")
    # And a repository with a different collection name
    repository5 = MemorysetInMemoryRepository(collection_name="test2")
    # Then the same repositories are equal
    assert repository1 == repository2
    # And different repositories are not equal
    assert repository1 != repository3
    assert repository1 != repository4
    assert repository1 != repository5


def test_update_config(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    # When we update the config with new label names
    new_config = MemorysetConfig(
        memory_type="labeled",
        label_names=["new_positive", "new_negative"],
        embedding_dim=MEMORYSET_CONFIG.embedding_dim,
        embedding_model_name=MEMORYSET_CONFIG.embedding_model_name,
        embedding_model_max_seq_length_override=MEMORYSET_CONFIG.embedding_model_max_seq_length_override,
        schema_version=2,
        index_type="FLAT",
        index_params={"new_param": "new_value"},
    )
    repository.update_config(new_config)
    # Then the config is updated
    updated_config = repository.get_config()
    assert updated_config is not None
    assert updated_config.label_names == ["new_positive", "new_negative"]
    # And the index type and vector index params are updated
    assert updated_config.index_type == "FLAT"
    assert updated_config.index_params == {"new_param": "new_value"}
    # But the schema version cannot be updated
    assert updated_config.schema_version == repository.SCHEMA_VERSION
    # And the memories have the new label names
    memories = repository.list()
    assert all(m.label_name in ["new_positive", "new_negative"] for m in memories)


def test_list(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    # When we get the list of memories
    memories = repository.list()
    # Then we get a list of all the memories
    assert len(memories) == len(TEXT_DATA)
    # And the memories are returned in order of creation
    for i in range(len(TEXT_DATA)):
        assert memories[i].source_id == TEXT_DATA[i].source_id
    # And the memories have the correct value, embedding, and embedding shape and type
    for value in memories:
        assert isinstance(value, LabeledMemory)
        assert isinstance(value.memory_id, UUID)
        assert isinstance(value.memory_version, int)
        assert isinstance(value.value, str)
        assert value.label in [0, 1]
        assert value.label_name in ["positive", "negative"]
        assert isinstance(value.embedding, np.ndarray)
        assert value.embedding.shape == (MEMORYSET_CONFIG.embedding_dim,)
        assert value.embedding.dtype == np.float32


def test_iterator(repository):
    repository.insert(TEXT_DATA)
    assert repository.count() == len(TEXT_DATA)
    memories = list(repository.iterator())
    assert len(memories) == len(TEXT_DATA)
    for i in range(len(TEXT_DATA)):
        assert memories[i].source_id == TEXT_DATA[i].source_id
        assert memories[i].value == TEXT_DATA[i].value
        assert memories[i].label == TEXT_DATA[i].label
        assert memories[i].label_name == MEMORYSET_CONFIG.label_names[TEXT_DATA[i].label]
        assert np.allclose(memories[i].embedding, TEXT_DATA[i].embedding)


def test_list_with_offset_and_limit(repository):
    # Given a storage backend with some data
    repository.insert(TEXT_DATA)
    # When we get a list of memories with an offset and limit
    memories = repository.list(offset=1, limit=2)
    # Then we get a list of the correct memories
    assert len(memories) == 2
    # And the memories come back in the same order every time
    memories_2 = repository.list(offset=1, limit=2)
    assert memories[0].value == memories_2[0].value
    assert memories[1].value == memories_2[1].value


def test_simple_list_with_filters_memory(repository):
    # Given a storage backend with some data
    mems_to_insert = [
        _create_labeled_memory(
            value="red",
            label=0,
            metadata={
                "id": "red",
                "score": 0.9,
                "is_primary": True,
            },
            embedding=EmbeddingModel.CLIP_BASE.embed(["red"])[0],
            source_id="source_1",
            memory_id=uuid7(),
        ),
        _create_labeled_memory(
            value="orange",
            label=1,
            metadata={"id": "orange", "score": 0.5, "is_primary": False},
            embedding=EmbeddingModel.CLIP_BASE.embed(["orange"])[0],
            source_id="source_2",
            memory_id=uuid7(),
        ),
        _create_labeled_memory(
            value="blue",
            label=2,
            metadata={"id": "blue", "score": 0.2, "is_primary": True},
            embedding=EmbeddingModel.CLIP_BASE.embed(["blue"])[0],
            source_id=None,
            memory_id=uuid7(),
        ),
    ]
    repository.insert(mems_to_insert)

    # Not using pytest.mark.parametrize for performance reasons, we want to insert the data once for all test cases

    ##### equals (==) filter #####
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op="==", value=0)])
    assert len(memories) == 1
    assert memories[0].value == "red"


def test_list_filters_memory(repository):
    # Given a storage backend with some data
    mems_to_insert = [
        _create_labeled_memory(
            value="red",
            label=0,
            metadata=dict(id="red", score=0.9),
            metrics=MemoryMetrics(is_duplicate=True),
            embedding=EmbeddingModel.CLIP_BASE.embed(["red"])[0],
            source_id="source_1",
            memory_id=uuid7(),
            created_at=datetime.now() - timedelta(seconds=3),
        ),
        _create_labeled_memory(
            value="orange",
            label=1,
            metadata=dict(id="orange", score=0.5),
            metrics=MemoryMetrics(),
            embedding=EmbeddingModel.CLIP_BASE.embed(["orange"])[0],
            source_id="source_2",
            memory_id=uuid7(),
            created_at=datetime.now() - timedelta(seconds=2),
        ),
        _create_labeled_memory(
            value="blue",
            label=2,
            metadata=dict(id="blue", score=0.2),
            metrics=MemoryMetrics(is_duplicate=True),
            embedding=EmbeddingModel.CLIP_BASE.embed(["blue"])[0],
            source_id=None,
            memory_id=uuid7(),
            created_at=datetime.now() - timedelta(seconds=1),
        ),
    ]
    repository.insert(mems_to_insert)

    # Not using pytest.mark.parametrize for performance reasons, we want to insert the data once for all test cases

    ##### equals (==) filter #####
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op="==", value=0)])
    assert len(memories) == 1
    assert memories[0].value == "red"
    # UUID column
    memories = repository.list(
        filters=[FilterItem(field=("memory_id",), op="==", value=str(mems_to_insert[0].memory_id))]
    )
    assert len(memories) == 1
    assert memories[0].value == "red"
    # string column
    memories = repository.list(filters=[FilterItem(field=("value",), op="==", value="red")])
    assert len(memories) == 1
    assert memories[0].value == "red"
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op="==", value=0.9)])
    assert len(memories) == 1
    assert memories[0].value == "red"
    # bool column
    memories = repository.list(filters=[FilterItem(field=("metrics", "is_duplicate"), op="==", value=True)])
    assert len(memories) == 2
    assert all(m.value in ["red", "blue"] for m in memories)
    # datetime column
    memories = repository.list(filters=[FilterItem(field=("created_at",), op="==", value=mems_to_insert[0].created_at)])
    assert len(memories) == 1
    assert memories[0].value == "red"
    # None value
    memories = repository.list(filters=[FilterItem(field=("source_id",), op="==", value=None)])
    assert len(memories) == 1
    assert memories[0].value == "blue"
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op="==", value="value")])
    assert len(memories) == 0

    ##### not equals (!=) filter #####
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op="!=", value=0)])
    assert len(memories) == 2
    assert all(m.value in ["blue", "orange"] for m in memories)
    # UUID column
    memories = repository.list(
        filters=[FilterItem(field=("memory_id",), op="!=", value=str(mems_to_insert[0].memory_id))]
    )
    assert len(memories) == 2
    assert all(m.value in ["blue", "orange"] for m in memories)
    # string column
    memories = repository.list(filters=[FilterItem(field=("value",), op="!=", value="red")])
    assert len(memories) == 2
    assert all(m.value in ["blue", "orange"] for m in memories)
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op="!=", value=0.9)])
    assert len(memories) == 2
    assert all(m.value in ["blue", "orange"] for m in memories)
    # bool column
    memories = repository.list(filters=[FilterItem(field=("metrics", "is_duplicate"), op="!=", value=True)])
    assert len(memories) == 1
    assert memories[0].value == "orange"
    # datetime column
    memories = repository.list(
        filters=[FilterItem(field=("created_at",), op="!=", value=mems_to_insert[0].created_at.isoformat())]
    )
    assert len(memories) == 2
    assert all(m.value in ["blue", "orange"] for m in memories)
    # None value
    memories = repository.list(filters=[FilterItem(field=("source_id",), op="!=", value=None)])
    assert len(memories) == 2
    assert all(m.value in ["red", "orange"] for m in memories)
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op="!=", value="value")])
    assert len(memories) == 3

    ##### greater than (>) filter #####
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op=">", value=0)])
    assert len(memories) == 2
    assert all(m.value in ["blue", "orange"] for m in memories)
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op=">", value=0.8)])
    assert len(memories) == 1
    assert memories[0].value == "red"
    # datetime column
    memories = repository.list(
        filters=[FilterItem(field=("created_at",), op=">", value=mems_to_insert[0].created_at - timedelta(days=1))]
    )
    assert len(memories) == 3
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op=">", value=4)])
    assert len(memories) == 0

    ##### greater than or equal to (>=) filter #####
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op=">=", value=0)])
    assert len(memories) == 3
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op=">=", value=0.5)])
    assert len(memories) == 2
    assert all(m.value in ["red", "orange"] for m in memories)
    # datetime column
    memories = repository.list(filters=[FilterItem(field=("created_at",), op=">=", value=mems_to_insert[0].created_at)])
    assert len(memories) == 3
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op=">=", value=4)])
    assert len(memories) == 0

    ##### less than (<) filter #####
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op="<", value=0)])
    assert len(memories) == 0
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op="<", value=0.8)])
    assert len(memories) == 2
    assert all(m.value in ["orange", "blue"] for m in memories)
    # datetime column
    memories = repository.list(filters=[FilterItem(field=("created_at",), op="<", value=mems_to_insert[0].created_at)])
    assert len(memories) == 0
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op="<", value=4)])
    assert len(memories) == 0

    ##### less than or equal to (<=) filter #####
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op="<=", value=0)])
    assert len(memories) == 1
    assert memories[0].value == "red"
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op="<=", value=0.5)])
    assert len(memories) == 2
    assert all(m.value in ["orange", "blue"] for m in memories)
    # datetime column
    memories = repository.list(filters=[FilterItem(field=("created_at",), op="<=", value=mems_to_insert[1].created_at)])
    assert len(memories) == 2
    assert all(m.value in ["red", "orange"] for m in memories)
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op="<=", value=4)])
    assert len(memories) == 0

    ##### in filter #####
    # string column
    memories = repository.list(filters=[FilterItem(field=("value",), op="in", value=["orange", "blue"])])
    assert len(memories) == 2
    assert all(m.value in ["orange", "blue"] for m in memories)
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op="in", value=[0, 1])])
    assert len(memories) == 2
    assert all(m.value in ["red", "orange"] for m in memories)
    # UUID column
    memories = repository.list(
        filters=[
            FilterItem(
                field=("memory_id",),
                op="in",
                value=[str(mems_to_insert[0].memory_id), str(mems_to_insert[1].memory_id)],
            )
        ]
    )
    assert len(memories) == 2
    assert all(m.value in ["red", "orange"] for m in memories)
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op="in", value=[0.2, 0.9])])
    assert len(memories) == 2
    assert all(m.value in ["red", "blue"] for m in memories)
    # bool column
    memories = repository.list(filters=[FilterItem(field=("metrics", "is_duplicate"), op="in", value=[True])])
    assert len(memories) == 2
    assert all(m.value in ["red", "blue"] for m in memories)
    # mismatched field and filter value type
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op="in", value=["orange", "blue"])])
    assert len(memories) == 0
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op="in", value=[1])])
    assert len(memories) == 0

    ##### not in filter #####
    # string column
    memories = repository.list(filters=[FilterItem(field=("value",), op="not in", value=["orange", "blue"])])
    assert len(memories) == 1
    assert memories[0].value == "red"
    # int column
    memories = repository.list(filters=[FilterItem(field=("label",), op="not in", value=[0, 1])])
    assert len(memories) == 1
    assert memories[0].value == "blue"
    # UUID column
    memories = repository.list(
        filters=[FilterItem(field=("memory_id",), op="not in", value=[str(mems_to_insert[0].memory_id)])]
    )
    assert len(memories) == 2
    assert all(m.value in ["blue", "orange"] for m in memories)
    # float column
    memories = repository.list(filters=[FilterItem(field=("metadata", "score"), op="not in", value=[0.2, 0.9])])
    assert len(memories) == 1
    assert memories[0].value == "orange"
    # bool column
    memories = repository.list(filters=[FilterItem(field=("metrics", "is_duplicate"), op="not in", value=[True])])
    assert len(memories) == 1
    assert memories[0].value == "orange"
    # mismatched field and filter value type
    memories = repository.list(
        filters=[FilterItem(field=("metrics", "is_duplicate"), op="not in", value=["orange", "blue"])]
    )
    assert len(memories) == 3
    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op="not in", value=[1])])
    assert len(memories) == 3

    ##### like filter #####
    # substring match
    memories = repository.list(filters=[FilterItem(field=("value",), op="like", value="%e%")])
    assert len(memories) == 3
    # prefix match
    memories = repository.list(filters=[FilterItem(field=("metadata", "id"), op="like", value="ora%")])
    assert len(memories) == 1
    assert memories[0].value == "orange"
    # suffix match
    memories = repository.list(filters=[FilterItem(field=("value",), op="like", value="%ed")])
    assert len(memories) == 1
    assert memories[0].value == "red"

    # Nonexistent key -- this should not raise an error
    memories = repository.list(filters=[FilterItem(field=("metadata", "nonexistent"), op="like", value="red%")])
    assert len(memories) == 0


def test_list_filter_errors(repository):
    # Given a storage backend with some data
    mems_to_insert = [
        _create_labeled_memory(
            value="red",
            label=0,
            metadata=dict(id="red", score=0.9),
            metrics=MemoryMetrics(is_duplicate=True),
            embedding=EmbeddingModel.CLIP_BASE.embed(["red"])[0],
            source_id="source_1",
            memory_id=uuid7(),
        ),
        _create_labeled_memory(
            value="orange",
            label=1,
            metadata=dict(id="orange", score=0.5),
            metrics=MemoryMetrics(),
            embedding=EmbeddingModel.CLIP_BASE.embed(["orange"])[0],
            source_id="source_2",
            memory_id=uuid7(),
        ),
        _create_labeled_memory(
            value="blue",
            label=2,
            metadata=dict(id="blue", score=0.2),
            metrics=MemoryMetrics(is_duplicate=True),
            embedding=EmbeddingModel.CLIP_BASE.embed(["blue"])[0],
            source_id=None,
            memory_id=uuid7(),
        ),
    ]
    repository.insert(mems_to_insert)

    # Not using pytest.mark.parametrize for performance reasons, we want to insert the data once for all test cases

    filters = [
        (FilterItem(field=("metadata",), op="==", value=["ireland"])),
        (FilterItem(field=("metadata",), op="!=", value=["ireland"])),
        (FilterItem(field=("value",), op=">", value="red")),
        (FilterItem(field=("memory_id",), op=">", value=str(mems_to_insert[0].memory_id))),
        (FilterItem(field=("memory_id",), op=">=", value=str(mems_to_insert[0].memory_id))),
        (FilterItem(field=("memory_id",), op="<", value=str(mems_to_insert[0].memory_id))),
        (FilterItem(field=("memory_id",), op="<=", value=str(mems_to_insert[0].memory_id))),
        (FilterItem(field=("value",), op=">=", value="red")),
        (FilterItem(field=("value",), op="<", value="red")),
        (FilterItem(field=("value",), op="<=", value="red")),
        (FilterItem(field=("label",), op=">", value=True)),
        (FilterItem(field=("label",), op=">=", value=True)),
        (FilterItem(field=("label",), op="<", value=True)),
        (FilterItem(field=("label",), op="<=", value=True)),
        (FilterItem(field=("created_at",), op=">", value="not_datetime")),
        (FilterItem(field=("created_at",), op=">=", value="not_datetime")),
        (FilterItem(field=("created_at",), op="<", value="not_datetime")),
        (FilterItem(field=("created_at",), op="<=", value="not_datetime")),
        (FilterItem(field=("label",), op="in", value=1)),
        (FilterItem(field=("label",), op="not in", value=0)),
        (FilterItem(field=("label",), op="like", value=0)),
        (FilterItem(field=("label",), op="like", value=["red"])),
        (FilterItem(field=("memory_id",), op="like", value=str(mems_to_insert[0].memory_id))),
    ]
    for filter_item in filters:
        with pytest.raises(ValueError):
            repository.list(filters=[filter_item])


def test_list_with_filters_memory_metrics(repository):
    # Given a storage backend with some data
    mems_to_insert = [
        _create_labeled_memory(
            value="red",
            label=0,
            metadata=dict(id="red", score=0.9),
            metrics=MemoryMetrics(neighbor_predicted_label=0, neighbor_predicted_label_matches_current_label=True),
            source_id="source_1",
        ),
        _create_labeled_memory(
            value="orange",
            label=1,
            metadata=dict(id="orange", score=0.5),
            source_id="source_2",
        ),
    ]
    repository.insert(mems_to_insert)

    memories = repository.list(
        filters=[FilterItem(field=("metrics", "neighbor_predicted_label_matches_current_label"), op="==", value=True)]
    )
    assert len(memories) == 1
    assert memories[0].value == "red"


@pytest.fixture
def scored_memory_repository(repo_params):
    repo_type, database_uri, collection_name, index_type = repo_params
    match repo_type:
        case "in-memory":
            repository = MemorysetInMemoryRepository(collection_name=collection_name)
        case "milvus-lite":
            repository = MemorysetMilvusRepository(database_uri=database_uri, collection_name=collection_name)
        case "milvus-server":
            repository = MemorysetMilvusRepository(database_uri=database_uri, collection_name=collection_name)
        case _:
            raise ValueError(f"Invalid repository type: {repo_type}")

    config = MemorysetConfig(
        memory_type="scored",
        label_names=[],  # Not used for scored memories
        embedding_dim=EmbeddingModel.DISTILBERT.embedding_dim,
        embedding_model_name=EmbeddingModel.DISTILBERT.path,
        embedding_model_max_seq_length_override=None,
        index_type=index_type,
        index_params={},
    )
    yield repository.connect(config)
    repository.drop()


def test_scored_memory_repository(scored_memory_repository):
    # Given a scored memory repository
    scored_memories = [
        ScoredMemory(
            value=data["value"],
            score=data["score"],
            embedding=EmbeddingModel.CLIP_BASE.embed([data["value"]])[0],
            memory_id=uuid7(),
            memory_version=1,
            source_id=data["source_id"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            edited_at=datetime.now(timezone.utc),
            metadata=data["metadata"],
            metrics={},
        )
        for data in [
            {"value": "high score text", "score": 0.95, "source_id": "source_1", "metadata": {"category": "high"}},
            {"value": "medium score text", "score": 0.65, "source_id": "source_2", "metadata": {"category": "medium"}},
            {"value": "low score text", "score": 0.35, "source_id": "source_3", "metadata": {"category": "low"}},
        ]
    ]
    # Then we can insert and retrieve scored memories
    scored_memory_repository.insert(scored_memories)
    assert scored_memory_repository.count() == 3
    for memory in scored_memory_repository.iterator():
        assert memory.score is not None
        assert memory.source_id is not None
        assert memory.memory_id is not None
        assert memory.memory_version == 1
        assert memory.created_at is not None
        assert memory.updated_at is not None
        assert memory.metadata is not None
        assert memory.metadata["category"] in ["high", "medium", "low"]
        assert memory.value is not None
        assert memory.metrics == {}
    # And filter by score
    memories = scored_memory_repository.list(filters=[FilterItem(field=("score",), op=">", value=0.7)])
    assert len(memories) == 1
    assert memories[0].value == "high score text"
    # And perform lookups
    query = EmbeddingModel.DISTILBERT.embed(["high"])[0]
    lookups = scored_memory_repository.lookup([query], k=2, use_cache=False)
    assert len(lookups) == 1
    assert len(lookups[0]) == 2


def test_milvus_config_collection_migration(temp_folder):
    # Given a milvus db with the old config collection
    database_uri = f"{temp_folder}/milvus_migration_test.db"
    client = MemorysetMilvusRepository._get_client(database_uri, create=True, token="")
    assert client is not None
    schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field("memoryset_collection_name", DataType.VARCHAR, is_primary=True, max_length=256)
    schema.add_field("label_names", DataType.VARCHAR, is_primary=False, max_length=256)
    schema.add_field("embedding_dim", DataType.INT64, is_primary=False)
    schema.add_field("embedding_model_name", DataType.VARCHAR, is_primary=False, max_length=256)
    schema.add_field("embedding_model_max_seq_length_overwrite", DataType.INT64, is_primary=False)
    schema.add_field("embedding_model_query_prompt_override", DataType.VARCHAR, is_primary=False, max_length=1024)
    schema.add_field("embedding_model_document_prompt_override", DataType.VARCHAR, is_primary=False, max_length=1024)
    schema.add_field("updated_at", DataType.VARCHAR, is_primary=False, max_length=48)
    schema.add_field("schema_version", DataType.INT64, is_primary=False)
    schema.add_field("_unused", DataType.FLOAT_VECTOR, is_primary=False, dim=2)
    client.create_collection(collection_name="memoryset_configs", schema=schema, consistency_level="Strong")
    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(field_name="_unused", index_name="_unused", index_type="FLAT", metric_type="L2")
    client.create_index("memoryset_configs", index_params=index_params)
    client.load_collection("memoryset_configs")
    # And a few configs in the old collection
    configs = [
        MemorysetConfig(
            schema_version=6,
            memory_type="labeled",
            label_names=["positive", "negative", "neutral"],
            embedding_dim=768,
            embedding_model_name="OrcaDB/cde-small-v1",
            embedding_model_max_seq_length_override=256,
            embedding_model_query_prompt_override="query: ",
            embedding_model_document_prompt_override="passage: ",
            index_type="IVF_FLAT",
            index_params={"nlist": 128},
        ),
        MemorysetConfig(
            schema_version=2,
            memory_type="scored",
            label_names=[],
            embedding_dim=512,
            embedding_model_name="OrcaDB/gte-base-en-v1.5",
        ),
    ]
    client.insert(
        "memoryset_configs",
        [
            {
                "memoryset_collection_name": f"test_collection_{i}",
                "memory_type": config.memory_type,
                "label_names": json.dumps(config.label_names),
                "embedding_dim": config.embedding_dim,
                "embedding_model_name": config.embedding_model_name,
                "embedding_model_max_seq_length_overwrite": config.embedding_model_max_seq_length_override or -1,
                "embedding_model_document_prompt_override": config.embedding_model_document_prompt_override or "",
                "embedding_model_query_prompt_override": config.embedding_model_query_prompt_override or "",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "index_type": config.index_type,
                "index_params": json.dumps(config.index_params),
                "schema_version": config.schema_version,
                "_unused": [0.0, 0.0],
            }
            for i, config in enumerate(configs)
        ],
    )
    assert client.query(collection_name="memoryset_configs", filter="", output_fields=["count(*)"])[0]["count(*)"] == 2
    # When the config collection is migrated
    repository = MemorysetMilvusRepository(database_uri)
    # Then all configs are migrated to the new collection
    assert repository.get_collection_count() == 2
    assert repository.get_collection_names() == ["test_collection_0", "test_collection_1"]
    # And the configs are the same
    assert MemorysetMilvusRepository(database_uri, "test_collection_0").get_config() == configs[0]
    assert MemorysetMilvusRepository(database_uri, "test_collection_1").get_config() == configs[1]
