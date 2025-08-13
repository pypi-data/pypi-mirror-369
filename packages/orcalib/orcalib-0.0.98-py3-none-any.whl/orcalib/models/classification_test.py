import os
from datetime import datetime
from uuid import UUID

import numpy as np
import torch

from ..utils import is_using_blob_storage, list_dir
from .classification import (
    ClassificationMetrics,
    MemoryAugmentedTrainingArguments,
    MemoryMixtureOfExpertsClassificationHead,
    NearestMemoriesClassificationHead,
    RACModel,
)
from .prediction_types import LabeledMemoryLookup, LabelPredictionWithMemories


def test_initialize_model(memoryset):
    # When a model is initialized with a memoryset
    model = RACModel(memoryset=memoryset, head_type="MMOE")
    # Then the model is initialized without errors
    assert model is not None
    # And the memoryset is attached to the model
    assert model.memoryset is memoryset
    # And it has the correct head
    assert isinstance(model.head, MemoryMixtureOfExpertsClassificationHead)
    # And a reasonable memory lookup count is inferred
    assert model.memory_lookup_count == 9
    # And the number of classes is inferred from the memoryset
    assert model.num_classes == 2
    # And the forward method returns a valid output
    batch_size = 2
    memories_labels = torch.tensor([[1] * 9, [0] * 9])
    assert memories_labels.shape == (batch_size, model.memory_lookup_count)
    input_embeddings = torch.rand(batch_size, model.memoryset.embedding_model.embedding_dim)
    memories_embeddings = torch.rand(
        batch_size, model.memory_lookup_count, model.memoryset.embedding_model.embedding_dim
    )
    expected_labels = torch.tensor([1, 0])
    assert expected_labels.shape == (batch_size,)
    output = model(
        input_embeddings=input_embeddings,
        memories_labels=memories_labels,
        memories_embeddings=memories_embeddings,
        memories_weights=None,
        labels=expected_labels,
    )
    assert output is not None
    assert output.loss is not None
    assert output.logits is not None
    assert output.logits.shape == (batch_size, model.num_classes)
    assert (output.logits.argmax(dim=-1) == expected_labels).all()


def test_save_and_load_model(location, memoryset):
    # Given a RAC model
    model = RACModel(memoryset=memoryset, head_type="KNN", weigh_memories=True)
    # When the model is saved
    model.save_pretrained(location)
    # Then the remote bucket should contain the model files
    if is_using_blob_storage(location):
        model_files = list_dir(location)
        assert len(model_files) > 0
        assert f"{location}/config.json" in model_files
    else:
        model_files = os.listdir(location)
        assert len(model_files) > 0
        assert "config.json" in model_files
    # When the model is loaded back up
    reloaded_model = RACModel.from_pretrained(location)
    # Then the model is loaded without errors
    assert reloaded_model is not None
    # And the memoryset is correctly attached
    assert reloaded_model.memoryset.uri == memoryset.uri
    assert len(reloaded_model.memoryset) == len(memoryset)
    # And the config is loaded correctly
    assert isinstance(reloaded_model.head, NearestMemoriesClassificationHead)
    assert reloaded_model.config.weigh_memories is True


