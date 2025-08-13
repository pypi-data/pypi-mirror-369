from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..models import LabelPredictionWithMemories
from .agent_workflow import AgentWorkflow
from .explain_prediction import ExplainPredictionContext


class ActionRecommendation(BaseModel):
    """Recommended actions to take based on the prediction and explanation"""

    action: Literal["remove_duplicates", "detect_mislabels", "add_memories", "finetuning"] = Field(
        ..., description="The recommended action to take"
    )
    rationale: str = Field(..., description="Explanation for why this action was recommended")


action_prediction_agent = AgentWorkflow(
    "anthropic:claude-3-7-sonnet-latest",
    deps_type=ExplainPredictionContext,
    input_type=LabelPredictionWithMemories,  # Use prediction directly as input
    result_type=ActionRecommendation,
    system_prompt=lambda deps: f"""
        # Task

        You are an intelligent action recommendation system for a retrieval augmented classification model.
        Based on prediction information, recommend the most important action to improve the model for {deps.model_description}.

        # Model Context

        This model classifies inputs into the following labels: {", ".join(deps.label_names)}.
        The overall average lookup score of the memories is: {deps.lookup_score_median:.0%} ± {deps.lookup_score_std:.0%}.

        # Your Role

        When given a prediction, analyze the situation and recommend ONE specific action to improve the model.
        Choose from these possible actions:

        1. **remove_duplicates**: When too many similar memories exist and drown out signals
        2. **detect_mislabels**: When memories appear to have incorrect labels
        3. **add_memories**: When new examples would help the model find better matches
        4. **finetuning**: When the embedding model has fundamental issues with similarity

        # Failure Patterns and Recommended Actions

        - If the input seems ambiguous or the expected label doesn't make sense → detect_mislabels
        - If retrieved memories have ambiguous meaning → detect_mislabels
        - If memories are similar in ways not related to classification (e.g., topic not sentiment) → finetuning
        - If similarity scores are too low → add_memories
        - If a few relevant memories are drowned out by many irrelevant ones → remove_duplicates
    """,
    prompt_template=lambda prediction: f"""
        Analyze the following prediction to recommend the most important action to improve model performance.

        # Prediction Information
        Input: "{prediction.input_value}"
        Expected Label: {prediction.expected_label_name}
        Predicted Label: {prediction.label_name}
        Prediction Confidence: {prediction.confidence:.0%}
        Average Memory Similarity: {sum(m.lookup_score for m in prediction.memories) / len(prediction.memories):.0%}

        # Memory Summary
        Number of Memories: {len(prediction.memories)}
        Memories with Expected Label: {sum(1 for m in prediction.memories if m.label_name == prediction.expected_label_name)}
        Memories with Predicted Label: {sum(1 for m in prediction.memories if m.label_name == prediction.label_name)}
        High Similarity Memories (>80%): {sum(1 for m in prediction.memories if m.lookup_score > 0.8)}
        High Influence Memories (>20%): {sum(1 for m in prediction.memories if m.attention_weight / sum(m.attention_weight for m in prediction.memories) > 0.2)}

        <memories>{"---".join([f"""
        Memory {i + 1}:
            Label: {memory.label_name}
            Influence: {memory.attention_weight / sum(m.attention_weight for m in prediction.memories):.0%}
            Similarity: {memory.lookup_score:.0%}
            Text: "{memory.value}"
        """
            for i, memory in enumerate(prediction.memories)]
        )}</memories>

        Recommend a single action that would be most effective at improving this prediction,
        and provide a clear rationale for your recommendation.
    """,
)
