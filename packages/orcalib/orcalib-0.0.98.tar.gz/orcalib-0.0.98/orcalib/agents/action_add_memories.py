from pydantic import BaseModel, Field

from ..memoryset.memory_types import LabeledMemoryInsert
from ..models import LabelPredictionWithMemories
from .agent_workflow import AgentWorkflow
from .explain_prediction import ExplainPredictionContext


class AddMemoryInput(BaseModel):
    """Input for the add memories agent"""

    input_text: str
    expected_label_name: str
    predicted_label_name: str
    explanation: str
    num_memories: int = 3


class AddMemorySuggestion(BaseModel):
    """A suggested memory to add to the memory store"""

    value: str
    label_name: str


class AddMemoryRecommendations(BaseModel):
    """Recommendations for memories to add"""

    memories: list[AddMemorySuggestion]


add_memories_agent = AgentWorkflow(
    "anthropic:claude-3-7-sonnet-latest",
    deps_type=ExplainPredictionContext,
    input_type=AddMemoryInput,
    result_type=AddMemoryRecommendations,
    system_prompt=lambda deps: f"""
        # Task

        Your job is to generate new memories for a retrieval-augmented classification model
        for {deps.model_description}. The model classifies inputs into the following labels:
        {", ".join(deps.label_names)}.

        # Context

        When a model makes an incorrect prediction because it can't find similar enough examples (called as memories)
        in its database, adding new memories similar to the input but with clearer signals can help.

        # Your Role

        Given an input where the model made an incorrect prediction, generate new memories that:
        1. Are similar to the original input
        2. Have clear signals for the expected label
        3. Maintain the same core meaning/topic as the original input
        4. Have different phrasing to create linguistic diversity

        # Guidelines

        - Maintain the core topic/subject of the original input
        - Create variations by adding context, changing sentence structure, etc.
    """,
    prompt_template=lambda input: f"""
        Create {input.num_memories} new memories that are similar to the following input but with clearer
        signals for the expected label.

        Original Input: "{input.input_text}"
        Expected Label: {input.expected_label_name}
        Predicted Label (incorrectly): {input.predicted_label_name}

        Explanation for incorrect prediction: {input.explanation}

        Generate {input.num_memories} memories that:
        1. Are similar to the original input
        2. Have clear signals for the {input.expected_label_name} label
        3. Maintain the same topic/subject as the original input
        4. Use different phrasings and vocabulary
    """,
)


async def generate_memories(
    prediction: LabelPredictionWithMemories, explanation: str, context: ExplainPredictionContext, num_memories: int = 3
) -> AddMemoryRecommendations:
    """
    Generate memory suggestions for a prediction

    Args:
        prediction: The prediction to generate memories for
        explanation: Explanation of the prediction
        context: Context for the explanation agent
        num_memories: Number of memories to generate

    Returns:
        Memory recommendations
    """
    # Add type safety checks
    if not isinstance(prediction.input_value, str):
        raise TypeError("Only text inputs supported for memory creation")

    missing_fields = []
    if prediction.expected_label_name is None:
        missing_fields.append("expected_label_name")
    if prediction.label_name is None:
        missing_fields.append("label_name")

    if missing_fields:
        raise ValueError(f"Missing label information in prediction: {', '.join(missing_fields)}")

    # Prepare input for the add memories agent
    input_data = AddMemoryInput(
        input_text=prediction.input_value,
        expected_label_name=prediction.expected_label_name,  # type: ignore[arg-type]
        predicted_label_name=prediction.label_name,  # type: ignore[arg-type]
        explanation=explanation,
        num_memories=num_memories,
    )

    # Generate memory suggestions
    result = await add_memories_agent.run(input_data, deps=context)
    return result.output
