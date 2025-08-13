import logging
from abc import ABC, abstractmethod
from itertools import batched
from typing import Any, Iterable, Sequence

from pydantic import BaseModel
from tqdm.auto import tqdm

from ..memoryset import (
    LabeledMemory,
    LabeledMemoryLookup,
    LabeledMemoryset,
    LabeledMemoryUpdate,
    MemoryMetrics,
)
from ..utils.progress import OnProgressCallback, safely_call_on_progress
from ..utils.pydantic import UUID7


class MemorysetAnalysis[TConfig: BaseModel, TMemoryMetrics: BaseModel, TMemorysetMetrics: BaseModel](ABC):
    """
    Base class for analyses that can be run with [`run_analyses`][orcalib.run_analyses].

    Analysis classes run computations on batches of memories and their neighbors supplied by the
    analyzer. This allows running multiple analyses efficiently in a single iteration over the memoryset.

    As the analyzer iterates over the memoryset, it yields to the `on_batch` method of each analysis
    class. The `on_batch` method receives a batch of memories and their neighbors and can return
    metrics for each memory which the analyzer will save.

    After all batches have been processed, the `after_all` method is called to compute any final
    metrics. It returns aggregate metrics for the whole memoryset. For some analyses metrics for
    individual memories can only be computed after all batches have been processed. Thus the
    `after_all` method can also return a tuple with the aggregate metrics and a list of memory
    metric updates to be added to the memoryset.

    Examples:
    >>> class DensityAnalysis(MemorysetAnalysis[DensityAnalysisConfig]):
    ...     name = "density"
    ...
    ...     def __init__(self, config: DensityAnalysisConfig | None = None, **kwargs):
    ...         self.config = config or DensityAnalysisConfig(**kwargs)
    ...         self.sum_avg_lookup_scores = 0
    ...
    ...     def on_batch(
    ...         self,
    ...             memories_batch: list[LabeledMemory],
    ...             neighbors_batch: list[list[LabeledMemoryLookup]],
    ...         ) -> list[tuple[UUID7, MemorysetDensityMetrics]]:
    ...         metrics = []
    ...         for memory, neighbors in zip(memories_batch, neighbors_batch):
    ...             avg_lookup_score = sum(lookup.lookup_score for lookup in neighbors) / self.lookup_count
    ...             self.sum_avg_lookup_scores += avg_lookup_score
    ...             metrics.append((memory.memory_id, MemorysetDensityMetrics(
    ...                 avg_lookup_score=avg_lookup_score
    ...             )))
    ...         return metrics
    ...
    ...     def after_all(self) -> MemorysetDensityMetrics:
    ...         return MemorysetDensityMetrics(
    ...             avg_lookup_score=self.sum_avg_lookup_scores / self.memoryset_num_rows,
    ...         )

    >>> run_analyses(memoryset, DensityAnalysis(), lookup_count=10, batch_size=8)
        {"density": MemorysetDensityMetrics(avg_lookup_score=0.56281324)}
    """

    name: str
    """The name of the analysis"""

    config: TConfig
    """The configuration for the analysis"""

    requires_lookups: bool = True
    """Whether the analysis requires lookups to be performed on the memories.
    If set to False, the analysis will not perform lookups and will only use the embeddings
    provided by the memoryset."""

    @abstractmethod
    def __init__(self, config: TConfig | None = None, **kwargs):
        """
        Initialize the analysis

        Params:
            config: Configuration object for the analysis
            **kwargs: Alternative way to specify configuration parameters directly

        Example:
            Passing configuration parameters directly:
            >>> analysis = MyAnalysis(param1=1, param2="test")

            Passing a configuration object:
            >>> analysis = MyAnalysis(MyAnalysisConfig(param1=1, param2="test"))

        """
        pass

    def bind_memoryset(
        self,
        memoryset: LabeledMemoryset,
        memoryset_num_rows: int,
        memoryset_num_classes: int,
        lookup_count: int,
    ) -> None:
        """Inject memoryset dependencies into the analysis"""
        self.memoryset = memoryset
        self.memoryset_num_rows = memoryset_num_rows
        self.memoryset_num_classes = memoryset_num_classes
        self.lookup_count = lookup_count

    @abstractmethod
    def on_batch(
        self,
        memories_batch: list[LabeledMemory],
        neighbors_batch: list[list[LabeledMemoryLookup]],
    ) -> Iterable[tuple[UUID7, TMemoryMetrics]] | None:
        """
        Process a batch of memories and their neighbor lookups

        Params:
            memories_batch: a batch of memories to process
            neighbors_batch: a batch of memory lookups for the memories

        Returns:
            Optional list of tuples with individual memory ids and metrics to be added
        """
        pass

    @abstractmethod
    def after_all(self) -> TMemorysetMetrics | tuple[TMemorysetMetrics, Iterable[tuple[UUID7, TMemoryMetrics]]]:
        """
        Runs after all batches have been processed to compute any final metrics

        Returns:
            Either the memoryset aggregate metrics or a tuple containing:
            - the memoryset aggregate metrics
            - a list of tuples with individual memory ids and metrics to be added
        """
        pass


