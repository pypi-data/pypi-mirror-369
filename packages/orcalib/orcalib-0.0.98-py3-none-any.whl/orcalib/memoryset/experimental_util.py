from __future__ import annotations

import logging
import time
from typing import Counter, cast

from datasets import Dataset
from pydantic import BaseModel
from tqdm.auto import tqdm

from ..utils.dataset import parse_dataset
from .memory_types import LabeledMemoryUpdate
from .memoryset import LabeledMemory, LabeledMemoryLookup, LabeledMemoryset


def insert_useful_memories(
    memoryset: LabeledMemoryset,
    dataset: Dataset,
    lookup_count: int = 15,
    batch_size: int = 32,
    value_column: str = "value",
    label_column: str = "label",
    source_id_column: str | None = None,
    other_columns_as_metadata: bool = True,
    compute_embeddings: bool = True,
    min_confidence: float = 0.85,
) -> int:
    """
    Inserts useful memories into a memoryset by evaluating their impact on prediction accuracy.

    This function iterates through a dataset and selectively adds rows to the memoryset if doing so
    improves the model's accuracy. It ensures that the memoryset has enough initial memories for
    lookup operations and uses a confidence threshold to determine whether a memory is useful.

    Args:
        memoryset: The memoryset to which useful memories will be added.
        dataset: Data to insert into the memoryset.
        lookup_count: The number of nearest neighbors to retrieve during memory lookup. Defaults to 15.
        batch_size: The batch size for memory insertion operations. Defaults to 32.
        value_column: The column name in the dataset containing memory values. Defaults to "value".
        label_column: The column name in the dataset containing memory labels. Defaults to "label".
        source_id_column: The column name in the dataset containing source IDs, or None if not applicable. Defaults to None.
        other_columns_as_metadata: Whether to treat other columns in the dataset as metadata. Defaults to True.
        compute_embeddings: Whether to compute embeddings for the inserted memories. Defaults to True.
        min_confidence: The minimum confidence threshold for a memory to be considered useful. Defaults to 0.85.

    Returns:
        The number of memories successfully inserted into the memoryset.

    Notes:
        - This method currently supports only text-based memories.
        - It is experimental and subject to change in future versions.
    """
    insert_count = 0  # The number of rows we've actually inserted
    total_data_count = len(dataset)
    assert total_data_count > 0, "No data provided"

    # Parse the dataset
    dataset = parse_dataset(
        dataset,
        value_column=value_column,
        label_column=label_column,
        source_id_column=source_id_column,
        other_columns_as_metadata=other_columns_as_metadata,
    )

    # We need at least lookup_count memories in the memoryset in order to do any predictions.
    # If we don't have enough memories we'll add lookup_count elements to the memoryset.
    missing_mem_count = max(0, lookup_count - len(memoryset))
    if missing_mem_count:
        if len(dataset) <= missing_mem_count:
            logging.info(
                f"Memoryset needs a minimum of {missing_mem_count} memories for lookup, but only contains {len(memoryset)}."
                f"{total_data_count}. Adding all {total_data_count} instances to the memoryset."
            )
            memoryset.insert(
                dataset,
                batch_size=batch_size,
                compute_embeddings=compute_embeddings,
                show_progress_bar=False,
            )
            return total_data_count

        logging.info(f"Adding {missing_mem_count} memories to reach minimum required count: {lookup_count}")

        memoryset.insert(
            dataset.select(range(missing_mem_count)),
            batch_size=batch_size,
            compute_embeddings=compute_embeddings,
            show_progress_bar=False,
        )
        insert_count = missing_mem_count
        dataset = dataset.select(range(missing_mem_count, len(dataset)))

    assert len(dataset) > 0, "No data left to add to memoryset. This shouldn't be possible!"

    # Now we can start predicting and adding only the useful memories
    for row in tqdm(dataset, total=total_data_count - missing_mem_count):
        row = cast(dict, row)
        lookups = memoryset.lookup(row["value"], count=lookup_count)
        counter = Counter([memory.label for memory in lookups])
        # get the count for row["label"] if it exists in the counter, otherwise default to 0
        confidence = counter[row["value"]] / lookup_count if lookup_count > 0 else 0
        if confidence < min_confidence:
            memoryset.insert(
                [row],
                compute_embeddings=compute_embeddings,
                show_progress_bar=False,
                other_columns_as_metadata=other_columns_as_metadata,
            )
            insert_count += 1

    return insert_count


