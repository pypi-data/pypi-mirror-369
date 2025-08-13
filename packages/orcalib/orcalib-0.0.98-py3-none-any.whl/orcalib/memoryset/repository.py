from __future__ import annotations

import hashlib
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterator, Literal, cast
from uuid import UUID

import numpy as np
from cachetools import TTLCache
from pydantic import BaseModel, Field

from ..utils.pydantic import Vector
from .memory_types import (
    FilterableMemoryField,
    FilterableMemoryMetricFields,
    LabeledMemory,
    LabeledMemoryLookup,
    Memory,
    MemoryLookup,
    ScoredMemory,
    ScoredMemoryLookup,
)

logging.basicConfig(level=logging.INFO)

CACHE_TTL = 2 * 60 * 60  # 2h
CACHE_SIZE = 25000

FilterOperator = Literal["==", "!=", ">", ">=", "<", "<=", "in", "not in", "like"]
FilterValue = str | int | float | bool | None | datetime | list[str] | list[int] | list[float] | list[bool]

FilterItemTuple = tuple[str, FilterOperator, FilterValue]

IndexType = Literal["FLAT", "IVF_FLAT", "IVF_SQ8", "IVF_PQ", "HNSW", "DISKANN"]
MemoryType = Literal["labeled", "scored", "plain"]


class FilterItem(BaseModel):
    field: (
        tuple[FilterableMemoryField]
        | tuple[Literal["metadata"], str]
        | tuple[Literal["metrics"], FilterableMemoryMetricFields]
    )
    op: FilterOperator
    value: FilterValue

    @staticmethod
    def from_tuple(input: FilterItemTuple) -> FilterItem:
        return FilterItem(field=cast(Any, tuple(input[0].split("."))), op=input[1], value=input[2])

    @staticmethod
    def from_tuple_list(
        inputs: list[FilterItem] | list[FilterItemTuple] | list[FilterItemTuple | FilterItem],
    ) -> list[FilterItem]:
        return [item if isinstance(item, FilterItem) else FilterItem.from_tuple(item) for item in inputs]


class MemorysetConfig[T: MemoryType](BaseModel):
    memory_type: T
    label_names: list[str]
    embedding_dim: int
    embedding_model_name: str
    embedding_model_max_seq_length_override: int | None = None
    embedding_model_document_prompt_override: str | None = None
    embedding_model_query_prompt_override: str | None = None
    index_type: IndexType = "FLAT"
    index_params: dict[str, Any] = {}

    schema_version: int = 0  # set by the repository, cannot be overridden from the outside

    class Config:
        frozen = True
        extra = "forbid"


