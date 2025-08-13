from pydantic import BaseModel

from ..memoryset import LabeledMemory, LabeledMemoryLookup
from ..utils.pydantic import UUID7, input_type_eq
from .analysis import MemorysetAnalysis


class MemoryDuplicateMetrics(BaseModel):
    is_duplicate: bool
    duplicate_memory_ids: list[UUID7]
    has_potential_duplicates: bool
    potential_duplicate_memory_ids: list[UUID7]


class MemorysetDuplicateMetrics(BaseModel):
    num_duplicates: int
    """The number of duplicate memories in the memoryset"""


class MemorysetDuplicateAnalysisConfig(BaseModel):
    potential_duplicate_threshold: float = 0.97
    """Lookup score threshold for a memory to be considered a potential duplicate"""


class MemorysetDuplicateAnalysis(
    MemorysetAnalysis[MemorysetDuplicateAnalysisConfig, MemoryDuplicateMetrics, MemorysetDuplicateMetrics]
):
    """
    Find exact and potential duplicates in a memoryset

    Note:
        This does not remove duplicates since that would not be compatible with running this
        alongside other analysis that depend on memoryset consistency while the analysis runs.
        To delete duplicates after the analysis has finished, you can, for example, run:

        ```py
        memoryset.delete(
            m.memory_id
            for m in memoryset.query(
                filters=[("metrics.is_duplicate", "==", True)]
            )
        )
        ```
    """

    name = "duplicate"

    def __init__(self, config: MemorysetDuplicateAnalysisConfig | None = None, **kwargs):
        self.config = config or MemorysetDuplicateAnalysisConfig(**kwargs)

        self._duplicate_memory_ids: set[UUID7] = set()

    def on_batch(
        self, memories_batch: list[LabeledMemory], neighbors_batch: list[list[LabeledMemoryLookup]]
    ) -> list[tuple[UUID7, MemoryDuplicateMetrics]]:
        metrics: list[tuple[UUID7, MemoryDuplicateMetrics]] = []
        for i, memory in enumerate(memories_batch):
            duplicate_memory_ids: list[UUID7] = []
            potential_duplicate_memory_ids: list[UUID7] = []
            for neighbor in neighbors_batch[i]:
                if neighbor.memory_id in self._duplicate_memory_ids:
                    continue
                is_duplicate = input_type_eq(memory.value, neighbor.value)
                if is_duplicate:
                    duplicate_memory_ids.append(neighbor.memory_id)
                    self._duplicate_memory_ids.add(memory.memory_id)
                elif neighbor.lookup_score > self.config.potential_duplicate_threshold:
                    potential_duplicate_memory_ids.append(neighbor.memory_id)

            metrics.append(
                (
                    memory.memory_id,
                    MemoryDuplicateMetrics(
                        is_duplicate=len(duplicate_memory_ids) > 0,
                        duplicate_memory_ids=duplicate_memory_ids,
                        has_potential_duplicates=len(potential_duplicate_memory_ids) > 0,
                        potential_duplicate_memory_ids=potential_duplicate_memory_ids,
                    ),
                )
            )

        return metrics

    def after_all(self) -> MemorysetDuplicateMetrics:
        return MemorysetDuplicateMetrics(
            num_duplicates=len(self._duplicate_memory_ids),
        )