LAST_SUGGESTED_MISLABEL_TIME_KEY = "last_suggested_time"
MISLABEL_SUGGESTION_COUNT_KEY = "mislabel_suggestion_count"
LABEL_CONFIRMED_TIME_KEY = "label_confirmed_time"


class CascadingEditSuggestion(BaseModel):
    neighbor: LabeledMemoryLookup
    suggested_label: int
    lookup_score: float


def get_cascading_edits_suggestions(
    self: LabeledMemoryset,
    memory: LabeledMemory,
    *,
    old_label: int,
    new_label: int,
    max_neighbors: int = 50,
    max_validation_neighbors: int = 10,
    similarity_threshold: float | None = None,
    only_if_has_old_label: bool = True,
    exclude_if_new_label: bool = True,
    suggestion_cooldown_time: float = 3600.0 * 24.0,  # 1 day
    label_confirmation_cooldown_time: float = 3600.0 * 24.0 * 7,  # 1 week
    _current_time: float | None = None,
) -> list[CascadingEditSuggestion]:
    """
    Suggests cascading edits for a given memory based on nearby points with similar labels.

    This function is triggered after a user changes a memory's label. It looks for nearby
    candidates in embedding space that may be subject to similar relabeling and returns them
    as suggestions. The system uses scoring heuristics, label filters, and cooldown tracking
    to reduce noise and improve usability.

    Params:
        memory: The memory whose label was just changed.
        old_label: The label this memory used to have.
        new_label: The label it was changed to.
        max_neighbors: Maximum number of neighbors to consider.
        max_validation_neighbors: Maximum number of neighbors to use for label suggestion.
        similarity_threshold: If set, only include neighbors with a lookup score above this threshold.
        only_if_has_old_label: If True, only consider neighbors that have the old label.
        exclude_if_new_label: If True, exclude neighbors that already have the new label.
        suggestion_cooldown_time: Minimum time (in seconds) since the last suggestion for a neighbor
            to be considered again.
        label_confirmation_cooldown_time: Minimum time (in seconds) since a neighbor's label was confirmed
            to be considered for suggestions.
        _current_time: Optional override for the current timestamp (useful for testing).

    Returns:
        A list of CascadingEditSuggestion objects, each containing a neighbor and the suggested new label.
    """
    memoryset = self
    _current_time = _current_time or time.time()

    # lookup with precomputed embeddings, to speed things up at the expense of not using query prompts
    neighbors = memoryset._perform_lookup([memory.embedding], count=max_neighbors)[0]

    pass

    # First filter neighbors based on viability criteria, so we don't waste time on lookups for neighbors that are not viable
    neighbors = [
        neighbor
        for neighbor in neighbors
        if _is_viable_cascade_edit_neighbor(
            original_memory=memory,
            neighbor=neighbor,
            old_label=old_label,
            new_label=new_label,
            similarity_threshold=similarity_threshold,
            only_if_has_old_label=only_if_has_old_label,
            exclude_if_new_label=exclude_if_new_label,
            suggestion_cooldown_time=suggestion_cooldown_time,
            label_confirmation_cooldown_time=label_confirmation_cooldown_time,
            current_time=_current_time,
        )
    ]

    pass

    # Get suggested labels for the remaining neighbors
    suggested_labels = [
        get_suggested_label(memoryset=memoryset, memory=neighbor, neighbor_count=max_validation_neighbors)
        for neighbor in neighbors
    ]

    # Filter out neighbors that did not receive a valid suggestion
    results = [
        CascadingEditSuggestion(
            neighbor=neighbor,
            suggested_label=suggested_label,
            lookup_score=neighbor.lookup_score,
        )
        for neighbor, suggested_label in zip(neighbors, suggested_labels)
        if suggested_label is not None
    ]

    # Update the last suggested time in metadata
    if results:
        for suggestion in results:
            suggestion.neighbor.metadata[LAST_SUGGESTED_MISLABEL_TIME_KEY] = _current_time
            suggest_count = suggestion.neighbor.metadata.get(MISLABEL_SUGGESTION_COUNT_KEY, 0)
            assert isinstance(
                suggest_count, int
            ), f"Expected {MISLABEL_SUGGESTION_COUNT_KEY} to be an int, but got {type(suggest_count)}"
            suggestion.neighbor.metadata[MISLABEL_SUGGESTION_COUNT_KEY] = suggest_count + 1
        memory_updates = [
            LabeledMemoryUpdate(
                memory_id=suggestion.neighbor.memory_id,
                metadata=suggestion.neighbor.metadata,
            )
            for suggestion in results
        ]
        memoryset.update(memory_updates)

    return results


