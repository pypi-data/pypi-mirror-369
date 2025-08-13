from typing import List, Optional

from pydantic import BaseModel, Field

from .agent_workflow import AgentWorkflow


class LabeledExample(BaseModel):
    """An example input with its expected label name"""

    text: str
    label_name: str


class BootstrapClassificationModelInput(BaseModel):
    """Input for creating a new classification model"""

    model_description: str
    label_names: list[str]
    initial_examples: list[LabeledExample] = []
    num_examples_per_label: int = 10


class BootstrapClassificationModelResult(BaseModel):
    """Result containing the memoryset and model configurations"""

    model_description: str
    label_names: list[str]

    model_name: str

    generated_examples: list[LabeledExample] = Field(default_factory=list, min_length=1)

    def generated_examples_to_list(self) -> list[dict[str, int | str]]:
        """Convert the generated examples to a list of dictionaries. Note that it also converts the labels to the index of the label in the label_names list.

        Returns:
            list[dict[str, int | str]]: A list of dictionaries with the text and label index.
        """
        inverted_label_names: dict[str, int] = {v: i for i, v in enumerate(self.label_names)}

        return [
            {
                "text": example.text,
                "label_name": inverted_label_names[example.label_name],
            }
            for example in self.generated_examples
        ]


bootstrap_classification_model_agent = AgentWorkflow(
    "anthropic:claude-3-7-sonnet-latest",
    input_type=BootstrapClassificationModelInput,
    result_type=BootstrapClassificationModelResult,
    system_prompt="""
        # Task

        You are an expert AI system for generating high-quality training examples for classification tasks.
        Your job is to create diverse, realistic examples that will enable a classification model to perform well on the specified task.

        # Your Role

        Given a model description, set of labels, and optional initial examples, you will:

        **Generate a Model Name**: Create a concise, descriptive name for the classification model
        **Generate Examples**: Create diverse, high-quality training examples for each label

        # Model Name Guidelines

        - Create a concise, descriptive name that captures the essence of the classification task
        - Use clear, professional language that would be appropriate for a production model
        - Avoid overly technical jargon unless it's domain-specific
        - Keep the name under 50 characters when possible
        - Make it memorable and easy to understand

        # Example Generation Guidelines

        - Create diverse examples that cover different aspects of each label
        - Ensure examples are realistic and representative of real-world usage
        - Vary sentence structure, vocabulary, and complexity
        - Include edge cases and ambiguous examples when appropriate
        - Make sure examples are clearly labeled (high confidence)
        - Avoid examples that could belong to multiple labels
        - Consider the domain-specific language and context
        - Use the initial examples provided to guide the generation of new examples
        - Please note that we use the terms "label" and "label name" interchangeably.

        # Quality Standards

        - All examples should be clearly classifiable into exactly one label
        - Examples should be realistic and representative
        - Avoid overly simplistic or artificial examples
        - Ensure good coverage across all labels
        - Consider the practical use case described in the model description
        - Make sure the list of "generated_examples" is not empty and has at least {input.num_examples_per_label} examples for each label
        - Each generated example should have a clear text and label
    """,
    prompt_template=lambda input: (
        f"""
        Generate high-quality training examples for the following classification task:

        **Model Description**: {input.model_description}
        **Label names**: {", ".join(input.label_names)}
        **Number of examples per label**: {input.num_examples_per_label}

        """
        + (
            f"**Initial Examples provided**: {len(input.initial_examples)} examples"
            if input.initial_examples
            else "**No initial examples provided**"
        )
        + "\n\n"
        + (
            "**Initial Examples**:\n"
            + "\n".join([f"- '{ex.text}' → {ex.label_name}" for ex in input.initial_examples[:100]])
            if input.initial_examples
            else ""
        )
        + f"""

        Please provide:

        **Model Name**: A concise, descriptive name for this classification model that captures the essence of the task.

        **Generated Examples**: {input.num_examples_per_label} high-quality examples for each of the {len(input.label_names)} label names. This list should not be empty and should
        extend the list of initial examples, if any were provided. The examples should have a clear text value and label name.

        Focus on creating diverse, realistic examples that will work well for the described classification task.
        Ensure the examples are clearly labeled and representative of real-world usage.

        Do not return an empty set of examples! Make sure to generate {input.num_examples_per_label} examples for each label. Each example should have a clear text value and label.
        """
    ),
)


async def bootstrap_classification_model(
    model_description: str,
    label_names: list[str],
    initial_examples: list[LabeledExample] = [],
    num_examples_per_label: int = 10,
) -> BootstrapClassificationModelResult:
    """
    Generate a complete memoryset and classification model configuration

    Args:
        model_description: Description of what the model should classify
        label_names: List of possible label names/classes
        initial_examples: Optional initial examples to help guide memory generation
        num_examples_per_label: Number of memories to generate per label

    Returns:
        Complete configuration for memoryset and model
    """
    input_data = BootstrapClassificationModelInput(
        model_description=model_description,
        label_names=label_names,
        initial_examples=initial_examples,
        num_examples_per_label=num_examples_per_label,
    )

    result = await bootstrap_classification_model_agent.run(input_data)

    result.output.model_description = model_description
    result.output.label_names = label_names

    return result.output
