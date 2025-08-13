from uuid import uuid4

from PIL import Image as pil

from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset
from .analysis import run_analyses
from .analysis_duplicate import MemorysetDuplicateAnalysis, MemorysetDuplicateMetrics


def test_text_duplicates():
    # Given a memoryset with some duplicate text entries
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["climate", "economy", "sports"],
    )
    memoryset.insert(
        [
            {"value": "about climate change", "label": 0},
            {"value": "about the economy", "label": 1},
            {"value": "about sports", "label": 2},
            {"value": "about sports", "label": 2},  # Duplicate
            {"value": "about sports", "label": 2},  # Duplicate
            {"value": "about climate change", "label": 0},  # Duplicate
        ]
    )
    # When we run a duplicate analysis
    result = run_analyses(
        memoryset,
        MemorysetDuplicateAnalysis(),
        lookup_count=2,
        show_progress_bar=False,
    )["duplicate"]
    # Then the expected number of duplicates is returned
    assert isinstance(result, MemorysetDuplicateMetrics)
    assert result.num_duplicates == 3
    # And the correct memories are marked as duplicates
    duplicate_memories = memoryset.query(filters=[("metrics.is_duplicate", "==", True)])
    assert len(duplicate_memories) == 3
    assert memoryset[0] in duplicate_memories
    assert memoryset[2] in duplicate_memories
    assert memoryset[3] in duplicate_memories


def test_image_duplicates():
    # Given a memoryset with some duplicate image entries
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.CLIP_BASE,
        label_names=["red", "green"],
    )
    memoryset.insert(
        [
            {"value": pil.new("RGB", (100, 100), color=(255, 0, 0)), "label": 0},
            {"value": pil.new("RGB", (100, 100), color=(0, 255, 0)), "label": 1},
            {"value": pil.new("RGB", (100, 100), color=(255, 0, 0)), "label": 0},  # Duplicate
        ]
    )
    # When we run a duplicate analysis
    result = run_analyses(memoryset, MemorysetDuplicateAnalysis(), lookup_count=1, show_progress_bar=False)["duplicate"]
    # Then the expected number of duplicates is returned
    assert isinstance(result, MemorysetDuplicateMetrics)
    assert result.num_duplicates == 1
    # And the correct memories are marked as duplicates
    duplicate_memories = memoryset.query(filters=[("metrics.is_duplicate", "==", True)])
    assert len(duplicate_memories) == 1
    assert memoryset[0] in duplicate_memories


def test_potential_duplicates():
    # Given a memoryset with some entries that are similar but not identical
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["technology"],
    )
    memoryset.insert(
        [
            {"value": "Ai is transforming tech", "label": 0},
            {"value": "AI is transforming technology", "label": 0},  # Possible Duplicate
            {"value": "AI is transforming technology", "label": 0},  # Duplicate
            {"value": "Machine learning is a subset of artificial intelligence", "label": 0},
            {"value": "Quantum computing is an emerging technology", "label": 0},
        ]
    )
    # When we run a duplicate analysis with a lower threshold for potential duplicates
    result = run_analyses(
        memoryset,
        MemorysetDuplicateAnalysis(potential_duplicate_threshold=0.95),
        lookup_count=3,
        show_progress_bar=False,
    )["duplicate"]
    # Then a valid result is returned
    assert isinstance(result, MemorysetDuplicateMetrics)
    assert result.num_duplicates == 1
    # And the potential duplicates are found
    potential_duplicates = memoryset.query(filters=[("metrics.has_potential_duplicates", "==", True)])
    assert len(potential_duplicates) == 3
    assert set(memoryset[0].metrics.get("potential_duplicate_memory_ids") or []) == set(
        [memoryset[1].memory_id, memoryset[2].memory_id]
    )
    assert memoryset[1].metrics.get("potential_duplicate_memory_ids") == [memoryset[0].memory_id]
    assert memoryset[2].metrics.get("potential_duplicate_memory_ids") == [memoryset[0].memory_id]
