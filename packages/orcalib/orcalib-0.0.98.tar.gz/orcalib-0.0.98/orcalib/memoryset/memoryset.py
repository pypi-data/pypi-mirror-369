from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from itertools import batched, islice
from typing import Any, Callable, Iterable, Iterator, Literal, Self, cast, overload
from uuid import UUID

import numpy as np
import PIL.Image as pil
from datasets import ClassLabel, Dataset, Features, Image, Sequence, Value
from pandas import DataFrame
from tqdm.auto import tqdm
from uuid_utils.compat import uuid7

from ..embedding import EmbeddingModel, EmbeddingModelContext
from ..utils.dataset import parse_dataset, parse_label_names
from ..utils.progress import OnProgressCallback, safely_call_on_progress
from ..utils.pydantic import UNSET, UUID7, Metadata, Vector, input_type_eq
from .memory_types import (
    InputType,
    InputTypeList,
    LabeledMemory,
    LabeledMemoryInsert,
    LabeledMemoryLookup,
    LabeledMemoryLookupColumnResult,
    LabeledMemoryUpdate,
    LookupReturnType,
    Memory,
    MemoryInsert,
    MemoryLookup,
    MemoryLookupColumnResult,
    MemoryMetrics,
    MemoryUpdate,
    ScoredMemory,
    ScoredMemoryInsert,
    ScoredMemoryLookup,
    ScoredMemoryLookupColumnResult,
    ScoredMemoryUpdate,
)
from .repository import (
    FilterItem,
    FilterItemTuple,
    IndexType,
    MemorysetConfig,
    MemorysetRepository,
    MemoryType,
)
from .repository_memory import MemorysetInMemoryRepository
from .repository_milvus import MemorysetMilvusRepository

logging.basicConfig(level=logging.INFO)