def get_suggested_label(memoryset: LabeledMemoryset, memory: LabeledMemory, *, neighbor_count: int) -> int | None:
    """
    Suggests a new label for a given memory based on its neighbors.
    This function looks at the labels of the nearest neighbors of a memory and suggests
    the most common label among them as a new label for the memory.
    Args:
        memoryset: The memoryset containing the memories.
        memory: The memory for which to suggest a new label.
        neighbor_count: The number of nearest neighbors to consider.
    Returns:
        None if no neighbors are found or the memory's label is already the most common among neighbors.
        The most common label among the neighbors if a suggestion is warranted.
    """
    # lookup with precomputed embeddings, to speed things up at the expense of not using query prompts
    neighbors = memoryset._perform_lookup([memory.embedding], count=neighbor_count + 1)[0]
    neighbors = [n for n in neighbors if n.memory_id != memory.memory_id]
    if not neighbors:
        return None
    # Count the labels of the neighbors
    label_counts = Counter(neighbor.label for neighbor in neighbors)
    # Remove the current label from the counts
    current_label = memory.label
    if not label_counts:
        return None
    # Find the most common label among the neighbors
    most_common_label, most_common_count = label_counts.most_common(1)[0]
    if most_common_label == current_label:
        return None
    return most_common_label


def _metadata_value_to_float(metadata_value: str | int | float | bool | None) -> float | None:
    """
    Convert a metadata value to a float for comparison purposes.

    Args:
        metadata_value: The value from metadata, which can be of type str, int, float, or bool.

    Returns:
        A float representation of the metadata value, or None if the value cannot be converted.

    Raises:
        ValueError: If the metadata value is a string that cannot be converted to a float, or if the type
            is unsupported.
    """
    if metadata_value is None:
        return None
    if isinstance(metadata_value, (bool, int, float)):
        return float(metadata_value)
    if isinstance(metadata_value, str):
        try:
            return float(metadata_value)
        except ValueError:
            raise ValueError(f"Cannot convert metadata value to float: {metadata_value}")
    raise ValueError(f"Unsupported metadata value: {metadata_value}")


def _is_viable_cascade_edit_neighbor(
    original_memory: LabeledMemory,
    neighbor: LabeledMemoryLookup,
    old_label: int,
    new_label: int,
    current_time: float,
    only_if_has_old_label: bool = True,
    exclude_if_new_label: bool = True,
    similarity_threshold: float | None = None,
    suggestion_cooldown_time: float = 3600.0,
    label_confirmation_cooldown_time: float = 3600.0 * 24.0 * 7,  # 1 week
) -> bool:
    """
    Check if a neighbor is a viable candidate for cascading edits.

    Args:
        neighbor: The neighbor memory to evaluate.
        old_label: The label that was changed.
        new_label: The new label that was applied.
        current_time: The current timestamp, used to evaluate cooldown periods.
        only_if_has_old_label: If True, only consider neighbors that have the old label.
        exclude_if_new_label: If True, exclude neighbors that already have the new label.
        similarity_threshold: If set, only include neighbors with a lookup score above this threshold.
        suggestion_cooldown_time: Minimum time (in seconds) since the last suggestion for a neighbor
            to be considered again.
        label_confirmation_cooldown_time: Minimum time (in seconds) since a neighbor's label was confirmed
            to be considered for suggestions.

    Returns:
        True if the neighbor is a viable candidate for cascading edits, False otherwise.
    """
    # Don't suggest edits to the original memory itself
    if neighbor.memory_id == original_memory.memory_id:
        return False

    # Filter by similarity threshold
    if similarity_threshold is not None and neighbor.lookup_score < similarity_threshold:
        return False

    # Filter by label match
    if only_if_has_old_label and neighbor.label != old_label:
        return False
    if exclude_if_new_label and neighbor.label == new_label:
        return False

    # Filter by cooldown
    if LAST_SUGGESTED_MISLABEL_TIME_KEY in neighbor.metadata:
        last_suggested_time = _metadata_value_to_float(neighbor.metadata[LAST_SUGGESTED_MISLABEL_TIME_KEY])
        if last_suggested_time is not None and (current_time - last_suggested_time) < suggestion_cooldown_time:
            return False

    if LABEL_CONFIRMED_TIME_KEY in neighbor.metadata:
        label_confirmed_time = _metadata_value_to_float(neighbor.metadata.get(LABEL_CONFIRMED_TIME_KEY))
        if (
            label_confirmed_time is not None
            and (current_time - label_confirmed_time) < label_confirmation_cooldown_time
        ):
            return False

    return True
