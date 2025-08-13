from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from uuid_utils.compat import UUID, uuid4, uuid7

from ..models import LabelPredictionMemoryLookup, LabelPredictionWithMemories
from .action_add_memories import (
    AddMemoryInput,
    AddMemoryRecommendations,
    AddMemorySuggestion,
    add_memories_agent,
    generate_memories,
)
from .explain_prediction import ExplainPredictionContext


def create_test_memory_lookup(prediction_id: UUID):
    return LabelPredictionMemoryLookup(
        prediction_id=prediction_id,
        value="Memory text about a product",
        label_name="positive",
        embedding=np.random.randn(10).astype(np.float32),
        memory_id=uuid7(),
        memory_version=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        edited_at=datetime.now(),
        metrics={},
        metadata={},
        label=0,
        source_id=None,
        lookup_score=0.9,
        attention_weight=0.5,
    )


def create_test_prediction():
    prediction_id = uuid4()
    return LabelPredictionWithMemories(
        prediction_id=prediction_id,
        anomaly_score=0.5,
        label=0,
        label_name="positive",
        expected_label=1,
        expected_label_name="negative",
        confidence=0.8,
        input_value="This product was not what I expected.",
        input_embedding=np.random.randn(10).astype(np.float32),
        logits=np.random.randn(2).astype(np.float32),
        timestamp=datetime.now(),
        memories=[
            create_test_memory_lookup(prediction_id),
            create_test_memory_lookup(prediction_id),
        ],
    )


def test_add_memory_recommendations_validation():
    """Test that AddMemoryRecommendations validates properly"""
    suggestions = [
        AddMemorySuggestion(value="I was disappointed with this product.", label_name="negative"),
        AddMemorySuggestion(value="This product fell short of my expectations.", label_name="negative"),
    ]

    recommendations = AddMemoryRecommendations(memories=suggestions)
    assert len(recommendations.memories) == 2
    assert recommendations.memories[0].value == "I was disappointed with this product."
    assert recommendations.memories[0].label_name == "negative"
