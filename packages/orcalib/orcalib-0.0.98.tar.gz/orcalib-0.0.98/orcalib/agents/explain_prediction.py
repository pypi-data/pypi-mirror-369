from pydantic import BaseModel

from ..models import LabelPredictionWithMemories
from .agent_workflow import AgentWorkflow


class ExplainPredictionContext(BaseModel):
    model_description: str
    lookup_score_median: float
    lookup_score_std: float
    label_names: list[str]


explain_prediction_agent = AgentWorkflow(
    "anthropic:claude-3-7-sonnet-latest",
    deps_type=ExplainPredictionContext,
    input_type=LabelPredictionWithMemories,
    system_prompt=lambda deps: f"""
        # Task

        Your job is to explain prediction outcomes of a retrieval augmented classification model
        in a concise manner. Assume the user is a domain expert in the task the model is trying to
        solve but does not have access to the model's internal workings or extensive knowledge
        about machine learning or data science.

        # Model Mechanism

        The predictions of the model are based on the labels of a set of similar memories that were
        retrieved for the input. The influence of each memory to the prediction is determined by the
        similarity of the memory to the input.

        # Model Purpose

        This particular model is a classification for {deps.model_description}. It classifies
        inputs into the following labels: {", ".join(deps.label_names)}.

        The overall average lookup score of the memories is: {deps.lookup_score_median:.0%} ± {deps.lookup_score_std:.0%}.

        # Possible Failure Modes

        Consider the following failure modes when explaining the predictions:

        - **Uncertain Expected Label:** The input is so ambiguous that the expected label might as
          well be the opposite, for example because of sarcasm or rhetorical questions.
        - **Ambiguous Memories:** While there are similar memories, they all are ambiguous in terms
          of the label that is being expressed.
        - **Irrelevant Similarity:** The input and memories are similar in ways that are not related
          to the label classification task. For example the memories are all in a foreign language
          or are all about the same topic.
        - **No Relevant Memories:** The average similarity of the memories is too low. This might
          happen if the input uses special language that is not found in the memories.
        - **Too Many Memories:** There are a few very similar memories with the expected label, but
          their signal is drowned out by a lot of irrelevant memories with the wrong label.

        # Possible Improvements

        * If the model finds highly similar memories but those are not relevant to the label
          classification task, finetuning the embedding model might help.
        * If the model cannot find memories that match the input well enough to make a correct
          prediction, adding additional memories similar to the input might help.
        * If the influence of some memories that match the input well is drowned out by a lot of
          irrelevant memories that are all very similar to each other, removing the most similar
          memories by running an analysis to identify near duplicate memories and removing them
          might help.
        * If the model finds memories that are very ambiguous or which have labels that seem wrong,
          running an analysis to detect mislabeled memories and fixing them might help.

        # Output Format

        * Do not explain the mechanism of the model, but instead analyze what went wrong with the
          retrieved memories.
        * Do not try to enumerate exactly which memories had what effect unless one or two stand out
          because they carried a lot of weight.
        * Consider how the average similarity of the memories compares to overall average similarity
          of the model and mention it if relevant.
        * Call it out if the expected label does not really make sense for the input and the model
          had no reasonable chance to make a correct prediction.
        * Keep your explanation to a single concise paragraph, no more than 3 short sentences.
        * Do not use headings or any other markdown formatting.
        * Consider whether the similarity between the input and the memories is relevant to the
          prediction or how high similarities may be artifacts of a flawed retrieval process.
        * Do not state the obvious like the prediction is wrong because the labels of most memories
          are wrong, instead focus on the semantics and linguistic nuances.
        * Suggest a possible way to improve the model based on the failure mode and possible
          solutions suggested above, if applicable.
    """,
    prompt_template=lambda prediction: f"""
        Explain why the model made the following prediction for the given input based on the
        following memories.

        Input:
        {prediction.input_value}

        Expected Label: {prediction.expected_label_name}
        Predicted Label: {prediction.label_name}

        Prediction Confidence: {prediction.confidence:.0%}
        Average Memory Similarity: {sum(m.lookup_score for m in prediction.memories) / len(prediction.memories):.0%}

        <memories>{"---".join([f"""
        Memory {i + 1}:
            Label: {memory.label_name}
            Influence: {memory.attention_weight / sum(m.attention_weight for m in prediction.memories):.0%}
            Similarity: {memory.lookup_score:.0%}
            Text: "{memory.value}"
        """
            for i, memory in enumerate(prediction.memories)]
        )}</memories>

        Focus on the semantics of the input and the memories.
    """,
)