class Memoryset[T: MemoryType]:
    """Unified memoryset that handles both labeled and scored memories."""

    repository: MemorysetRepository
    """Storage backend used to persist the memoryset"""

    embedding_model: EmbeddingModel
    """Embedding model used to generate embeddings for semantic similarity search"""

    config: MemorysetConfig[T]
    """Configuration for the memoryset"""

    DEFAULT_TABLE_NAME = "memories"

    def __init__(
        self,
        location: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        memory_type: T | None = None,
        label_names: list[str] | None = None,
        document_prompt: str | None = None,
        query_prompt: str | None = None,
        config: MemorysetConfig | None = None,
        index_type: IndexType = "FLAT",
        index_params: dict[str, Any] = {},
    ):
        """
        Initialize a memoryset.

        Args:
            location: location where the memoryset is stored. Can either be directly a storage
                backend instance, or a URI like `"file:~/.orca/milvus.db#my_memoryset"`, or just a
                collection name like `"my_memoryset"` if a `MILVUS_URL` environment
                variable is set.
            embedding_model: Embedding model to use for semantic similarity search. When reconnecting
                to an existing memoryset the correct embedding model will automatically be loaded,
                otherwise an embedding model must be specified.
            memory_type: Type of memories to store ("labeled", "scored", or "plain"). Required when creating
                a new memoryset, automatically detected when connecting to existing memoryset.
            label_names: List with label names for labeled memorysets, where each index maps the
                integer value of the label to the name of the label. When reconnecting to an existing
                memoryset, the label names will be loaded, otherwise should be specified for labeled memorysets.
            document_prompt: Optional prompt prefix to use for document embeddings when creating a new memoryset.
            query_prompt: Optional prompt prefix to use for query embeddings when creating a new memoryset.
            config: Optional config to use instead of auto-detecting or creating one.
            index_type: Type of vector index to use.
            index_params: Parameters for the vector index.
        """
        disconnected_repository = self.repository_from_uri(location) if isinstance(location, str) else location
        config = config if config is not None else disconnected_repository.get_config()

        if config is None:
            if embedding_model is None:
                raise ValueError("Embedding model must be specified when creating a new memoryset.")
            if memory_type is None:
                raise ValueError("Memory type must be specified when creating a new memoryset.")
            self.embedding_model = embedding_model
            if memory_type == "labeled" and label_names is None:
                logging.warning("No label names specified, memoryset will not be able to resolve label names.")

            self.config = MemorysetConfig(
                memory_type=memory_type,
                label_names=label_names or [],
                embedding_dim=embedding_model.embedding_dim,
                embedding_model_name=embedding_model.path,
                embedding_model_max_seq_length_override=embedding_model.max_seq_length_override,
                embedding_model_query_prompt_override=query_prompt,
                embedding_model_document_prompt_override=document_prompt,
                index_type=index_type,
                index_params=index_params,
            )
        else:
            if embedding_model and embedding_model.path != config.embedding_model_name:
                raise ValueError(
                    f"Given embedding model ({embedding_model.path}) does not match previously used embedding model ({config.embedding_model_name})."
                )
            self.embedding_model = embedding_model or EmbeddingModel(
                config.embedding_model_name, max_seq_length_override=config.embedding_model_max_seq_length_override
            )
            self.config = config

        if isinstance(location, str):
            disconnected_repository = self.repository_from_uri(location)

        self.repository = disconnected_repository.connect(self.config)

    @property
    def _embedding_context(self) -> EmbeddingModelContext | None:
        # initializing this lazily to avoid slowing down the constructor
        if not self.embedding_model.uses_context:
            return None
        if not hasattr(self, "__embedding_context"):
            # NOTE: To avoid loading all memories into memory, we only load a sample of 10000 memories
            context = list(islice(self, 10000))
            self.__embedding_context = (
                self.embedding_model.compute_context([m.value for m in context if isinstance(m.value, str)])
                if len(self) > 10
                else None
            )
        return self.__embedding_context

    @_embedding_context.setter
    def _embedding_context(self, context: EmbeddingModelContext | None):
        self.__embedding_context = context

    @classmethod
    def repository_from_uri(cls, uri: str) -> MemorysetRepository:
        """Create a repository instance from URI."""
        if uri.startswith("memory:"):
            # Parse memory: URIs - they can be "memory:#collection_name" or just "memory:"
            if "#" in uri:
                collection_name = uri.split("#", 1)[1]
            else:
                collection_name = cls.DEFAULT_TABLE_NAME
            return MemorysetInMemoryRepository(collection_name=collection_name)
        else:
            # Parse the URI for Milvus repositories
            if "#" in uri:
                database_uri, collection_name = uri.split("#", 1)
            elif "MILVUS_URL" in os.environ and os.environ["MILVUS_URL"]:
                database_uri = os.environ["MILVUS_URL"]
                collection_name = uri
            else:
                database_uri = uri
                collection_name = cls.DEFAULT_TABLE_NAME

            # Clean up the database URI
            database_uri = database_uri.replace("file://", "").replace("file:", "")
            return MemorysetMilvusRepository(database_uri=database_uri, collection_name=collection_name)

    @staticmethod
    def _is_database_uri(uri: str) -> bool:
        """Check if a given URI is a database URI."""
        return ".db" in uri or uri.startswith("http") or uri.startswith("memory:")

    @property
    def memory_type(self) -> T:
        """Type of memories stored in this memoryset."""
        return self.config.memory_type

    @property
    def uri(self) -> str:
        """URI where the memoryset is stored."""
        return self.repository.database_uri + "#" + self.repository.collection_name

    @property
    def label_names(self) -> list[str]:
        """List of label names for labeled memorysets."""
        if self.memory_type != "labeled":
            raise NotImplementedError("label_names is only available for labeled memorysets")
        return self.config.label_names

    @label_names.setter
    def label_names(self, label_names: list[str]):
        if self.memory_type != "labeled":
            raise NotImplementedError("label_names can only be set for labeled memorysets")
        self.config = self.repository.update_config(
            MemorysetConfig(**(self.config.model_dump() | {"label_names": label_names}))
        )

    @property
    def document_prompt(self) -> str | None:
        """Prompt to use for memory embeddings."""
        return self.config.embedding_model_document_prompt_override

    @document_prompt.setter
    def document_prompt(self, prompt: str | None):
        self.config = self.repository.update_config(
            MemorysetConfig(
                **(
                    self.config.model_dump()
                    | {
                        "embedding_model_document_prompt_override": prompt,
                        "embedding_model_query_prompt_override": prompt,  # Keep both prompts equal
                    }
                )
            )
        )

    @property
    def query_prompt(self) -> str | None:
        """Prompt to use for query embeddings."""
        return self.config.embedding_model_query_prompt_override

    @query_prompt.setter
    def query_prompt(self, prompt: str | None):
        self.config = self.repository.update_config(
            MemorysetConfig(
                **(
                    self.config.model_dump()
                    | {
                        "embedding_model_document_prompt_override": prompt,  # Keep both prompts equal
                        "embedding_model_query_prompt_override": prompt,
                    }
                )
            )
        )

    def get_label_name(self, label: int) -> str | None:
        """Get the name for a label value based on the set label names."""
        if self.memory_type != "labeled":
            raise NotImplementedError("get_label_name is only available for labeled memorysets")
        return self.label_names[label] if label < len(self.label_names) else None

    @property
    def num_classes(self) -> int:
        """Number of unique labels in labeled memorysets."""
        if self.memory_type != "labeled":
            raise NotImplementedError("num_classes is only available for labeled memorysets")
        if self.label_names:
            return len(self.label_names)
        logging.warning(
            f"Could not find label names in memoryset config, counting unique labels instead for {self.uri}. This may be slow."
        )
        return len(set(mem.label for mem in self if isinstance(mem, LabeledMemory)))

    def reset(self) -> None:
        """Remove all memories and reinitialize."""
        self.repository.reset(self.config)

    @overload
    def to_list(self: Memoryset[Literal["plain"]], limit: int | None = None) -> list[Memory]:
        pass

    @overload
    def to_list(self: Memoryset[Literal["scored"]], limit: int | None = None) -> list[ScoredMemory]:
        pass

    @overload
    def to_list(self: Memoryset[Literal["labeled"]], limit: int | None = None) -> list[LabeledMemory]:
        pass

    def to_list(self, limit: int | None = None) -> list[Memory] | list[ScoredMemory] | list[LabeledMemory]:
        """Get a list of all memories."""
        return self.repository.list(limit=limit)

    def to_pandas(self, limit: int | None = None) -> DataFrame:
        """Get a pandas DataFrame representation."""
        return DataFrame([m.model_dump() for m in self.repository.list(limit=limit)])

    def count(self, filters: list[FilterItem] | list[FilterItemTuple] = []) -> int:
        """Count memories matching filters."""
        return self.repository.count(filters=FilterItem.from_tuple_list(filters))

    @classmethod
    @lru_cache(maxsize=100)
    def connect(cls, uri: str) -> Self:
        """
        Connect to an existing memoryset.

        Args:
            uri: The URI of the memoryset to connect to.

        Returns:
            A Memoryset instance connected to the existing memoryset.
        """
        repository = cls.repository_from_uri(uri)
        config = repository.get_config()
        if not config:
            raise ValueError(f"No memoryset found at {uri}")

        return cls(
            location=uri,
            memory_type=config.memory_type,
            label_names=config.label_names,
            embedding_model=None,  # Will be loaded from config
            config=config,
        )

    @classmethod
    def drop(cls, uri: str) -> None:
        """Drop (delete) a memoryset at the given URI."""
        repository = cls.repository_from_uri(uri)
        repository.drop()

    @classmethod
    def exists(cls, uri: str) -> bool:
        """Check if a memoryset exists at the given URI."""
        try:
            repository = cls.repository_from_uri(uri)
            config = repository.get_config()
            return config is not None
        except Exception:
            return False

    def __repr__(self) -> str:
        if self.memory_type == "labeled":
            return (
                "Memoryset({\n"
                f"    uri: {self.uri},\n"
                f"    memory_type: {self.memory_type},\n"
                f"    embedding_model: {self.embedding_model},\n"
                f"    num_rows: {len(self)},\n"
                f"    label_names: {self.label_names},\n"
                "})"
            )
        else:
            return (
                "Memoryset({\n"
                f"    uri: {self.uri},\n"
                f"    memory_type: {self.memory_type},\n"
                f"    embedding_model: {self.embedding_model},\n"
                f"    num_rows: {len(self)},\n"
                "})"
            )

    def to_dataset(
        self, *, value_column: str = "value", label_column: str = "label", score_column: str = "score"
    ) -> Dataset:
        """
        Get a [Dataset][datasets.Dataset] representation of the memoryset.

        Args:
            value_column: name of the column containing the values
            label_column: name of the column containing the labels (for labeled memorysets)
            score_column: name of the column containing the scores (for scored memorysets)

        Returns:
            Dataset of the memories with appropriate features based on memory type
        """
        value_type = self.value_type

        if value_type == "string":
            value_feature = Value(dtype="string")
        elif value_type == "image":
            value_feature = Image()
        else:  # time series
            value_feature = Sequence(feature=Value(dtype="float32"))

        def to_dict(memory: Memory | ScoredMemory | LabeledMemory) -> dict:
            m = {
                value_column: memory.value,
                "embedding": memory.embedding.tolist(),
                "memory_id": str(memory.memory_id),
                "memory_version": memory.memory_version,
                "source_id": memory.source_id,
                "metadata": memory.metadata,
                "metrics": memory.metrics,
            }
            if isinstance(memory, ScoredMemory):
                m[score_column] = memory.score
            elif isinstance(memory, LabeledMemory):
                m[label_column] = memory.label
            return m

        features = Features(
            {
                value_column: value_feature,
                "embedding": Sequence(feature=Value(dtype="float32")),
                "memory_id": Value(dtype="string"),
                "memory_version": Value(dtype="int64"),
                "source_id": Value(dtype="string"),
                "metadata": dict(),
                "metrics": dict(),
            }
        )
        if self.memory_type == "labeled":
            features[label_column] = ClassLabel(names=self.label_names) if self.label_names else Value(dtype="int64")
        elif self.memory_type == "scored":
            features[score_column] = Value(dtype="float32")

        return Dataset.from_list(
            [to_dict(memory) for memory in self],
            features=features,
        )

    @overload
    def query(
        self: Memoryset[Literal["plain"]],
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[Memory]:
        pass

    @overload
    def query(
        self: Memoryset[Literal["labeled"]],
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[LabeledMemory]:
        pass

    @overload
    def query(
        self: Memoryset[Literal["scored"]],
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[ScoredMemory]:
        pass

    def query(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[Memory] | list[ScoredMemory] | list[LabeledMemory]:
        """
        Query the memoryset for memories that match the query.

        Args:
            limit: Maximum number of memories to return.
            offset: Number of memories to skip.
            filters: Filters to apply to the query.

        Returns:
            List of memories that match the query.
        """
        return self.repository.list(limit=limit, offset=offset, filters=FilterItem.from_tuple_list(filters))

    def _embed(
        self,
        values: InputTypeList,
        value_kind: Literal["document", "query"],
        prompt_override: str | None = None,
        use_cache: bool = True,
        batch_size: int = 32,
    ) -> list[Vector]:
        return self.embedding_model.embed(
            values,
            context=self._embedding_context,
            use_cache=use_cache,
            value_kind=value_kind,
            prompt=prompt_override
            or (
                self.config.embedding_model_document_prompt_override
                if value_kind == "document"
                else self.config.embedding_model_query_prompt_override
            ),
            batch_size=batch_size,
        )

    def insert(
        self,
        dataset: (
            Dataset
            | list[dict]
            | list[MemoryInsert]
            | list[ScoredMemoryInsert]
            | list[LabeledMemoryInsert]
            | list[Memory]
            | list[ScoredMemory]
            | list[LabeledMemory]
        ),
        *,
        value_column: str = "value",
        label_column: str = "label",
        score_column: str = "score",
        source_id_column: str | None = None,
        other_columns_as_metadata: bool = True,
        show_progress_bar: bool = True,
        compute_embeddings: bool = True,
        batch_size: int = 32,
        prompt_override: str | None = None,
        only_if_empty: bool = False,
        on_progress: OnProgressCallback | None = None,
    ) -> list[UUID]:
        """
        Inserts a dataset into the memoryset database.

        For dict-like or list of dict-like datasets, there must be a `label`/`score` key and one of the following keys: `text`, `image`, or `value`.
        If there are only two keys and one is `label`/`score`, the other will be inferred to be `value`.

        For list-like datasets, the first element of each tuple must be the value and the second must be the label/score.

        Args:
            dataset: data to insert into the memoryset
            value_column: name of the dataset column containing the values
            label_column: name of the dataset column containing the labels (for labeled memorysets)
            score_column: name of the dataset column containing the scores (for scored memorysets)
            source_id_column: name of a dataset column containing ids used for the memories in an external system
            other_columns_as_metadata: collect all other column values in the metadata dictionary
            show_progress_bar: whether to show a progress bar
            compute_embeddings: optionally disable embedding computation when copying memories
            batch_size: the batch size when creating embeddings from memories
            prompt_override: override for the document prompt to use for the inserted memories
            only_if_empty: whether to skip the insert if the memoryset is not empty
            on_progress: callback function to call with the already inserted and total number of rows

        Examples:
            >>> dataset = Dataset.from_list([
            ...    {"text": "text 1", "label": 0},
            ...    {"text": "text 2", "label": 1},
            ... ])
            >>> memoryset = Memoryset("file:///path/to/memoryset", memory_type="labeled")
            >>> memoryset.insert(dataset)
        """
        if only_if_empty and len(self):
            logging.warning("Skipping insert: `only_if_empty` is True and memoryset is not empty.")
            return []

        insert_num_rows = len(dataset)
        if insert_num_rows == 0:
            logging.warning("Nothing to insert")
            return []

        if not compute_embeddings and not isinstance(dataset, list) and not hasattr(dataset[0], "embedding"):
            raise ValueError("compute_embeddings can only be disabled when inserting Memory objects with embeddings")

        @dataclass
        class InsertItem:
            value: InputType
            label: int | None = None
            score: float | None = None
            metadata: Metadata = field(default_factory=dict)
            source_id: str | None = None
            embedding: Vector | None = None
            memory_id: UUID7 = field(default_factory=uuid7)
            memory_version: int = 1
            created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
            updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
            edited_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
            metrics: MemoryMetrics = field(default_factory=lambda: MemoryMetrics())

        # if a list of dicts is passed, convert it to a Dataset
        if isinstance(dataset, list) and isinstance(dataset[0], dict):
            dataset = Dataset.from_list(cast(list[dict], dataset))
        else:
            # tell the type checker that list[dict] is not an option anymore
            dataset = cast(
                Dataset
                | list[Memory]
                | list[ScoredMemory]
                | list[LabeledMemory]
                | list[LabeledMemoryInsert]
                | list[ScoredMemoryInsert]
                | list[MemoryInsert],
                dataset,
            )

        if isinstance(dataset, Dataset):
            # For labeled memorysets, handle label names
            if self.memory_type == "labeled":
                label_names = parse_label_names(dataset, label_column=label_column)
                if self.label_names == [] and label_names is not None:
                    logging.warning(f"Setting label names to {label_names}")
                    self.label_names = label_names

            parsed_dataset = parse_dataset(
                dataset,
                value_column=value_column,
                label_column=label_column if self.memory_type == "labeled" else None,
                score_column=score_column if self.memory_type == "scored" else None,
                source_id_column=source_id_column,
                other_columns_as_metadata=other_columns_as_metadata,
                label_names=self.label_names if self.memory_type == "labeled" else None,
            )
            insert_items = [
                InsertItem(
                    value=item["value"],
                    label=item["label"] if self.memory_type == "labeled" else None,
                    score=item["score"] if self.memory_type == "scored" else None,
                    metadata=item["metadata"] if "metadata" in item else {},
                    source_id=item["source_id"] if "source_id" in item else None,
                )
                for item in cast(list[dict], parsed_dataset)
            ]
        else:
            insert_items = [InsertItem(**m.model_dump(exclude_none=True, exclude={"label_name"})) for m in dataset]

        # Some embedding models use a context to customize the embeddings for a specific task
        # if the model uses it and there are enough memories then update the context
        if self.embedding_model.uses_context:
            # update the context if the dataset changed by more than 20% and at least 10 items
            if insert_num_rows > 10 and insert_num_rows > len(self) / 5:
                self._embedding_context = self.embedding_model.compute_context(
                    [m.value for m in insert_items] + [m.value for m in self]
                )

        if compute_embeddings:
            # Use smart batching to optimize memory usage when calculating embeddings
            batches = self.embedding_model.smart_batch(
                insert_items, batch_size=batch_size, prompt=prompt_override, value_kind="document"
            )
        else:
            batches = [insert_items[i : i + batch_size] for i in range(0, len(insert_items), batch_size)]

        # Process each smart batch
        processed_items = 0
        for batch in tqdm(batches, disable=not show_progress_bar):
            safely_call_on_progress(on_progress, processed_items, insert_num_rows)

            # compute embeddings if not already provided.
            if compute_embeddings:
                embeddings = self._embed(
                    [m.value for m in batch],
                    value_kind="document",
                    prompt_override=prompt_override,
                    batch_size=len(batch),
                )
            else:
                embeddings: list[Vector] = []
                for item in batch:
                    embedding = item.embedding
                    assert embedding is not None
                    embeddings.append(embedding)

            # insert fully populated memory objects
            match self.memory_type:
                case "labeled":
                    memories = [
                        LabeledMemory(
                            value=item.value,
                            label=item.label if item.label is not None else 0,  # Default to 0 if None
                            label_name=self.get_label_name(item.label) if item.label is not None else None,
                            embedding=embedding,
                            memory_id=item.memory_id,
                            memory_version=item.memory_version,
                            source_id=item.source_id,
                            metadata=item.metadata,
                            metrics=MemoryMetrics(),
                            created_at=item.created_at,
                            updated_at=item.updated_at,
                            edited_at=item.edited_at,
                        )
                        for item, embedding in zip(batch, embeddings)
                    ]
                case "scored":
                    memories = [
                        ScoredMemory(
                            value=item.value,
                            score=item.score if item.score is not None else 0.0,  # Default to 0.0 if None
                            embedding=embedding,
                            memory_id=item.memory_id,
                            memory_version=item.memory_version,
                            source_id=item.source_id,
                            metadata=item.metadata,
                            metrics=MemoryMetrics(),
                            created_at=item.created_at,
                            updated_at=item.updated_at,
                            edited_at=item.edited_at,
                        )
                        for item, embedding in zip(batch, embeddings)
                    ]
                case "plain":
                    memories = [
                        Memory(
                            value=item.value,
                            embedding=embedding,
                            memory_id=item.memory_id,
                            memory_version=item.memory_version,
                            source_id=item.source_id,
                            metadata=item.metadata,
                            metrics=MemoryMetrics(),
                            created_at=item.created_at,
                            updated_at=item.updated_at,
                            edited_at=item.edited_at,
                        )
                        for item, embedding in zip(batch, embeddings)
                    ]

            self.repository.insert(memories)
            processed_items += len(memories)

        safely_call_on_progress(on_progress, insert_num_rows, insert_num_rows)
        return [m.memory_id for m in insert_items]

    def delete(self, memory_ids: UUID | Iterable[UUID]) -> bool:
        """
        Delete a memory from the memoryset.

        Args:
            memory_ids: The UUID of the memory to delete, or a list of such UUIDs.
        Returns:
            True if a memory was deleted, False otherwise.
        """
        if isinstance(memory_ids, UUID):
            return self.repository.delete(memory_ids)
        return self.repository.delete_multi(list(memory_ids))

    @overload
    def __iter__(self: Memoryset[Literal["plain"]]) -> Iterator[Memory]:
        pass

    @overload
    def __iter__(self: Memoryset[Literal["scored"]]) -> Iterator[ScoredMemory]:
        pass

    @overload
    def __iter__(self: Memoryset[Literal["labeled"]]) -> Iterator[LabeledMemory]:
        pass

    @overload
    def __iter__(self: Memoryset[MemoryType]) -> Iterator[Memory] | Iterator[ScoredMemory] | Iterator[LabeledMemory]:
        pass

    def __iter__(self) -> Iterator[Memory] | Iterator[ScoredMemory] | Iterator[LabeledMemory]:
        """
        Allow iterating over the memories.
        """
        return self.repository.iterator()

    def __len__(self) -> int:
        return self.repository.count()

    @property
    def num_rows(self) -> int:
        """Number of memories in the memoryset."""
        return len(self)

    @overload
    def __getitem__(self: Memoryset[Literal["plain"]], index: slice) -> list[Memory]:
        pass

    @overload
    def __getitem__(self: Memoryset[Literal["plain"]], index: int | str | UUID) -> Memory:
        pass

    @overload
    def __getitem__(self: Memoryset[Literal["scored"]], index: slice) -> list[ScoredMemory]:
        pass

    @overload
    def __getitem__(self: Memoryset[Literal["scored"]], index: int | str | UUID) -> ScoredMemory:
        pass

    @overload
    def __getitem__(self: Memoryset[Literal["labeled"]], index: slice) -> list[LabeledMemory]:
        pass

    @overload
    def __getitem__(self: Memoryset[Literal["labeled"]], index: int | str | UUID) -> LabeledMemory:
        pass

    @overload
    def __getitem__(self, index: slice) -> list[Memory] | list[ScoredMemory] | list[LabeledMemory]:
        pass

    @overload
    def __getitem__(self, index: int | UUID | str) -> Memory | ScoredMemory | LabeledMemory:
        pass

    def __getitem__(
        self, index: slice | int | UUID | str
    ) -> list[Memory] | list[ScoredMemory] | list[LabeledMemory] | Memory | ScoredMemory | LabeledMemory:
        if isinstance(index, int):
            if index >= len(self):
                raise IndexError(f"Index {index} out of bounds for memoryset with length {len(self)}")
            return self.repository.list(offset=index, limit=1)[0]
        if isinstance(index, UUID) or isinstance(index, str):
            memory = self.repository.get(index if isinstance(index, UUID) else UUID(index))
            if memory is None:
                raise IndexError(f"Memory with id {index} not found")
            return memory
        if isinstance(index, slice):
            if index.step is not None:
                raise NotImplementedError("Stepping through a memoryset is not supported")

            start = index.start or 0
            stop = index.stop or len(self)
            slice_length = stop - start

            return self.repository.list(offset=start, limit=slice_length)
        raise ValueError(f"Invalid index type: {type(index)}")

    @property
    def value_type(self) -> Literal["string", "image", "timeseries"]:
        match self[0].value:
            case str():
                return "string"
            case pil.Image():
                return "image"
            case np.ndarray():
                return "timeseries"
            case _:
                raise ValueError(f"Unknown value type: {type(self[0].value)}")

    @overload
    def lookup(
        self: Memoryset[Literal["labeled"]],
        query: InputType,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS] | Literal["rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[LabeledMemoryLookup]:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["labeled"]],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS] | Literal["rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[list[LabeledMemoryLookup]]:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["labeled"]],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.COLUMNS] | Literal["columns"],
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> LabeledMemoryLookupColumnResult:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["scored"]],
        query: InputType,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS] | Literal["rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[ScoredMemoryLookup]:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["scored"]],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS] | Literal["rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[list[ScoredMemoryLookup]]:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["scored"]],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.COLUMNS] | Literal["columns"],
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> ScoredMemoryLookupColumnResult:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["plain"]],
        query: InputType,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS] | Literal["rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[MemoryLookup]:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["plain"]],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS] | Literal["rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[list[MemoryLookup]]:
        pass

    @overload
    def lookup(
        self: Memoryset[Literal["plain"]],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.COLUMNS] | Literal["columns"],
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> MemoryLookupColumnResult:
        pass

    @overload
    def lookup(
        self: Memoryset[MemoryType],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS] | Literal["rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[list[MemoryLookup]] | list[list[LabeledMemoryLookup]] | list[list[ScoredMemoryLookup]]:
        pass

    @overload
    def lookup(
        self: Memoryset[MemoryType],
        query: InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.COLUMNS] | Literal["columns"],
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> MemoryLookupColumnResult | LabeledMemoryLookupColumnResult | ScoredMemoryLookupColumnResult:
        pass

    def lookup(
        self,
        query: InputType | InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: LookupReturnType | Literal["rows", "columns"] = LookupReturnType.ROWS,
        use_cache: bool = True,
        prompt: str | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> (
        list[MemoryLookup]
        | list[LabeledMemoryLookup]
        | list[ScoredMemoryLookup]
        | list[list[MemoryLookup]]
        | list[list[LabeledMemoryLookup]]
        | list[list[ScoredMemoryLookup]]
        | MemoryLookupColumnResult
        | LabeledMemoryLookupColumnResult
        | ScoredMemoryLookupColumnResult
    ):
        """
        Retrieves the most similar memories to the query from the memoryset.

        Note:
            This method does not support performing lookups with precomputed embeddings, because
            instruction tuned embedding models use different prompts for queries and documents which
            means the embeddings stored in the memoryset are different from the ones that are
            computed in this method for identical values. Embeddings are already automatically
            cached, so for smallish memorysets they will not be recomputed during e.g. finetuning.
            If you know what you are doing, you can directly call `_perform_lookup` with precomputed
            embeddings, but this does not support excluding exact matches.

        Args:
            query: The query to retrieve memories for. Can be a single value or a list of values.
            count: The number of memories to retrieve.
            exclude_exact_match: Whether to exclude a maximum of one exact match from the results.
            return_type: Whether to return a list of memory lookups or a dictionary of columns.
            use_cache: Whether to use the cache to speed up lookups.
            prompt_override: Override for the default query prompt.
            filters: Filters to apply to the query.

        Returns:
            The memory lookup results for the query.
        """
        embedded_queries = self._embed(
            query if isinstance(query, list) else [query],
            value_kind="query",
            prompt_override=prompt or self.config.embedding_model_query_prompt_override,
            use_cache=use_cache,
        )
        memory_lookups_batch = self._perform_lookup(
            embedded_queries,
            # to exclude the exact match, we fetch one extra memory and then remove the top hit
            count=count + 1 if exclude_exact_match else count,
            use_cache=use_cache,
            filters=FilterItem.from_tuple_list(filters),
        )
        if exclude_exact_match:
            self._exclude_exact_lookup_matches(memory_lookups_batch, query)

        # return correctly formatted results
        if return_type == "columns":
            return self._format_lookup_column_result(memory_lookups_batch, embedded_queries)

        if not isinstance(query, list):
            assert len(memory_lookups_batch) == 1
            return memory_lookups_batch[0]

        return memory_lookups_batch

    @overload
    def _perform_lookup(
        self: Memoryset[Literal["plain"]],
        embedded_queries: list[Vector],
        count: int,
        use_cache: bool = True,
        filters: list[FilterItem] = [],
    ) -> list[list[MemoryLookup]]:
        pass

    @overload
    def _perform_lookup(
        self: Memoryset[Literal["scored"]],
        embedded_queries: list[Vector],
        count: int,
        use_cache: bool = True,
        filters: list[FilterItem] = [],
    ) -> list[list[ScoredMemoryLookup]]:
        pass

    @overload
    def _perform_lookup(
        self: Memoryset[Literal["labeled"]],
        embedded_queries: list[Vector],
        count: int,
        use_cache: bool = True,
        filters: list[FilterItem] = [],
    ) -> list[list[LabeledMemoryLookup]]:
        pass

    @overload
    def _perform_lookup(
        self: Memoryset[MemoryType],
        embedded_queries: list[Vector],
        count: int,
        use_cache: bool = True,
        filters: list[FilterItem] = [],
    ) -> list[list[MemoryLookup]] | list[list[ScoredMemoryLookup]] | list[list[LabeledMemoryLookup]]:
        pass

    def _perform_lookup(
        self,
        embedded_queries: list[Vector],  # calling
        count: int,
        use_cache: bool = True,
        filters: list[FilterItem] = [],
    ) -> list[list[MemoryLookup]] | list[list[ScoredMemoryLookup]] | list[list[LabeledMemoryLookup]]:
        if count == 0:
            return [[] for _ in range(len(embedded_queries))]
        if len(self) < count:
            raise ValueError(f"Requested {count} memories but memoryset only contains {len(self)} memories")

        memory_lookups_batch = self.repository.lookup(embedded_queries, k=count, use_cache=use_cache, filters=filters)

        if not all(len(memories) == count for memories in memory_lookups_batch):
            raise Exception("lookup failed to return the correct number of memories")

        return memory_lookups_batch

    def _exclude_exact_lookup_matches(
        self,
        memory_lookups_batch: (
            list[list[MemoryLookup]] | list[list[ScoredMemoryLookup]] | list[list[LabeledMemoryLookup]]
        ),
        query: InputType | InputTypeList,
    ):
        for i, memory_lookups in enumerate(memory_lookups_batch):
            query_item = query[i] if isinstance(query, list) else query
            exact_match_count = 0
            for j, memory_lookup in enumerate(memory_lookups):
                if input_type_eq(memory_lookup.value, query_item):
                    if exact_match_count == 0:
                        # remove the first exact match
                        memory_lookups_batch[i] = memory_lookups[:j] + memory_lookups[j + 1 :]  # type: ignore
                    exact_match_count += 1
            if exact_match_count == 0:
                # remove the last match if no exact match was found
                memory_lookups_batch[i] = memory_lookups[:-1]  # type: ignore
            if exact_match_count > 1:
                logging.warning(
                    f"Found {exact_match_count} exact matches for '{query_item}' in the memoryset, run find duplicate analysis to remove duplicates"
                )

    def _format_lookup_column_result(
        self,
        memory_lookups_batch: (
            list[list[MemoryLookup]] | list[list[ScoredMemoryLookup]] | list[list[LabeledMemoryLookup]]
        ),
        embedded_queries: list[Vector],
    ) -> LabeledMemoryLookupColumnResult | ScoredMemoryLookupColumnResult | MemoryLookupColumnResult:
        match self.memory_type:
            case "labeled":
                return LabeledMemoryLookupColumnResult(
                    input_embeddings=np.vstack(embedded_queries),
                    memories_embeddings=np.array(
                        [[m.embedding for m in memories] for memories in memory_lookups_batch], dtype=np.float32
                    ),
                    memories_labels=np.array(
                        [[getattr(m, "label", 0) for m in memories] for memories in memory_lookups_batch],
                        dtype=np.int64,
                    ),
                    memories_lookup_scores=np.array(
                        [[m.lookup_score for m in memories] for memories in memory_lookups_batch], dtype=np.float32
                    ),
                    memories_values=[[m.value for m in memories] for memories in memory_lookups_batch],
                    memories_label_names=[
                        [getattr(m, "label_name", None) for m in memories] for memories in memory_lookups_batch
                    ],
                    memories_ids=[[m.memory_id for m in memories] for memories in memory_lookups_batch],
                    memories_versions=[[m.memory_version for m in memories] for memories in memory_lookups_batch],
                    memories_metadata=[[m.metadata for m in memories] for memories in memory_lookups_batch],
                    memories_metrics=[
                        [m.metrics if m.metrics else MemoryMetrics() for m in memories]
                        for memories in memory_lookups_batch
                    ],
                    memories_source_ids=[[m.source_id for m in memories] for memories in memory_lookups_batch],
                    memories_created_ats=[[m.created_at for m in memories] for memories in memory_lookups_batch],
                    memories_updated_ats=[[m.updated_at for m in memories] for memories in memory_lookups_batch],
                    memories_edited_ats=[[m.edited_at for m in memories] for memories in memory_lookups_batch],
                )
            case "scored":
                return ScoredMemoryLookupColumnResult(
                    input_embeddings=np.vstack(embedded_queries),
                    memories_embeddings=np.array(
                        [[m.embedding for m in memories] for memories in memory_lookups_batch], dtype=np.float32
                    ),
                    memories_scores=np.array(
                        [[getattr(m, "score", 0.0) for m in memories] for memories in memory_lookups_batch],
                        dtype=np.float32,
                    ),
                    memories_lookup_scores=np.array(
                        [[m.lookup_score for m in memories] for memories in memory_lookups_batch], dtype=np.float32
                    ),
                    memories_values=[[m.value for m in memories] for memories in memory_lookups_batch],
                    memories_ids=[[m.memory_id for m in memories] for memories in memory_lookups_batch],
                    memories_versions=[[m.memory_version for m in memories] for memories in memory_lookups_batch],
                    memories_metadata=[[m.metadata for m in memories] for memories in memory_lookups_batch],
                    memories_metrics=[
                        [cast(MemoryMetrics, m.metrics) if m.metrics else MemoryMetrics() for m in memories]
                        for memories in memory_lookups_batch
                    ],
                    memories_source_ids=[[m.source_id for m in memories] for memories in memory_lookups_batch],
                    memories_created_ats=[[m.created_at for m in memories] for memories in memory_lookups_batch],
                    memories_updated_ats=[[m.updated_at for m in memories] for memories in memory_lookups_batch],
                    memories_edited_ats=[[m.edited_at for m in memories] for memories in memory_lookups_batch],
                )
            case "plain":
                return MemoryLookupColumnResult(
                    input_embeddings=np.vstack(embedded_queries),
                    memories_embeddings=np.array(
                        [[m.embedding for m in memories] for memories in memory_lookups_batch], dtype=np.float32
                    ),
                    memories_lookup_scores=np.array(
                        [[m.lookup_score for m in memories] for memories in memory_lookups_batch], dtype=np.float32
                    ),
                    memories_values=[[m.value for m in memories] for memories in memory_lookups_batch],
                    memories_ids=[[m.memory_id for m in memories] for memories in memory_lookups_batch],
                    memories_versions=[[m.memory_version for m in memories] for memories in memory_lookups_batch],
                    memories_metadata=[[m.metadata for m in memories] for memories in memory_lookups_batch],
                    memories_metrics=[
                        [cast(MemoryMetrics, m.metrics) if m.metrics else MemoryMetrics() for m in memories]
                        for memories in memory_lookups_batch
                    ],
                    memories_source_ids=[[m.source_id for m in memories] for memories in memory_lookups_batch],
                    memories_created_ats=[[m.created_at for m in memories] for memories in memory_lookups_batch],
                    memories_updated_ats=[[m.updated_at for m in memories] for memories in memory_lookups_batch],
                    memories_edited_ats=[[m.edited_at for m in memories] for memories in memory_lookups_batch],
                )

    @overload
    def get(
        self: Memoryset[Literal["plain"]],
        memory_ids: UUID,
    ) -> Memory | None:
        pass

    @overload
    def get(
        self: Memoryset[Literal["plain"]],
        memory_ids: list[UUID],
    ) -> list[Memory | None]:
        pass

    @overload
    def get(
        self: Memoryset[Literal["scored"]],
        memory_ids: UUID,
    ) -> ScoredMemory | None:
        pass

    @overload
    def get(
        self: Memoryset[Literal["scored"]],
        memory_ids: list[UUID],
    ) -> list[ScoredMemory | None]:
        pass

    @overload
    def get(
        self: Memoryset[Literal["labeled"]],
        memory_ids: UUID,
    ) -> LabeledMemory | None:
        pass

    @overload
    def get(
        self: Memoryset[Literal["labeled"]],
        memory_ids: list[UUID],
    ) -> list[LabeledMemory | None]:
        pass

    def get(
        self,
        memory_ids: UUID | list[UUID],
    ) -> (
        Memory
        | ScoredMemory
        | LabeledMemory
        | None
        | list[Memory | None]
        | list[ScoredMemory | None]
        | list[LabeledMemory | None]
    ):
        """
        Get a memory from the memoryset by its UUID or list of UUIDs.

        Args:
            memory_ids: The UUID of the memory to get, or a list of such UUIDs.

        Returns:
            The memory if it exists, otherwise None. If a list of memory ids is provided, it returns a list of memories.
        """
        if isinstance(memory_ids, list):
            memories_dict = self.repository.get_multi(memory_ids)
            return [memories_dict.get(m_id, None) for m_id in memory_ids]
        else:
            memories_dict = self.repository.get_multi([memory_ids])
            return memories_dict.get(memory_ids, None)

    @overload
    def update(
        self: Memoryset[Literal["plain"]],
        updates: MemoryUpdate,
    ) -> Memory | None:
        pass

    @overload
    def update(
        self: Memoryset[Literal["plain"]],
        updates: list[MemoryUpdate],
    ) -> list[Memory | None]:
        pass

    @overload
    def update(
        self: Memoryset[Literal["scored"]],
        updates: ScoredMemoryUpdate,
    ) -> ScoredMemory | None:
        pass

    @overload
    def update(
        self: Memoryset[Literal["scored"]],
        updates: list[ScoredMemoryUpdate],
    ) -> list[ScoredMemory | None]:
        pass

    @overload
    def update(
        self: Memoryset[Literal["labeled"]],
        updates: LabeledMemoryUpdate,
    ) -> LabeledMemory | None:
        pass

    @overload
    def update(
        self: Memoryset[Literal["labeled"]],
        updates: list[LabeledMemoryUpdate],
    ) -> list[LabeledMemory | None]:
        pass

    def update(
        self,
        updates: (
            MemoryUpdate
            | ScoredMemoryUpdate
            | LabeledMemoryUpdate
            | list[MemoryUpdate]
            | list[ScoredMemoryUpdate]
            | list[LabeledMemoryUpdate]
        ),
    ) -> (
        Memory
        | ScoredMemory
        | LabeledMemory
        | None
        | list[Memory | None]
        | list[ScoredMemory | None]
        | list[LabeledMemory | None]
    ):
        """
        Update a memory in the memoryset.

        Args:
            updates: Update object or list of update objects containing the values to update.

        Returns:
            The updated memory if a memory was found and updated, otherwise None.
        """
        if isinstance(updates, list):
            updates_dict = self._update_multi(updates)
            memory_ids = [update.memory_id for update in updates]
            return [updates_dict.get(m_id, None) for m_id in memory_ids]
        else:
            updates_dict = self._update_multi([updates])
            return updates_dict.get(updates.memory_id, None)

    def _update_multi(
        self,
        updates: list[MemoryUpdate] | list[ScoredMemoryUpdate] | list[LabeledMemoryUpdate],
    ) -> dict[UUID, Memory] | dict[UUID, ScoredMemory] | dict[UUID, LabeledMemory]:
        memory_ids = [update.memory_id for update in updates]
        if len(memory_ids) != len(set(memory_ids)):
            raise ValueError("Duplicate memory ids in updates.")

        updates_dict = dict(zip(memory_ids, updates))
        existing_dict = self.repository.get_multi(memory_ids)

        updated_memories = {}
        embeddings_to_compute = {}

        for memory_id, existing_memory in existing_dict.items():
            update = updates_dict[memory_id]

            # Handle metadata reset
            update_dict = update.model_dump(exclude_unset=True, exclude={"memory_id"})
            if "metadata" in update_dict and update_dict["metadata"] is None:
                update_dict["metadata"] = {}

            # Handle metrics reset
            if "metrics" in update_dict and update_dict["metrics"] is None:
                update_dict["metrics"] = MemoryMetrics()

            # Create updated memory based on memory type
            if self.memory_type == "labeled":
                updated_memory = LabeledMemory(
                    **(existing_memory.model_dump() | update_dict | dict(updated_at=datetime.now(timezone.utc))),
                )
            else:  # scored
                updated_memory = ScoredMemory(
                    **(existing_memory.model_dump() | update_dict | dict(updated_at=datetime.now(timezone.utc))),
                )

            # Handle metadata merging
            if hasattr(update, "metadata") and update.metadata and update.metadata is not UNSET:
                updated_memory.metadata = existing_memory.metadata | update.metadata

            # Handle metrics merging
            if hasattr(update, "metrics") and update.metrics and update.metrics is not UNSET:
                # Merge metrics dict
                updated_memory.metrics = existing_memory.metrics | update.metrics  # type: ignore

            if existing_memory.value != updated_memory.value:
                embeddings_to_compute[memory_id] = updated_memory.value

            # Check if key fields changed based on memory type
            value_changed = existing_memory.value != updated_memory.value
            type_field_changed = False
            if self.memory_type == "labeled":
                type_field_changed = getattr(existing_memory, "label", None) != getattr(updated_memory, "label", None)
            else:  # scored
                type_field_changed = getattr(existing_memory, "score", None) != getattr(updated_memory, "score", None)

            if value_changed or type_field_changed:
                updated_memory.memory_version = existing_memory.memory_version + 1
                updated_memory.updated_at = datetime.now(timezone.utc)
                updated_memory.edited_at = datetime.now(timezone.utc)
                # if metrics were not updated but the values changed, we need to reset the metrics
                if hasattr(update, "metrics") and update.metrics is UNSET:
                    updated_memory.metrics = MemoryMetrics()

            updated_memories[memory_id] = updated_memory

        if embeddings_to_compute:
            embeddings_ids = list(embeddings_to_compute.keys())
            embeddings = self._embed(
                [embeddings_to_compute[memory_id] for memory_id in embeddings_ids],
                value_kind="document",
            )
            for memory_id, embedding in zip(embeddings_ids, embeddings):
                updated_memories[memory_id].embedding = embedding

        return self.repository.upsert_multi(list(updated_memories.values()))

    def _prepare_destination(self, destination: str | MemorysetRepository, config: MemorysetConfig) -> Self:
        if isinstance(destination, str) and not self._is_database_uri(destination):
            destination = f"{self.repository.database_uri}#{destination}"
        destination_memoryset = type(self)(destination, config=config)
        if destination_memoryset.repository == self.repository:
            raise ValueError("Destination memoryset cannot be the same as the source memoryset.")
        if len(destination_memoryset) > 0:
            raise ValueError("Destination memoryset must be empty.")
        return destination_memoryset

    def filter(
        self,
        fn: Callable[[Memory | ScoredMemory | LabeledMemory], bool],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> Self:
        """
        Filter memories out from the current memoryset and store result in a new destination.

        Args:
            fn: Function that takes in the memory and returns a boolean indicating whether the
                memory should be included or not.
            destination: location where the filtered memoryset will be stored.
            show_progress_bar: whether to show a progress bar

        Returns:
            The memoryset with the filtered memories at the given destination.
        """
        destination_memoryset = self._prepare_destination(destination, self.config)
        values_to_insert = [m for m in self if fn(m)]
        destination_memoryset.insert(values_to_insert, compute_embeddings=False, show_progress_bar=show_progress_bar)
        return destination_memoryset

    def map(
        self,
        fn: Callable[[Memory | ScoredMemory | LabeledMemory], dict[str, Any]],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> Self:
        """
        Apply updates to all the memories in the memoryset and store result in a new destination.

        Args:
            fn: Function that takes in the memory and returns a dictionary containing the values to
                update in the memory.
            destination: location where the updated memoryset will be stored.
            show_progress_bar: whether to show a progress bar

        Returns:
            The memoryset with the changed memories at the given destination.
        """

        def replace_fn(memory: Memory | ScoredMemory | LabeledMemory) -> Memory | ScoredMemory | LabeledMemory:
            fn_result = fn(memory)
            if not isinstance(fn_result, dict):
                raise ValueError("Map function must return a dictionary with updates.")
            if "embedding" in fn_result:
                raise ValueError(
                    "Embedding cannot be updated. Memoryset automatically calculates embeddings as needed."
                )
            value_changed = "value" in fn_result and memory.value != fn_result["value"]

            # Check type-specific field changes
            type_field_changed = False
            if self.memory_type == "labeled":
                type_field_changed = "label" in fn_result and getattr(memory, "label", None) != fn_result["label"]
            else:  # scored
                type_field_changed = "score" in fn_result and getattr(memory, "score", None) != fn_result["score"]

            if value_changed:
                fn_result["embedding"] = destination_memoryset._embed(
                    [fn_result["value"]],
                    value_kind="document",
                )[0]

            if value_changed or type_field_changed:
                fn_result["memory_version"] = memory.memory_version + 1
                fn_result["updated_at"] = datetime.now(timezone.utc)
                fn_result["edited_at"] = datetime.now(timezone.utc)

            # Create the appropriate memory type
            if self.memory_type == "labeled":
                return LabeledMemory(**(memory.model_dump() | fn_result))
            else:
                return ScoredMemory(**(memory.model_dump() | fn_result))

        destination_memoryset = self._prepare_destination(destination, self.config)
        mapped_memories = [replace_fn(memory) for memory in self]
        destination_memoryset.insert(
            mapped_memories,
            compute_embeddings=False,
            show_progress_bar=show_progress_bar,
        )
        return destination_memoryset

    def clone(
        self,
        destination: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        limit: int | None = None,
        batch_size: int = 32,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
    ) -> Self:
        """
        Clone the current memoryset into a new memoryset.

        Args:
            destination: location where the copied memoryset will be stored.
            embedding_model: optional different embedding model to use for the cloned memoryset.
            limit: optional maximum number of memories to clone.
            batch_size: size of the batches to use for re-embedding the memories
            show_progress_bar: whether to show a progress bar
            on_progress: callback function to update the progress of the cloning process

        Returns:
            The memoryset that the memories were cloned into at the given destination.
        """
        destination_memoryset = self._prepare_destination(
            destination,
            (
                self.config
                if embedding_model is None
                else MemorysetConfig(
                    memory_type=self.memory_type,
                    label_names=self.config.label_names,
                    embedding_dim=embedding_model.embedding_dim,
                    embedding_model_name=embedding_model.path,
                    embedding_model_max_seq_length_override=embedding_model.max_seq_length_override,
                    embedding_model_query_prompt_override=self.config.embedding_model_query_prompt_override,
                    embedding_model_document_prompt_override=self.config.embedding_model_document_prompt_override,
                    index_type=self.config.index_type,
                    index_params=self.config.index_params.copy(),
                )
            ),
        )

        if limit is None:
            limit = self.count()

        memories_iterator = batched(self.repository.iterator(limit=limit, batch_size=batch_size), batch_size)

        num_batches = limit // batch_size

        num_processed = 0
        if on_progress:
            safely_call_on_progress(on_progress, num_processed, limit)

        for memories in tqdm(memories_iterator, disable=not show_progress_bar, total=num_batches):
            destination_memoryset.insert(
                list(memories),
                compute_embeddings=embedding_model is not None and embedding_model != self.embedding_model,
                show_progress_bar=False,
                on_progress=None,
                batch_size=batch_size,
            )

            num_processed += len(memories)

            if on_progress:
                safely_call_on_progress(on_progress, num_processed, limit)

        return destination_memoryset


# Legacy compatibility aliases
class LabeledMemoryset(Memoryset[Literal["labeled"]]):
    def __init__(self, *args, **kwargs):
        # Always set memory_type to "labeled" for LabeledMemoryset
        kwargs["memory_type"] = "labeled"
        super().__init__(*args, **kwargs)


class ScoredMemoryset(Memoryset[Literal["scored"]]):
    def __init__(self, *args, **kwargs):
        # Always set memory_type to "scored" for ScoredMemoryset
        kwargs["memory_type"] = "scored"
        super().__init__(*args, **kwargs)


class PlainMemoryset(Memoryset[Literal["plain"]]):
    def __init__(self, *args, **kwargs):
        # Always set memory_type to "plain" for PlainMemoryset
        kwargs["memory_type"] = "plain"
        super().__init__(*args, **kwargs)
