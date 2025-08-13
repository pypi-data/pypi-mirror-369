import pytest
from pydantic_ai.models.test import TestModel

from .agent_workflow import AgentWorkflow
from .describe_class_patterns import (
    ClassPatternsDescription,
    ClassPatternsInput,
    ClassRepresentatives,
    DescribeClassPatternsContext,
    describe_class_patterns_agent,
    prompt_template,
    system_prompt,
)


@pytest.mark.asyncio
async def test_describe_class_patterns_agent():
    """Test the class patterns description agent with test data."""

    # Create agent with test model directly
    test_agent = AgentWorkflow(
        TestModel(),
        deps_type=DescribeClassPatternsContext,
        input_type=ClassPatternsInput,
        result_type=ClassPatternsDescription,
        system_prompt=system_prompt,
        prompt_template=prompt_template,
    )

    # Create test input data
    context = DescribeClassPatternsContext(memoryset_description="sentiment analysis of product reviews")

    class_reps = [
        ClassRepresentatives(
            label=0,
            label_name="negative",
            representative_values=[
                "This product is terrible and broke immediately",
                "Worst purchase ever, complete waste of money",
                "Absolutely awful quality, would not recommend",
            ],
        ),
        ClassRepresentatives(
            label=1,
            label_name="positive",
            representative_values=[
                "Amazing product, exceeded all expectations!",
                "Love this item, fantastic quality and fast shipping",
                "Perfect product, would definitely buy again",
            ],
        ),
    ]

    agent_input = ClassPatternsInput(class_representatives=class_reps)

    # Test the agent
    result = await test_agent.run(agent_input, deps=context)

    # Verify the result
    assert isinstance(result.output, ClassPatternsDescription)
    assert isinstance(result.output.summary, str)
    assert len(result.output.classes) > 0


def test_class_patterns_input_validation():
    """Test input validation for the agent models."""

    # Test ClassRepresentatives
    class_rep = ClassRepresentatives(label=0, label_name="test_class", representative_values=["example 1", "example 2"])
    assert class_rep.label == 0
    assert class_rep.label_name == "test_class"
    assert len(class_rep.representative_values) == 2

    # Test ClassPatternsInput
    agent_input = ClassPatternsInput(class_representatives=[class_rep])
    assert len(agent_input.class_representatives) == 1

    # Test DescribeClassPatternsContext
    context = DescribeClassPatternsContext(memoryset_description="test dataset")
    assert context.memoryset_description == "test dataset"

    # Test default context
    default_context = DescribeClassPatternsContext()
    assert default_context.memoryset_description == "data classification"


def test_prompt_generation():
    """Test that prompts are generated correctly."""

    # Create test input
    class_reps = [
        ClassRepresentatives(label=0, label_name="negative", representative_values=["bad example", "poor quality"]),
        ClassRepresentatives(
            label=1, label_name=None, representative_values=["good example"]  # Test with no label name
        ),
    ]

    agent_input = ClassPatternsInput(class_representatives=class_reps)
    context = DescribeClassPatternsContext(memoryset_description="test classification")

    # Test system prompt generation
    system_prompt = describe_class_patterns_agent.make_system_prompt(context)
    assert "test classification" in system_prompt
    assert "data analyst" in system_prompt.lower()

    # Test user prompt generation
    user_prompt = describe_class_patterns_agent.make_prompt(agent_input, context)
    assert "negative" in user_prompt
    assert "Class 1" in user_prompt  # Should use fallback for missing label name
    assert "bad example" in user_prompt
    assert "good example" in user_prompt
