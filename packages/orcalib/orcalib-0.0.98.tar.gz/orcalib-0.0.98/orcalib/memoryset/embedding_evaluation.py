# TODO: decouple this from memoryset and move it to embeddings submodule

import logging
import re
from datetime import datetime

from datasets import Dataset
from pydantic import BaseModel
from tqdm.auto import tqdm

from ..embedding import (
    EmbeddingModel,
    FinetunedEmbeddingModelName,
    PretrainedEmbeddingModelName,
)
from ..utils import OnProgressCallback, remove_duplicates, safely_call_on_progress
from ..utils.dataset import parse_dataset
from .memoryset import LabeledMemoryset
from .memoryset_analyzer import AnalyzeNeighborLabelsResult, LabeledMemorysetAnalyzer


class EmbeddingEvaluationResult(BaseModel):
    class EmbeddingModelResult(BaseModel):
        embedding_model_name: str
        """The name of the embedding model"""
        embedding_model_path: str
        """The path of the embedding model"""
        analysis_result: AnalyzeNeighborLabelsResult
        """The analysis result for the embedding model"""
        memoryset_name: str | None = None
        """The name of the memoryset"""
        is_finetuned: bool = False
        """Whether this is a finetuned embedding model"""

    evaluation_results: list[EmbeddingModelResult]
    """The evaluation results for each embedding model"""

    def sort_by_neighbor_prediction_accuracy(self) -> None:
        """Sort the evaluation results by neighbor prediction accuracy"""
        self.evaluation_results.sort(key=lambda x: x.analysis_result.neighbor_prediction_accuracy, reverse=True)


class EmbeddingEvaluation:
    DEFAULT_EMBEDDING_MODELS: list[PretrainedEmbeddingModelName | FinetunedEmbeddingModelName] = [
        PretrainedEmbeddingModelName.GTE_BASE,
        PretrainedEmbeddingModelName.CDE_SMALL,
    ]

    @staticmethod
    def run(
        dataset: Dataset,
        *,
        run_name: str | None,
        value_column: str = "value",
        label_column: str = "label",
        source_id_column: str | None = None,
        neighbor_count: int = 5,
        drop_memorysets: bool = True,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
        label_names: list[str] | None = None,
        embedding_models: (
            list[PretrainedEmbeddingModelName | FinetunedEmbeddingModelName] | None
        ) = DEFAULT_EMBEDDING_MODELS,
    ) -> EmbeddingEvaluationResult:
        """
        Run embedding evaluation on a dataset with both pretrained and finetuned models.

        Params:
            dataset: Dataset to evaluate models on
            run_name: Name for this evaluation run, auto-generated if None
            value_column: Name of the column containing text values
            label_column: Name of the column containing labels
            source_id_column: Name of the column containing source IDs (optional)
            neighbor_count: Number of neighbors to analyze for each sample
            drop_memorysets: Whether to drop memorysets after evaluation to save memory
            show_progress_bar: Whether to show progress bars
            on_progress: Callback for progress updates
            label_names: Optional list of label names
            embedding_models: List of embedding models to evaluate

        Returns:
            Results of the embedding evaluation
        """
        if run_name is None:
            run_name = f"embedding_evaluation_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"

        step = 0
        n = len(embedding_models or []) + 1

        safely_call_on_progress(on_progress, step, n)
        step += 1

        if value_column not in dataset.column_names:
            raise ValueError(f"Value column {value_column} not found in dataset")
        if label_column not in dataset.column_names:
            raise ValueError(f"Label column {label_column} not found in dataset")
        if source_id_column and source_id_column not in dataset.column_names:
            raise ValueError(f"Source ID column {source_id_column} not found in dataset")

        # TODO: make sampling configurable
        logging.info("Removing duplicates from dataset...")
        processed_dataset = remove_duplicates(dataset, value_column)

        # Only sample if we have more than 1000 rows AND more than the sample size
        sample_size = None if processed_dataset.num_rows <= 1000 else 1000
        logging.info(f"Subsampling dataset to {sample_size} samples...")
        processed_dataset = parse_dataset(
            processed_dataset, value_column=value_column, label_column=label_column, sample=sample_size
        )

        evaluation_results = []

        def evaluate_model(
            model_name: str,
            model_path: str,
            is_finetuned: bool,
            progress_step: int,
        ) -> tuple[EmbeddingEvaluationResult.EmbeddingModelResult, int]:
            safely_call_on_progress(on_progress, progress_step, n)
            progress_step += 1

            memoryset_name = _sanitize_collection_name(f"{run_name}_{model_name}")
            LabeledMemoryset.drop(memoryset_name)

            model_type = "finetuned model" if is_finetuned else "model"
            logging.info(f"Creating memoryset {memoryset_name} for {model_type} {model_name}...")
            memoryset = LabeledMemoryset(
                memoryset_name, embedding_model=EmbeddingModel(model_path), label_names=label_names
            )
            memoryset.insert(
                processed_dataset, value_column="value", label_column="label", source_id_column=source_id_column
            )

            analyzer = LabeledMemorysetAnalyzer(memoryset, neighbor_count=neighbor_count)
            if len(memoryset) == 0:
                raise ValueError(
                    f"Cannot run embedding selection for {model_type} {model_name} because the memoryset is empty"
                )

            logging.info(f"Analyzing neighbor labels for {model_type} {model_name}...")
            analysis_result = analyzer.analyze_neighbor_labels()

            if drop_memorysets:
                logging.info(f"Dropping memoryset {memoryset_name}...")
                LabeledMemoryset.drop(memoryset_name)
                memoryset_name = None

            result = EmbeddingEvaluationResult.EmbeddingModelResult(
                embedding_model_name=model_name,
                embedding_model_path=model_path,
                analysis_result=analysis_result,
                memoryset_name=memoryset_name,
                is_finetuned=is_finetuned,
            )
            return result, progress_step

        # Evaluate pretrained models
        if embedding_models:
            for model_name in tqdm(embedding_models, disable=not show_progress_bar):
                result, step = evaluate_model(
                    model_name=model_name.value,
                    model_path=model_name.path,
                    is_finetuned=model_name.finetuned,
                    progress_step=step,
                )
                evaluation_results.append(result)

        safely_call_on_progress(on_progress, n, n)

        result = EmbeddingEvaluationResult(evaluation_results=evaluation_results)
        result.sort_by_neighbor_prediction_accuracy()
        return result


def _sanitize_collection_name(name: str) -> str:
    """
    Sanitize a string to be valid as a collection name.
    Collection names can only contain letters, numbers, and underscores.
    Any other characters will be replaced with underscores.
    """
    # Replace any character that is not a letter, number or underscore with an underscore
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)
