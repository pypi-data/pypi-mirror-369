from __future__ import annotations

from datetime import datetime
from typing import Any, Self, cast
from uuid import UUID

import numpy as np

from ..utils.pydantic import Vector
from .memory_types import (
    LabeledMemory,
    LabeledMemoryLookup,
    Memory,
    MemoryLookup,
    ScoredMemory,
    ScoredMemoryLookup,
)
from .repository import (
    CACHE_SIZE,
    CACHE_TTL,
    FilterItem,
    MemorysetConfig,
    MemorysetRepository,
    MemoryType,
)

# Global in-memory database
_collections: dict[str, tuple[MemorysetConfig, dict[UUID, dict]]] = {}


class MemorysetInMemoryRepository(MemorysetRepository):
    SCHEMA_VERSION = 0  # always keep this as 0 since this is in-memory

    def _serialize(self, memory: Memory | LabeledMemory | ScoredMemory) -> dict:
        m = memory.model_dump()
        # Check that embedding has correct shape
        if len(m["embedding"].shape) != 1 or m["embedding"].shape[0] != self._config.embedding_dim:
            raise ValueError(
                f"Embedding shape {m['embedding'].shape} should be one dimensional with length {self._config.embedding_dim}"
            )
        # Convert timestamps to milliseconds
        m["created_at"] = int(m["created_at"].timestamp() * 1000)
        m["updated_at"] = int(m["updated_at"].timestamp() * 1000)
        # Set metrics to empty dict if it's None
        if m["metrics"] is None:
            m["metrics"] = {}
        # Remove label_name for labeled memories
        if self._config.memory_type == "labeled" and "label_name" in m:
            del m["label_name"]
        return m

    def _to_memory(self, data: dict) -> Memory | LabeledMemory | ScoredMemory:
        match self._config.memory_type:
            case "labeled":
                label_name = (
                    self._config.label_names[data["label"]] if data["label"] < len(self._config.label_names) else None
                )
                return LabeledMemory(**data, label_name=label_name)
            case "scored":
                return ScoredMemory(**data)
            case "plain":
                return Memory(**data)

    def _to_memory_lookup(
        self, lookup_score: float, memory: Memory | LabeledMemory | ScoredMemory
    ) -> MemoryLookup | LabeledMemoryLookup | ScoredMemoryLookup:
        match self._config.memory_type:
            case "labeled":
                return LabeledMemoryLookup(lookup_score=lookup_score, **memory.model_dump())
            case "scored":
                return ScoredMemoryLookup(lookup_score=lookup_score, **memory.model_dump())
            case "plain":
                return MemoryLookup(lookup_score=lookup_score, **memory.model_dump())

    def __init__(
        self,
        database_uri: str = "memory:",
        collection_name: str = "default",
        cache_ttl: int = CACHE_TTL,
        cache_size: int = CACHE_SIZE,
    ) -> None:
        if database_uri != "memory:":
            raise ValueError("MemorysetInMemoryRepository only supports one in-memory database")
        super().__init__(database_uri, collection_name, cache_ttl, cache_size)

    def get_collection_names(self) -> list[str]:
        return list(_collections.keys())

    def get_config(self) -> MemorysetConfig | None:
        if self.collection_name in _collections:
            return _collections[self.collection_name][0]
        return None

    def drop(self):
        if self.collection_name in _collections:
            del _collections[self.collection_name]

    def _upsert_config_and_collection(self, config: MemorysetConfig, data: dict[UUID, dict]) -> None:
        _collections[self.collection_name] = (
            MemorysetConfig(
                **config.model_dump(exclude={"schema_version"}),
                schema_version=self.SCHEMA_VERSION,
            ),
            data,
        )

    @property
    def _config(self) -> MemorysetConfig[MemoryType]:
        if self.collection_name not in _collections:
            raise RuntimeError("You need to connect the storage backend before using it")
        return _collections[self.collection_name][0]

    @property
    def _data(self) -> dict[UUID, dict]:
        if self.collection_name not in _collections:
            raise RuntimeError("You need to connect the storage backend before using it")
        return _collections[self.collection_name][1]

    def update_config(self, config: MemorysetConfig) -> MemorysetConfig:
        self._upsert_config_and_collection(config, self._data)
        return config

    def connect(self, config: MemorysetConfig) -> Self:
        if self.collection_name not in _collections:
            self._upsert_config_and_collection(config, {})
        return self

    def insert(self, data: list[Memory] | list[ScoredMemory] | list[LabeledMemory]) -> None:
        # Serialize all memories first to check that they are valid.
        # This way we will raise an error if any of the memories are invalid so we don't end up with a partial update
        serialized_memories = [self._serialize(memory) for memory in data]
        for memory in serialized_memories:
            self._data[memory["memory_id"]] = memory

    def _single_lookup(
        self, query: Vector, k: int, filters: list[FilterItem]
    ) -> list[MemoryLookup] | list[ScoredMemoryLookup] | list[LabeledMemoryLookup]:
        if not self._data:
            return []

        memories = [self._to_memory(m) for m in self._data.values()]
        if filters:
            memories = [m for m in memories if self._match_filters(filters, m)]

        if len(memories) < k:
            k = len(memories)

        results = sorted(
            [
                self._to_memory_lookup(
                    lookup_score=np.dot(m.embedding, query),
                    memory=m,
                )
                for m in memories
            ],
            key=lambda x: x.lookup_score,
            reverse=True,
        )[:k]

        return results

    def lookup(
        self, queries: list[Vector], k: int, *, use_cache: bool, filters: list[FilterItem] = []
    ) -> list[list[MemoryLookup]] | list[list[ScoredMemoryLookup]] | list[list[LabeledMemoryLookup]]:
        return cast(
            list[list[MemoryLookup]] | list[list[ScoredMemoryLookup]] | list[list[LabeledMemoryLookup]],
            [self._single_lookup(q, k, filters) for q in queries],
        )

    def _match_filters(self, filters: list[FilterItem], memory: Memory | ScoredMemory | LabeledMemory) -> bool:
        for filter in filters:
            field_value: Any = memory.model_dump()
            for f in filter.field:
                try:
                    field_value = field_value[f]
                except (KeyError, IndexError):
                    field_value = None

            if filter.value is None and len(filter.field) > 1:
                raise ValueError("Filtering for null values is not supported for JSON fields")

            # Try to convert string filter value to datetime and then to timestamp in milliseconds for comparison
            # if the field is a datetime
            if isinstance(field_value, datetime) and isinstance(filter.value, str):
                try:
                    filter.value = int(datetime.fromisoformat(filter.value).timestamp() * 1000)
                except ValueError:
                    match = False
            # Convert datetime field and filter values to timestamp in milliseconds for comparison
            # This is make sure they are in the same format and precision
            if isinstance(field_value, datetime):
                field_value = int(field_value.timestamp() * 1000)
            if isinstance(filter.value, datetime):
                filter.value = int(filter.value.timestamp() * 1000)

            # Convert UUID field and filter values to string for comparison
            # This would technically be supported but the Milvus backend doesn't support it and we want feature parity
            if isinstance(field_value, UUID):
                field_value = str(field_value)
            if isinstance(filter.value, UUID):
                filter.value = str(filter.value)

            match filter.op:
                case "==":
                    # Note: We technically could support list equality but it's not supported by the Milvus backend
                    # and we want feature parity
                    # If Milvus ever adds support for list equality or we want to support it for im-memory, just remove this ef clause
                    if isinstance(filter.value, list):
                        raise ValueError(
                            "Equality operation on a list is not supported. Please use the 'in' or 'not in' operators instead."
                        )
                    match = field_value == filter.value
                case "!=":
                    # Note: We technically could support list equality but it's not supported by the Milvus backend
                    # and we want feature parity
                    # If Milvus ever adds support for list equality or we want to support it for im-memory, just remove this if clause
                    if isinstance(filter.value, list):
                        raise ValueError(
                            "Equality operation on a list is not supported. Please use the 'in' or 'not in' operators instead."
                        )
                    match = field_value != filter.value
                case ">":
                    if field_value is None:
                        match = False
                    elif (
                        isinstance(field_value, (int, float))
                        and isinstance(filter.value, (int, float))
                        and not isinstance(field_value, bool)
                        and not isinstance(filter.value, bool)
                    ):
                        match = field_value > filter.value
                    else:
                        raise ValueError("'>' operation is only supported on numeric columns")
                case "<":
                    if field_value is None:
                        match = False
                    elif (
                        isinstance(field_value, (int, float))
                        and isinstance(filter.value, (int, float))
                        and not isinstance(field_value, bool)
                        and not isinstance(filter.value, bool)
                    ):
                        match = field_value < filter.value
                    else:
                        raise ValueError("'<' operation is only supported on numeric columns")
                case ">=":
                    if field_value is None:
                        match = False
                    elif (
                        isinstance(field_value, (int, float))
                        and isinstance(filter.value, (int, float))
                        and not isinstance(field_value, bool)
                        and not isinstance(filter.value, bool)
                    ):
                        match = field_value >= filter.value
                    else:
                        raise ValueError("'>=' operation is only supported on numeric columns")
                case "<=":
                    if field_value is None:
                        match = False
                    elif (
                        isinstance(field_value, (int, float))
                        and isinstance(filter.value, (int, float))
                        and not isinstance(field_value, bool)
                        and not isinstance(filter.value, bool)
                    ):
                        match = field_value <= filter.value
                    else:
                        raise ValueError("'<=' operation is only supported on numeric columns")
                case "in":
                    if not isinstance(filter.value, list) or isinstance(field_value, list):
                        raise ValueError("'in' operation only supported on scalar columns")
                    match = field_value in filter.value
                case "not in":
                    if not isinstance(filter.value, list) or isinstance(field_value, list):
                        raise ValueError("'not in' operation only supported on scalar columns")
                    match = field_value not in filter.value
                case "like":
                    if field_value is None:
                        match = False
                    elif not isinstance(field_value, str) or not isinstance(filter.value, str):
                        raise ValueError("'like' operation only supported on string columns")
                    elif filter.value.startswith("%") and filter.value.endswith("%"):
                        match = filter.value[1:-1] in field_value
                    elif filter.value.startswith("%"):
                        match = field_value.endswith(filter.value[1:])
                    elif filter.value.endswith("%"):
                        match = field_value.startswith(filter.value[:-1])
                    else:
                        # Note: We technically could support like without wildcards but it's not supported by the Milvus backend
                        # and we want feature parity
                        # If Milvus ever adds support for like without wildcards or we want to support it for im-memory, just make this a simple equality check
                        raise ValueError(
                            f"{filter.op} operator requires the use of a wildcard ('%') character in the value, got {filter.value}. "
                            "If you would like to filter on string equality please use the '==' operator."
                        )
                case _:
                    raise ValueError(f"Invalid filter operation: {filter.op}")

            if not match:
                return False

        return True

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[FilterItem] = [],
    ) -> list[Memory] | list[ScoredMemory] | list[LabeledMemory]:
        memories = [self._to_memory(m) for m in self._data.values()]
        if filters != []:
            memories = [m for m in memories if self._match_filters(filters, m)]
        # filter by primary key to match Milvus behavior
        memories = sorted(memories, key=lambda x: x.memory_id)
        if limit is not None:
            offset = offset or 0
            memories = memories[offset : offset + limit]
        elif offset is not None:
            memories = memories[offset:]
        return memories

    def count(self, filters: list[FilterItem] = []) -> int:
        if filters == []:
            return len(self._data)
        memories = [self._to_memory(m) for m in self._data.values()]
        memories = [m for m in memories if self._match_filters(filters, m)]
        return len(memories)

    def get_multi(
        self, memory_ids: list[UUID]
    ) -> dict[UUID, Memory] | dict[UUID, ScoredMemory] | dict[UUID, LabeledMemory]:
        return {
            memory_id: self._to_memory(self._data[memory_id]) for memory_id in memory_ids if memory_id in self._data
        }

    def upsert_multi(
        self, memories: list[Memory] | list[ScoredMemory] | list[LabeledMemory]
    ) -> dict[UUID, Memory] | dict[UUID, ScoredMemory] | dict[UUID, LabeledMemory]:
        # Serialize all memories first to check that they are valid.
        # This way we will raise an error if any of the memories are invalid so we don't end up with a partial update
        serialized_memories = [self._serialize(memory) for memory in memories]
        for memory in serialized_memories:
            self._data[memory["memory_id"]] = memory
        return self.get_multi([memory.memory_id for memory in memories])

    def delete_multi(self, memory_ids: list[UUID]) -> bool:
        deleted_ids = [memory_id for memory_id in memory_ids if memory_id in self._data]
        for memory_id in deleted_ids:
            del self._data[memory_id]

        return all((id in deleted_ids) for id in memory_ids)
