import hashlib
from typing import cast

import numpy as np
from numpy._typing._array_like import NDArray
from PIL import Image as pil
from pydantic import BaseModel
from umap import UMAP

from ..memoryset import LabeledMemory, LabeledMemoryLookup
from ..utils.pydantic import UUID7, Vector
from .analysis import MemorysetAnalysis


class MemoryProjectionMetrics(BaseModel):
    embedding_2d: tuple[float, float]


class MemorysetProjectionMetrics(BaseModel):
    # nothing to return here yet, but analysis base class requires a return value for now
    pass


class MemorysetProjectionAnalysisConfig(BaseModel):
    min_dist: float = 0.1
    """The minimum distance between points in the UMAP projection"""

    spread: float = 1.0
    """The spread to use for the UMAP projection"""


class MemorysetProjectionAnalysis(
    MemorysetAnalysis[MemorysetProjectionAnalysisConfig, MemoryProjectionMetrics, MemorysetProjectionMetrics]
):
    """Generate 2D embedding projections for all memory embeddings"""

    name = "projection"

    def __init__(self, config: MemorysetProjectionAnalysisConfig | None = None, **kwargs):
        self.config = config or MemorysetProjectionAnalysisConfig(**kwargs)

        self._memory_ids: dict[UUID7, int] = {}
        self._embeddings: list[Vector] = []
        self._neighbors: list[tuple[UUID7, list[tuple[UUID7, np.float32]]]] = []  # memory_id, [neighbor_id, distance]

    @staticmethod
    def hash_image(image: pil.Image) -> str:
        return hashlib.md5(image.convert("RGB").tobytes()).hexdigest()

    def on_batch(self, memories_batch: list[LabeledMemory], neighbors_batch: list[list[LabeledMemoryLookup]]) -> None:
        for i, memory in enumerate(memories_batch):
            self._embeddings.append(memory.embedding)
            self._memory_ids[memory.memory_id] = len(self._memory_ids)
            self._neighbors.append(
                (
                    memory.memory_id,
                    [(lookup.memory_id, np.float32(1 - lookup.lookup_score)) for lookup in neighbors_batch[i]],
                )
            )

    def after_all(self) -> tuple[MemorysetProjectionMetrics, list[tuple[UUID7, MemoryProjectionMetrics]]]:
        memory_embeddings = np.stack(self._embeddings, axis=0)
        neighbor_indices = np.full((self.memoryset_num_rows, self.lookup_count + 1), -1, dtype=np.int32)
        neighbor_distances = np.full((self.memoryset_num_rows, self.lookup_count + 1), np.inf, dtype=np.float32)
        for memory_id, neighbors in self._neighbors:
            memory_idx = self._memory_ids[memory_id]
            neighbor_indices[memory_idx, 0] = memory_idx
            neighbor_distances[memory_idx, 0] = np.float32(0.0)
            for j, (neighbor_id, distance) in enumerate(neighbors):
                neighbor_indices[memory_idx, j + 1] = self._memory_ids[neighbor_id]
                neighbor_distances[memory_idx, j + 1] = distance

        vectors = cast(
            NDArray[np.float32],
            UMAP(
                n_components=2,
                random_state=42,
                metric="cosine",
                n_neighbors=self.lookup_count + 1,
                precomputed_knn=(neighbor_indices, neighbor_distances),
                min_dist=self.config.min_dist,
                spread=self.config.spread,
                disconnection_distance=1.0,
            ).fit_transform(memory_embeddings),
        )
        assert vectors.shape == (len(self._memory_ids), 2)
        return (
            MemorysetProjectionMetrics(),
            [
                (memory_id, MemoryProjectionMetrics(embedding_2d=embedding_2d))
                for memory_id, embedding_2d in zip(self._memory_ids, vectors)
            ],
        )