class MemorysetRepository(ABC):
    collection_name: str
    database_uri: str
    is_local_database: bool
    connected: bool = False

    # Important note: We make this a class variable so that all instances of the same class share the same cache.
    # This is important because we want to avoid creating multiple caches for the same collection. The key is the collection name.
    _caches: dict[str, TTLCache[str, list[MemoryLookup] | list[ScoredMemoryLookup] | list[LabeledMemoryLookup]]] = {}

    @classmethod
    def _get_cache_key(cls, query: np.ndarray, k: int, filters: list[FilterItem] | None = None) -> str:
        query_hash = hashlib.md5(query.tobytes(order="C")).hexdigest()
        if filters:
            filters_str = "|".join(f"{f.field}:{f.op}:{f.value}" for f in filters)
            filters_hash = hashlib.md5(filters_str.encode()).hexdigest()
            return f"{query_hash}_{k}_{filters_hash}"
        return f"{query_hash}_{k}"

    def __init__(
        self,
        database_uri: str,
        collection_name: str = "default",
        cache_ttl: int = CACHE_TTL,
        cache_size: int = CACHE_SIZE,
    ) -> None:
        """
        Create a storage backend for the memoryset without connecting to it.

        Warning:
            Before performing any operations on the storage backend other than `drop` and
            `get_config`, you must call `connect` on it.

        Args:
            collection_name: Name of the collection to use for the memoryset
            database_uri: URI of the database to connect to
            cache_ttl: the time to live for the cache
            cache_size: the size of the cache
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", collection_name):
            raise ValueError(f"Collection name {collection_name} must only contain letters, numbers, and underscores")
        self.collection_name = collection_name
        self.database_uri = database_uri

        if self._cache_collection_name() not in self._caches:
            MemorysetRepository._caches[self._cache_collection_name()] = TTLCache(maxsize=cache_size, ttl=cache_ttl)

    def _cache_collection_name(self) -> str:
        return f"{self.database_uri}_{self.collection_name}"

    def _clear_cache(self) -> None:
        MemorysetRepository._caches[self._cache_collection_name()].clear()

    def _get_cache_item(
        self, key: str
    ) -> list[MemoryLookup] | list[ScoredMemoryLookup] | list[LabeledMemoryLookup] | None:
        return MemorysetRepository._caches[self._cache_collection_name()].get(key)

    def _set_cache_item(
        self, key: str, item: list[MemoryLookup] | list[ScoredMemoryLookup] | list[LabeledMemoryLookup]
    ) -> None:
        MemorysetRepository._caches[self._cache_collection_name()][key] = item

    def _cache_size(self) -> int:
        return int(MemorysetRepository._caches[self._cache_collection_name()].currsize)

    def __eq__(self, other: Any) -> bool:
        return (
            self.__class__ == other.__class__
            and self.database_uri == other.database_uri
            and self.collection_name == other.collection_name
        )

    def get_collection_names(self) -> list[str]:
        """
        Get the names of all collections in the database.

        Returns:
            List of collection names.
        """
        raise NotImplementedError

    @abstractmethod
    def drop(self):
        """
        Drop the data collection of the memoryset and delete its config.

        Notes:
            This does not drop the database file itself, only the data collection for the memoryset and
            the row for the memoryset's config. If the memoryset has not been created yet, this
            operation is a no-op.
        """
        pass

    @abstractmethod
    def get_config(self) -> MemorysetConfig | None:
        """
        Get the config for the memoryset if it exists.

        Notes:
            This will not create a local database file if it does not exist.

        Returns:
            Metadata for the memoryset or None if the memoryset has not been created yet.
        """
        pass

    @abstractmethod
    def connect(self, config: MemorysetConfig) -> MemorysetRepository:
        """
        Connect to the database, initialize the database and memories collection if necessary, and
        save the config for the memoryset.
        """
        pass

    @abstractmethod
    def update_config(self, config: MemorysetConfig) -> MemorysetConfig:
        """
        Update the config of the memoryset and save it.
        """
        pass

    def reset(self, config: MemorysetConfig):
        """
        Drop the collection of the memoryset and delete its config, then recreate it.
        """
        self.drop()
        self.connect(config)

    @abstractmethod
    def insert(self, data: list[Memory] | list[ScoredMemory] | list[LabeledMemory]) -> None:
        """Inserts a list of memories into the database"""
        pass

    @abstractmethod
    def lookup(
        self, queries: list[Vector], k: int, *, use_cache: bool, filters: list[FilterItem] = []
    ) -> list[list[MemoryLookup]] | list[list[ScoredMemoryLookup]] | list[list[LabeledMemoryLookup]]:
        """
        Find nearest neighbors for each query and return a list of lookup results for each query
        """
        pass

    @abstractmethod
    def list(
        self, *, limit: int | None = None, offset: int | None = None, filters: list[FilterItem] = []
    ) -> list[Memory] | list[ScoredMemory] | list[LabeledMemory]:
        """
        Get a list of memories from the database that match the filters
        """
        pass

    def iterator(
        self,
        *,
        limit: int | None = None,
        batch_size: int = 100,
        filters: list[FilterItem] = [],
    ) -> Iterator[Memory] | Iterator[ScoredMemory] | Iterator[LabeledMemory]:
        """
        Iterate over the memories in the database that match the filters, this is much more efficient
        than `list` because it does not need to load all memories into memory at once.
        """
        limit = limit or self.count(filters)
        for i in range(0, limit, batch_size):
            yield from self.list(limit=batch_size, offset=i, filters=filters)

    @abstractmethod
    def count(self, filters: list[FilterItem] = []) -> int:
        """
        Count the number of memories in the database that match the filters
        """
        pass

    def get(self, memory_id: UUID) -> Memory | ScoredMemory | LabeledMemory | None:
        """
        Get a single memory from the database by its ID
        """
        return self.get_multi([memory_id]).get(memory_id, None)

    @abstractmethod
    def get_multi(
        self, memory_ids: list[UUID]
    ) -> dict[UUID, Memory] | dict[UUID, ScoredMemory] | dict[UUID, LabeledMemory]:
        pass

    def upsert(self, memory: Memory | ScoredMemory | LabeledMemory) -> Memory | ScoredMemory | LabeledMemory:
        """
        Upsert a single memory into the database
        """
        return self.upsert_multi([memory])[memory.memory_id]

    @abstractmethod
    def upsert_multi(
        self, memories: list[Memory] | list[ScoredMemory] | list[LabeledMemory]
    ) -> dict[UUID, Memory] | dict[UUID, ScoredMemory] | dict[UUID, LabeledMemory]:
        """
        Upsert a list of memories into the database
        """
        pass

    def delete(self, memory_id: UUID) -> bool:
        """
        Delete a single memory from the database by its ID
        """
        return self.delete_multi([memory_id])

    @abstractmethod
    def delete_multi(self, memory_ids: list[UUID]) -> bool:
        """
        Delete a list of memories from the database by their IDs
        """
        pass
