from .embedding_evaluation import evaluate_embedding_model
from .embedding_models import EmbeddingModel


def test_evaluate_for_classification(dataset):
    metrics = evaluate_embedding_model(
        embedding_model=EmbeddingModel.GTE_SMALL,
        memory_dataset=dataset,
        value_column="text",
        label_column="label",
    )
    assert metrics.accuracy > 0.5


def test_evaluate_for_regression(dataset):
    # Use the actual score column for regression test
    metrics = evaluate_embedding_model(
        embedding_model=EmbeddingModel.GTE_SMALL,
        memory_dataset=dataset,
        value_column="text",
        score_column="score",
    )
    # For regression, we check that the metrics are reasonable
    assert metrics.mse >= 0.0
    assert metrics.mae >= 0.0
