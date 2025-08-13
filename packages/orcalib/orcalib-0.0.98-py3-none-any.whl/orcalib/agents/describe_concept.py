from pydantic import BaseModel

from ..models import LabelPredictionWithMemories
from .agent_workflow import AgentWorkflow


class DescribeConceptContext(BaseModel):
    """
    Describe the conceptual group of a set of memories.
    """

    base_decision_description: str  # e.g. "Classification of news articles by topic."


class ConceptualGroupInstance(BaseModel):
    outer_concept_label: str  # e.g. "Business"
    representative_examples: list[
        str
    ]  # e.g. ["Apple releases its new iPhone model", "NASA announces a new mission to Mars"]
    contrasting_examples: list[str]  # e.g. ["The local football team won their game", "The stock market crashed today"]


class DescribeConceptResult(BaseModel):
    """
    Result of the DescribeConcept agent.

    The result is an object with two fields:
    - name: A short, descriptive label that captures the essence of the concept.
    - description: A detailed description of the concept.
    """

    name: str
    description: str


def system_prompt(deps: DescribeConceptContext) -> str:
    return f"""
        You are part of a system whose main goal is: {deps.base_decision_description}.
        Your job is to provide a name and description for a distinct subgroup of examples that are 
        similar to each, but conceptually distinct from other subgroups within the same top-level category.

        You are given a set of examples that are similar to each other, and a set of examples that have
        the same top-level category but are conceptually distinct from the first set.

        Your goal is to provide maximum clarity and conciseness in your answer. Don't refer to specific
        examples in your description; instead, focus on making this concept clear - and distinct - from
        other concepts (within the same top-level category).
    """


def prompt_template(prediction: ConceptualGroupInstance) -> str:
    return f"""
        Within the category "{prediction.outer_concept_label}", you are given the following examples
        that form a distinct conceptual subgroup:
        {"\n".join(prediction.representative_examples)}

        You are also given examples that are similar to the first set but are conceptually distinct:
        {"\n".join(prediction.contrasting_examples)}

        Please provide a name and description for the distinct conceptual subgroup based on the
        examples and contrasting examples. The name should be a short, descriptive label that captures 
        the essence of the concept that would be accessible to a domain expert. 
    """


# Provide your answer in json, as follows:
# {{
#     "name": "<name>",
#     "description": "<description>"
# }}
# """

describe_concept_agent = AgentWorkflow(
    "anthropic:claude-3-7-sonnet-latest",
    deps_type=DescribeConceptContext,
    input_type=ConceptualGroupInstance,
    result_type=DescribeConceptResult,
    system_prompt=system_prompt,
    prompt_template=prompt_template,
)
