from pydantic import BaseModel

from .agent_workflow import AgentWorkflow


class ClassRepresentatives(BaseModel):
    """Representatives for a single class."""

    label: int
    label_name: str | None
    representative_values: list[str]


class DescribeClassPatternsContext(BaseModel):
    """Context for describing class patterns analysis. This provides the agent with information about what the dataset/memoryset represents to help generate more accurate pattern descriptions."""

    memoryset_description: str = "data classification"
    """Description of what the memoryset is about (e.g., 'sentiment analysis of product reviews')"""


class ClassPatternsInput(BaseModel):
    """Input containing all class representatives for pattern analysis."""

    class_representatives: list[ClassRepresentatives]


class ClassPattern(BaseModel):
    """An explanation of similarities between memories in a single class."""

    label: int
    name: str
    description: str


class ClassPatternsDescription(BaseModel):
    """Result of the class patterns analysis."""

    overview: str
    classes: list[ClassPattern]
    summary: str


def system_prompt(deps: DescribeClassPatternsContext) -> str:
    return f"""
        You are an expert data analyst specialized in understanding patterns within classified data.

        Dataset description: {deps.memoryset_description}

        Your task is to analyze representative examples from different classes in a
        dataset and provide a clear, insightful description of what distinguishes each class from the others.

        Focus on:
        - Key linguistic, semantic, or stylistic differences between classes
        - Common themes or patterns within each class
        - What makes the classification boundaries meaningful

        Provide a concise but comprehensive overview that would help someone understand the
        nature of the classification task and what separates the different categories.
    """


def prompt_template(input_data: ClassPatternsInput) -> str:
    class_sections = []
    for class_rep in input_data.class_representatives:
        class_name = class_rep.label_name or f"Class {class_rep.label}"
        examples = "\n".join([f"  - {value}" for value in class_rep.representative_values])

        class_sections.append(
            f"""
**{class_name}** (Label {class_rep.label}):
{examples}
        """.strip()
        )

    return f"""
        Analyze the following representative examples from each class and describe the key patterns that distinguish these classes from each other:

        {chr(10).join(class_sections)}
        """


describe_class_patterns_agent = AgentWorkflow(
    "anthropic:claude-3-7-sonnet-latest",
    deps_type=DescribeClassPatternsContext,
    input_type=ClassPatternsInput,
    result_type=ClassPatternsDescription,
    system_prompt=system_prompt,
    prompt_template=prompt_template,
)
