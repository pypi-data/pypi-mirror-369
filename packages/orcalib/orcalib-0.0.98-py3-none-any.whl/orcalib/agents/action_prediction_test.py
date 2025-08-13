from datetime import datetime

import numpy as np
import pytest
from pydantic_ai.models.test import TestModel
from uuid_utils.compat import UUID, uuid4, uuid7

from ..models import LabelPredictionMemoryLookup, LabelPredictionWithMemories
from .action_prediction import ActionRecommendation, action_prediction_agent
from .explain_prediction import ExplainPredictionContext


# Reuse the helper functions from explain_prediction_test
def create_test_memory_lookup(prediction_id: UUID):
    return LabelPredictionMemoryLookup(
        prediction_id=prediction_id,
        value="Memory 1 text",
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
        input_value="This is a test input",
        input_embedding=np.random.randn(10).astype(np.float32),
        logits=np.random.randn(2).astype(np.float32),
        timestamp=datetime.now(),
        memories=[
            create_test_memory_lookup(prediction_id),
            create_test_memory_lookup(prediction_id),
        ],
    )


@pytest.mark.asyncio
async def test_action_prediction_agent(llm_test_model: TestModel):
    """Test basic functionality of the action prediction agent"""
    prediction = create_test_prediction()
    context = ExplainPredictionContext(
        model_description="sentiment analysis",
        lookup_score_median=0.6,
        lookup_score_std=0.2,
        label_names=["positive", "negative"],
    )

    # Run the action prediction agent
    result = await action_prediction_agent.run(prediction, deps=context, model=llm_test_model)

    # Verify the result
    assert isinstance(result.output, ActionRecommendation)
    assert result.output.action in ["remove_duplicates", "detect_mislabels", "add_memories", "finetuning"]
    assert len(result.output.rationale) > 0


@pytest.mark.asyncio
async def test_action_prediction_with_different_context(llm_test_model: TestModel):
    """Test that the agent adapts to different context parameters"""
    prediction = create_test_prediction()

    # Create a different context
    context = ExplainPredictionContext(
        model_description="toxicity detection",  # Different model purpose
        lookup_score_median=0.8,  # Higher median similarity
        lookup_score_std=0.1,  # Lower standard deviation
        label_names=["toxic", "non-toxic"],  # Different labels
    )

    # Run the agent with modified context
    result = await action_prediction_agent.run(prediction, deps=context, model=llm_test_model)

    # Verify the result still meets expectations
    assert isinstance(result.output, ActionRecommendation)
    assert result.output.action in ["remove_duplicates", "detect_mislabels", "add_memories", "finetuning"]
    assert len(result.output.rationale) > 0


@pytest.mark.asyncio
async def test_action_prediction_with_modified_prediction(llm_test_model: TestModel):
    """Test with a prediction that has different characteristics"""
    prediction_id = uuid4()

    # Create memories with a different label
    memories = [
        LabelPredictionMemoryLookup(
            prediction_id=prediction_id,
            value="This is a negative review.",
            label_name="negative",
            embedding=np.random.randn(10).astype(np.float32),
            memory_id=uuid7(),
            memory_version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            edited_at=datetime.now(),
            metrics={},
            metadata={},
            label=1,
            source_id=None,
            lookup_score=0.85,
            attention_weight=0.6,
        ),
        LabelPredictionMemoryLookup(
            prediction_id=prediction_id,
            value="I didn't like this product at all.",
            label_name="negative",
            embedding=np.random.randn(10).astype(np.float32),
            memory_id=uuid7(),
            memory_version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            edited_at=datetime.now(),
            metrics={},
            metadata={},
            label=1,
            source_id=None,
            lookup_score=0.75,
            attention_weight=0.4,
        ),
    ]

    # Create a prediction with different characteristics
    prediction = LabelPredictionWithMemories(
        prediction_id=prediction_id,
        anomaly_score=0.2,
        label=1,  # Different predicted label
        label_name="negative",
        expected_label=0,  # Different expected label
        expected_label_name="positive",
        confidence=0.95,  # Higher confidence
        input_value="I really loved this product!",  # Clear positive sentiment
        input_embedding=np.random.randn(10).astype(np.float32),
        logits=np.random.randn(2).astype(np.float32),
        timestamp=datetime.now(),
        memories=memories,
    )

    context = ExplainPredictionContext(
        model_description="sentiment analysis",
        lookup_score_median=0.6,
        lookup_score_std=0.2,
        label_names=["positive", "negative"],
    )

    # Run the action prediction agent
    result = await action_prediction_agent.run(prediction, deps=context, model=llm_test_model)

    # Verify the result
    assert isinstance(result.output, ActionRecommendation)
    assert result.output.action in ["remove_duplicates", "detect_mislabels", "add_memories", "finetuning"]
    assert len(result.output.rationale) > 0


@pytest.mark.asyncio
async def test_action_prediction_system_prompt():
    """Test that the system prompt is correctly generated"""
    context = ExplainPredictionContext(
        model_description="sentiment analysis",
        lookup_score_median=0.6,
        lookup_score_std=0.2,
        label_names=["positive", "negative"],
    )

    # Get the system prompt
    system_prompt = action_prediction_agent.make_system_prompt(context)
    # Check that key elements are present
    assert "sentiment analysis" in system_prompt
    assert "positive" in system_prompt
    assert "negative" in system_prompt
    assert "remove_duplicates" in system_prompt
    assert "detect_mislabels" in system_prompt
    assert "add_memories" in system_prompt
    assert "finetuning" in system_prompt
    assert "60%" in system_prompt  # lookup_score_median as percentage
    assert "20%" in system_prompt  # lookup_score_std as percentage


@pytest.mark.asyncio
async def test_action_prediction_integration(llm_test_model: TestModel):
    """Test an end-to-end flow combining explanation and action recommendation"""
    from .explain_prediction import explain_prediction_agent

    prediction = create_test_prediction()
    context = ExplainPredictionContext(
        model_description="sentiment analysis",
        lookup_score_median=0.6,
        lookup_score_std=0.2,
        label_names=["positive", "negative"],
    )

    # First get explanation
    explanation_result = await explain_prediction_agent.run(prediction, deps=context, model=llm_test_model)
    assert isinstance(explanation_result.output, str)

    # Then get action recommendation
    action_result = await action_prediction_agent.run(prediction, deps=context, model=llm_test_model)
    assert isinstance(action_result.output, ActionRecommendation)

    # Verify the result
    assert action_result.output.action in ["remove_duplicates", "detect_mislabels", "add_memories", "finetuning"]
    assert len(action_result.output.rationale) > 0