def test_evaluate(memoryset, dataset_dict):
    # Given a RAC model
    model = RACModel(memoryset=memoryset, head_type="KNN", min_memory_weight=0.5)
    # And a progress callback
    progress_calls = []
    progress_callback = lambda step, total: progress_calls.append((step, total))  # noqa: E731
    # When the model is evaluated
    result = model.evaluate(
        dataset_dict["test"].rename_column("label", "category"),
        value_column="text",
        label_column="category",
        on_progress=progress_callback,
        batch_size=len(dataset_dict["test"]) // 2,
    )

    # Then a result is returned
    assert isinstance(result, ClassificationMetrics)
    # And the result contains all the metrics
    assert result.accuracy > 0.7
    assert result.f1_score > 0.7
    assert isinstance(result.loss, float)
    assert result.roc_auc is not None
    assert result.pr_auc is not None
    assert result.roc_auc > 0.7
    assert result.pr_auc > 0.7
    assert result.pr_curve is not None
    assert len(result.pr_curve["precisions"]) == len(result.pr_curve["recalls"])
    assert len(result.pr_curve["precisions"]) == len(result.pr_curve["thresholds"])
    assert result.roc_curve is not None
    assert len(result.roc_curve["false_positive_rates"]) == len(result.roc_curve["true_positive_rates"])
    assert len(result.roc_curve["false_positive_rates"]) == len(result.roc_curve["thresholds"])

    # And the progress callback is called
    assert len(progress_calls) == 3
    assert progress_calls[0] == (0, len(dataset_dict["test"]))
    assert progress_calls[1] == (len(dataset_dict["test"]) // 2, len(dataset_dict["test"]))
    assert progress_calls[2] == (len(dataset_dict["test"]), len(dataset_dict["test"]))

    # And anomaly score statistics are present and valid
    assert isinstance(result.anomaly_score_mean, float)
    assert isinstance(result.anomaly_score_median, float)
    assert isinstance(result.anomaly_score_variance, float)
    assert -1.0 <= result.anomaly_score_mean <= 1.0
    assert -1.0 <= result.anomaly_score_median <= 1.0
    assert -1.0 <= result.anomaly_score_variance <= 1.0


def test_finetune(location_or_none, memoryset, dataset_dict):
    # Given a RAC model
    model = RACModel(memoryset=memoryset, head_type="FF")
    # And a progress callback
    progress_calls = []
    progress_callback = lambda step, total: progress_calls.append((step, total))  # noqa: E731
    # And a log callback
    logs = []
    log_callback = lambda log: logs.append(log)  # noqa: E731
    # When the model is finetuned
    pre_finetune_metrics = model.evaluate(dataset_dict["train"], value_column="text")
    model.finetune(
        location_or_none,
        train_dataset=dataset_dict["train"],
        eval_dataset=dataset_dict["test"],
        value_column="text",
        on_log=log_callback,
        training_args=MemoryAugmentedTrainingArguments(
            max_steps=4,
            warmup_steps=0,
            eval_strategy="steps",
            eval_steps=4,
            logging_steps=1,
            per_device_train_batch_size=16,
        ),
        on_progress=progress_callback,
    )
    # Then the model is fit to the training data
    post_finetune_metrics = model.evaluate(dataset_dict["train"], value_column="text")
    assert post_finetune_metrics.loss < pre_finetune_metrics.loss
    assert post_finetune_metrics.accuracy > pre_finetune_metrics.accuracy
    # And the progress callback is called
    assert len(progress_calls) == 4 + 1
    for i in range(4 + 1):
        assert progress_calls[i] == (i, 4)
    # And the log callback is called
    assert len(logs) >= 4
    for log in logs[:4]:
        assert "epoch" in log
        assert isinstance(log["epoch"], float)
        assert "loss" in log
        assert isinstance(log["loss"], float)
        assert "grad_norm" in log
        assert isinstance(log["grad_norm"], float)
        assert "learning_rate" in log
        assert isinstance(log["learning_rate"], float)
    # And training checkpoints are saved
    if location_or_none is not None:
        files_at_location = list_dir(location_or_none)
        assert len(files_at_location) > 0
        assert any("checkpoint" in f for f in files_at_location)


def test_predict(memoryset, dataset_dict, label_names):
    # Given a RAC model
    model = RACModel(memoryset=memoryset)
    # When predict is called with a single text
    prediction = model.predict(dataset_dict["test"]["text"][0], expected_label=dataset_dict["test"]["label"][0])
    # Then a single prediction is returned
    assert prediction is not None
    assert isinstance(prediction, LabelPredictionWithMemories)
    # And the prediction contains a label
    assert prediction.label in [0, 1]
    # And the label name is resolved
    assert prediction.label_name in label_names
    # And the prediction contains a confidence
    assert 0 <= prediction.confidence <= 1
    # And the prediction contains an anomaly score
    assert prediction.anomaly_score is not None
    # And the logits are a numpy array
    assert isinstance(prediction.logits, np.ndarray)
    assert prediction.logits.shape == (model.num_classes,)
    assert prediction.logits.dtype == np.float32
    # And the input embedding is a numpy array
    assert isinstance(prediction.input_embedding, np.ndarray)
    assert prediction.input_embedding.shape == (model.memoryset.embedding_model.embedding_dim,)
    assert prediction.input_embedding.dtype == np.float32
    # And a prediction id is returned
    prediction_id = prediction.prediction_id
    assert isinstance(prediction_id, UUID)
    # And a timestamp is returned
    assert isinstance(prediction.timestamp, datetime)
    # And the memory lookups
    assert isinstance(prediction.memories, list)
    assert len(prediction.memories) == model.memory_lookup_count
    assert isinstance(prediction.memories[0], LabeledMemoryLookup)
    # And the memory lookups contain the attention weights
    assert prediction.memories[0].attention_weight is not None
    assert isinstance(prediction.memories[0].attention_weight, float)
    # And the memory lookups contain the prediction id
    assert prediction.memories[0].prediction_id == prediction_id
    # And an expected label is returned
    assert prediction.expected_label is not None
    assert prediction.expected_label == dataset_dict["test"]["label"][0]
    # And the prediction is correct
    assert prediction.label == prediction.expected_label


def test_predict_batch(memoryset, dataset_dict):
    # Given a RAC model
    model = RACModel(memoryset=memoryset)
    # When predict is called with a batch of texts
    predictions = model.predict(dataset_dict["test"]["text"][:2])
    # Then a list of predictions is returned
    assert isinstance(predictions, list)
    assert len(predictions) == 2
    # And each prediction is of the correct type
    assert all(isinstance(prediction, LabelPredictionWithMemories) for prediction in predictions)
    # And the prediction results contain memories
    assert all(isinstance(prediction.memories[0], LabeledMemoryLookup) for prediction in predictions)
