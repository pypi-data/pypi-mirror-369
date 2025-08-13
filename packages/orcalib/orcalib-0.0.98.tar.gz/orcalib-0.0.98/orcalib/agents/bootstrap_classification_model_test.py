from unittest.mock import MagicMock, patch

import pytest

from .bootstrap_classification_model import (
    BootstrapClassificationModelInput,
    BootstrapClassificationModelResult,
    LabeledExample,
    bootstrap_classification_model,
    bootstrap_classification_model_agent,
)


def test_create_memoryset_and_model_input_validation():
    """Test that CreateMemorysetAndModelInput validates properly"""
    input_data = BootstrapClassificationModelInput(
        model_description="sentiment analysis of product reviews",
        label_names=["positive", "negative", "neutral"],
        num_examples_per_label=5,
    )

    assert input_data.model_description == "sentiment analysis of product reviews"
    assert input_data.label_names == ["positive", "negative", "neutral"]
    assert input_data.num_examples_per_label == 5
    assert input_data.initial_examples == []


def test_create_memoryset_and_model_input_with_examples():
    """Test that CreateMemorysetAndModelInput works with examples"""
    examples = [
        LabeledExample(text="This product is amazing!", label_name="positive"),
        LabeledExample(text="Terrible quality, don't buy", label_name="negative"),
        LabeledExample(text="It's okay, nothing special", label_name="neutral"),
    ]

    input_data = BootstrapClassificationModelInput(
        model_description="sentiment analysis of product reviews",
        label_names=["positive", "negative", "neutral"],
        initial_examples=examples,
        num_examples_per_label=5,
    )

    assert input_data.initial_examples is not None
    assert len(input_data.initial_examples) == 3
    assert input_data.initial_examples[0].text == "This product is amazing!"
    assert input_data.initial_examples[0].label_name == "positive"


def test_memoryset_and_model_result_validation():
    """Test that MemorysetAndModelResult validates properly"""
    generated_memories = [
        LabeledExample(
            text="I love this product!",
            label_name="positive",
        ),
        LabeledExample(
            text="This is the worst purchase ever",
            label_name="negative",
        ),
    ]

    result = BootstrapClassificationModelResult(
        model_description="sentiment analysis",
        label_names=["positive", "negative"],
        model_name="sentiment_analysis_model",
        generated_examples=generated_memories,
    )

    assert result.model_description == "sentiment analysis"
    assert result.label_names == ["positive", "negative"]
    assert len(result.generated_examples) == 2


@pytest.mark.asyncio
async def test_create_memoryset_and_model_with_examples():
    """Test the create_memoryset_and_model function with examples"""

    examples = [
        LabeledExample(text="This product exceeded my expectations!", label_name="positive"),
        LabeledExample(text="Complete waste of money", label_name="negative"),
    ]

    # Mock the agent to return a test result
    mock_result = MagicMock()
    mock_result.output = BootstrapClassificationModelResult(
        model_description="sentiment analysis",
        label_names=["positive", "negative"],
        model_name="sentiment_analysis_model",
        generated_examples=[
            LabeledExample(text="Amazing quality!", label_name="positive"),
            LabeledExample(text="Terrible product", label_name="negative"),
        ],
    )

    with patch.object(bootstrap_classification_model_agent, "run", return_value=mock_result):
        result = await bootstrap_classification_model(
            model_description="sentiment analysis",
            label_names=["positive", "negative"],
            initial_examples=examples,
            num_examples_per_label=1,
        )

        assert isinstance(result, BootstrapClassificationModelResult)
        assert len(result.generated_examples) == 2
