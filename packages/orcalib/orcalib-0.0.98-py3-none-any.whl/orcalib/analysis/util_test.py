import logging
import os

from datasets import ClassLabel, Dataset

from ..analysis import (
    MemorysetDuplicateAnalysis,
    group_potential_duplicates,
    run_analyses,
)
from ..memoryset import LabeledMemoryset

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


def test_group_potential_duplicates(memoryset: LabeledMemoryset):
    # Given a memoryset with some memories
    memoryset.insert(TEST_DATASET)
    # And a few potential duplicates
    memoryset.insert(
        [
            {"value": "the cats breaks a theory.", "label": 1},
            {"value": "A bird brings the fence", "label": 0},
            {"value": "the cats breaks a theorY", "label": 1},
            {"value": "The cats breaks a theory", "label": 1},
        ]
    )

    # And duplicate analysis is run to populate the metrics
    run_analyses(
        memoryset,
        MemorysetDuplicateAnalysis(potential_duplicate_threshold=0.95),
        lookup_count=3,
        show_progress_bar=False,
    )["duplicate"]
    memories = memoryset.query(filters=[("metrics.has_potential_duplicates", "==", True)])
    # When we group the potential duplicates
    potential_duplicate_groups = group_potential_duplicates(memoryset)
    # Then we get the correct number of groups
    assert len(potential_duplicate_groups) == 2
    # With the correct number of memories
    assert len(potential_duplicate_groups[0] | potential_duplicate_groups[1]) == len(memories)
    # And the correct sizes of the groups
    # Order is not stable, so this enables the assert
    group_sizes = sorted([len(group) for group in potential_duplicate_groups])
    assert group_sizes == [2, 4]  # 2 bird, 4 cat memories