def run_analyses(
    memoryset: LabeledMemoryset,
    *analyses: MemorysetAnalysis,
    lookup_count: int = 15,
    show_progress_bar: bool = True,
    on_progress: OnProgressCallback | None = None,
    batch_size: int = 32,
    clear_metrics: bool = False,
) -> dict[str, Any]:
    """
    Run one or more analyses.

    Params:
        memoryset: Memoryset to analyze
        analyses: One or more analysis instances to be run in parallel
        lookup_count: Number of lookups to perform for each memory
        show_progress_bar: Whether to show a progress bar
        on_progress: Callback to report progress
        batch_size: Batch size for processing the memoryset
        clear_metrics: Whether to delete the metrics of all memories in the memoryset first

    Returns:
        A dictionary with the memoryset aggregate metrics for each analysis

    Examples:
    >>> run_analyses(
    ...     memoryset,
    ...     MemorysetDuplicateMetrics(potential_duplicate_threshold=0.95),
    ...     MemorysetProjectionAnalysis(),
    ...     MemorysetClusterAnalysis(min_cluster_size=10),
    ...     lookup_count=30,
    ...     clear_metrics=True,
    ... )
        {'duplicate': MemorysetDuplicateMetrics(num_duplicates=10),
         'projection': MemorysetProjectionMetrics(),
         'cluster': MemorysetClusterMetrics(cluster_metrics=[ClusterMetrics(cluster=0, memory_count=100), ClusterMetrics(cluster=1, memory_count=73)], num_outliers=21, num_clusters=2)}
    """
    memoryset_num_rows = memoryset.num_rows
    memoryset_num_classes = memoryset.num_classes
    for analysis in analyses:
        analysis.bind_memoryset(
            memoryset=memoryset,
            memoryset_num_rows=memoryset_num_rows,
            memoryset_num_classes=memoryset_num_classes,
            lookup_count=lookup_count,
        )

    if clear_metrics:
        logging.info(f"Clearing metrics for {memoryset_num_rows} memories")
        for memory_batch in batched(memoryset, 100):
            memoryset.update([LabeledMemoryUpdate(memory_id=m.memory_id, metrics=None) for m in memory_batch])

    def save_memory_metrics(
        metric_updates: dict[UUID7, dict],
    ):
        logging.debug(f"Saving metrics for {len(metric_updates)} memories")
        for id_metrics_tuples in batched(metric_updates.items(), 100):
            memoryset.update(
                [
                    LabeledMemoryUpdate(memory_id=memory_id, metrics=MemoryMetrics(**metrics))
                    for memory_id, metrics in id_metrics_tuples
                ]
            )

    are_lookups_required = any(analysis.requires_lookups for analysis in analyses)

    # add 3 batches for the final step of each analysis
    after_all_step_size = 3 * batch_size

    total_steps = len(analyses) * after_all_step_size
    if are_lookups_required:
        total_steps = memoryset_num_rows + (len(analyses) * after_all_step_size)

        offset = 0
        for memory_batch in tqdm(
            batched(memoryset, batch_size),
            total=memoryset_num_rows // batch_size,
            disable=not show_progress_bar,
        ):
            safely_call_on_progress(on_progress, offset, total_steps)

            # lookup with precomputed embeddings, to speed things up at the expense of not using query prompts
            neighbors_batch = memoryset._perform_lookup([m.embedding for m in memory_batch], count=lookup_count + 1)
            # remove exact matches by id to avoid confusion in duplicate analysis, or trim to correct count
            neighbors_batch = [
                [n for n in ns if n.memory_id != m.memory_id][:lookup_count]
                for ns, m in zip(neighbors_batch, memory_batch)
            ]

            memory_metrics: dict[UUID7, dict] = {m.memory_id: {} for m in memory_batch}
            for analysis in analyses:
                if not analysis.requires_lookups:
                    continue
                metrics_batch = analysis.on_batch(list(memory_batch), neighbors_batch)
                if metrics_batch is None:
                    continue
                for memory_id, metric in metrics_batch:
                    memory_metrics[memory_id] |= metric.model_dump()

            save_memory_metrics(memory_metrics)
            offset += batch_size
        else:
            safely_call_on_progress(on_progress, memoryset_num_rows, total_steps)

    memoryset_metrics: dict[str, BaseModel] = {}
    memory_metrics: dict[UUID7, dict] = {}
    for i, analysis in enumerate(analyses):
        safely_call_on_progress(on_progress, memoryset_num_rows + (i * after_all_step_size), total_steps)
        logging.info(f"Running finishing step for: {analysis.__class__.__name__}")
        result = analysis.after_all()
        if isinstance(result, tuple):
            memoryset_metrics[analysis.name] = result[0]
            for memory_id, metrics in result[1]:
                if memory_id not in memory_metrics:
                    memory_metrics[memory_id] = metrics.model_dump()
                else:
                    memory_metrics[memory_id] |= metrics.model_dump()
        else:
            memoryset_metrics[analysis.name] = result

    safely_call_on_progress(on_progress, total_steps, total_steps)

    save_memory_metrics(memory_metrics)
    return memoryset_metrics
