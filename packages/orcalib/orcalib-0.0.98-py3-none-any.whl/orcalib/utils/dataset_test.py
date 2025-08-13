import base64
from io import BytesIO

import pytest
from datasets import Array2D, ClassLabel, Dataset, DatasetDict, Image, Value
from PIL import Image as pil

from .dataset import (
    _PARSED_BUILDER_NAME_SUFFIX,
    is_parsed,
    parse_dataset,
    parse_dataset_schema,
    parse_label_names,
    reduce_dataset,
    remove_duplicates,
)
from .pydantic import ColumnInfo, ColumnType


def test_parse_dataset_with_text():
    dataset = Dataset.from_dict({"text": ["hello", "world"]})
    parsed = parse_dataset(dataset, value_column="text")
    assert "value" in parsed.features
    assert parsed.features["value"].dtype == "string"
    assert len(parsed) == 2
    assert len(parsed.features) == 1


def test_parse_dataset_with_pil_image():
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg=="
    bytes_image: bytes = base64.b64decode(base64_image)
    pil_image: pil.Image = pil.open(BytesIO(bytes_image))
    dataset = Dataset.from_list([{"image": pil_image}])
    parsed = parse_dataset(dataset, value_column="image")
    assert "value" in parsed.features
    assert isinstance(parsed.features["value"], Image)
    assert parsed[0]["value"] == pil_image
    assert len(parsed.features) == 1


def test_parse_dataset_with_bytes_image():
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg=="
    bytes_image: bytes = base64.b64decode(base64_image)
    pil_image: pil.Image = pil.open(BytesIO(bytes_image))
    dataset = Dataset.from_list([{"image": {"bytes": bytes_image}}]).cast_column("image", Image(decode=False))
    parsed = parse_dataset(dataset, value_column="image")
    assert "value" in parsed.features
    assert isinstance(parsed.features["value"], Image)
    assert parsed[0]["value"] == pil_image
    assert len(parsed.features) == 1


def test_parse_dataset_with_2d_timeseries():
    dataset = Dataset.from_list([{"timeseries": [[1, 2.0, 3], [4, 5.0, 6]]}])
    parsed = parse_dataset(dataset, value_column="timeseries")
    assert "value" in parsed.features
    assert isinstance(parsed.features["value"], Array2D)
    assert parsed["value"][0].shape == (2, 3)
    assert parsed["value"][0].dtype == "float32"


def test_parse_dataset_with_1d_timeseries():
    dataset = Dataset.from_list([{"timeseries": [1.0, 2.0, 3.0]}, {"timeseries": [4.0, 5.0, 6.0, 7.0]}])
    parsed = parse_dataset(dataset, value_column="timeseries")
    assert "value" in parsed.features
    assert isinstance(parsed.features["value"], Array2D)
    assert parsed["value"][0].shape == (3, 1)
    assert parsed["value"][0].dtype == "float32"


def test_parse_dataset_missing_value_column():
    dataset = Dataset.from_dict({"other": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text")


def test_parse_dataset_wrong_value_column_type():
    dataset = Dataset.from_dict({"value": [1, 2]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="value")


def test_parse_dataset_incongruent_timeseries_shape():
    dataset = Dataset.from_list([{"timeseries": [[1], [2], [3]]}, {"timeseries": [[4, 4], [5, 5], [6, 6]]}])
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="timeseries")


def test_parse_dataset_invalid_timeseries_dtype():
    dataset = Dataset.from_list([{"timeseries": [["a", "b", "c"], ["d", "e", "f"]]}])
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="timeseries")


def test_parse_dataset_invalid_timeseries_sequence():
    dataset = Dataset.from_list([{"timeseries": {"a": 1, "b": 2, "c": 3}}])
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="timeseries")


def test_parse_dataset_with_int_label():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": [0, 1]})
    parsed = parse_dataset(dataset, value_column="text", label_column="label")
    assert "label" in parsed.features
    assert isinstance(parsed.features["label"], ClassLabel)
    assert parsed.features["label"].names == ["0", "1"]
    assert len(parsed) == 2
    assert len(parsed.features) == 2
    assert parsed["label"] == [0, 1]


def test_parse_dataset_with_int_label_and_label_names():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": [0, 1]})
    parsed = parse_dataset(dataset, value_column="text", label_column="label", label_names=["neg", "pos"])
    assert len(parsed) == 2
    assert parsed.features["label"].names == ["neg", "pos"]
    assert parsed["label"] == [0, 1]


def test_parse_dataset_with_int_label_and_num_classes():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": [0, 1]})
    parsed = parse_dataset(dataset, value_column="text", label_column="label", num_classes=3)
    assert len(parsed) == 2
    assert parsed.features["label"].num_classes == 3
    assert parsed.features["label"].names == ["0", "1", "2"]
    assert parsed["label"] == [0, 1]


def test_parse_dataset_with_class_label():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": ["pos", "neg"]}).cast_column(
        "label", ClassLabel(num_classes=2, names=["neg", "pos"])
    )
    parsed = parse_dataset(dataset, value_column="text", label_column="label")
    assert "label" in parsed.features
    assert isinstance(parsed.features["label"], ClassLabel)
    assert parsed.features["label"].names == ["neg", "pos"]
    assert len(parsed) == 2
    assert len(parsed.features) == 2
    assert parsed[0]["label"] == 1
    assert parsed[1]["label"] == 0


def test_parse_dataset_missing_label_column():
    dataset = Dataset.from_dict({"text": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", label_column="label")


def test_parse_dataset_wrong_label_column_type():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": ["pos", "neg"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", label_column="label")


def test_parse_dataset_with_float_score():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "score": [0.5, 1.0]})
    parsed = parse_dataset(dataset, value_column="text", score_column="score")
    assert "score" in parsed.features
    assert isinstance(parsed.features["score"], Value)
    assert parsed.features["score"].dtype in ("float32", "float64")
    assert len(parsed) == 2
    assert len(parsed.features) == 2


def test_parse_dataset_missing_score_column():
    dataset = Dataset.from_dict({"text": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", score_column="score")


def test_parse_dataset_wrong_score_column_type():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "score": ["high", "low"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", score_column="score")


def test_parse_dataset_with_string_source_id():
    dataset = Dataset.from_dict({"value": ["hello", "world"], "label": [0, 1], "source_id": ["a:1", "b:2"]})
    parsed = parse_dataset(dataset, value_column="value", label_column="label", source_id_column="source_id")
    assert "source_id" in parsed.features
    assert parsed.features["source_id"].dtype == "string"
    assert len(parsed) == 2
    assert len(parsed.features) == 3


def test_parse_dataset_with_missing_source_id_column():
    dataset = Dataset.from_dict({"value": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="value", source_id_column="source_id")


def test_parse_dataset_with_wrong_source_id_column_type():
    dataset = Dataset.from_dict({"value": ["hello", "world"], "source_id": [1, 2]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="value", source_id_column="source_id")


def test_parse_dataset_with_other_columns_as_metadata():
    dataset = Dataset.from_dict(
        {
            "value": ["hello", "world"],
            "label": [0, 1],
            "score": [1.5, 2.5],
            "source_id": ["a:1", "b:2"],
            "metadata": ["some", "context"],
        }
    )
    parsed = parse_dataset(
        dataset,
        value_column="value",
        label_column="label",
        other_columns_as_metadata=True,
    )
    assert "metadata" in parsed.features
    assert len(parsed) == 2
    assert len(parsed.features) == 3
    assert parsed[0]["metadata"] == {"score": 1.5, "metadata": "some", "source_id": "a:1"}
    assert parsed[1]["metadata"] == {"score": 2.5, "metadata": "context", "source_id": "b:2"}


def test_parse_dataset_with_other_columns_as_metadata_and_invalid_types():
    dataset = Dataset.from_dict(
        {
            "value": ["hello", "world"],
            "label": [0, 1],
            "source_id": ["a:1", "b:2"],
            "invalid_metadata": [[1.5], [2.5]],
            "metadata": ["some", "context"],
        }
    )
    parsed = parse_dataset(
        dataset,
        value_column="value",
        label_column="label",
        other_columns_as_metadata=True,
    )
    assert "metadata" in parsed.features
    assert len(parsed) == 2
    assert len(parsed.features) == 3
    assert parsed[0]["metadata"] == {"metadata": "some", "source_id": "a:1"}
    assert parsed[1]["metadata"] == {"metadata": "context", "source_id": "b:2"}


def test_parse_dataset_with_source_id_and_other_columns_as_metadata():
    dataset = Dataset.from_dict(
        {
            "value": ["hello", "world"],
            "label": [0, 1],
            "score": [0.5, 1.0],
            "source_id": ["a:1", "b:2"],
            "other": [1.5, 2.5],
        }
    )
    parsed = parse_dataset(
        dataset,
        value_column="value",
        label_column="label",
        score_column="score",
        other_columns_as_metadata=True,
        source_id_column="source_id",
    )
    assert "metadata" in parsed.features
    assert len(parsed) == 2
    assert len(parsed.features) == 5
    assert "source_id" in parsed.features
    assert parsed[0]["metadata"] == {"other": 1.5}
    assert parsed[1]["metadata"] == {"other": 2.5}


def test_parse_dataset_with_percentage_sampling():
    dataset = Dataset.from_dict({"text": ["hello", "world", "foo", "bar"]})
    parsed = parse_dataset(dataset, value_column="text", sample=3)
    assert len(parsed) == 3


def test_parse_dataset_with_stratified_sampling():
    dataset = Dataset.from_dict({"text": ["hello", "world", "foo", "bar"], "label": [0, 1, 0, 1]})
    parsed = parse_dataset(dataset, value_column="text", label_column="label", sample=0.5)
    assert len(parsed) == 2
    assert parsed[0]["label"] == 0
    assert parsed[1]["label"] == 1


def test_parse_dataset_marks_dataset_as_parsed():
    dataset = Dataset.from_dict({"text": ["hello", "world"]})
    parsed = parse_dataset(dataset, value_column="text")
    assert is_parsed(parsed)


def test_parse_dataset_skipped_if_already_parsed():
    dataset = Dataset.from_dict({"would_change": ["hello", "world"]})
    dataset.info.builder_name = "forcefully_marked_as_parsed" + _PARSED_BUILDER_NAME_SUFFIX
    parsed = parse_dataset(dataset, value_column="would_change")
    assert is_parsed(parsed)
    assert parsed["would_change"] == ["hello", "world"]


def test_parse_label_names_from_class_label():
    dataset = Dataset.from_dict({"label": [0, 1]}).cast_column("label", ClassLabel(num_classes=2, names=["neg", "pos"]))
    assert parse_label_names(dataset, label_column="label") == ["neg", "pos"]


def test_parse_label_names_from_int_label():
    dataset = Dataset.from_dict({"label": [0, 1]})
    assert parse_label_names(dataset, label_column="label") is None


def test_parse_label_names_from_string_label():
    dataset = Dataset.from_dict({"label": ["neg", "pos"]})
    assert parse_label_names(dataset, label_column="label") is None


def test_parse_dataset_schema():
    dataset = Dataset.from_dict(
        {
            "text": ["hello", "world"],
            "score": [0.5, 1.0],
            "label": [0, 1],
            "list": [[1, 2], [3, 4]],
            "metadata": [{"a": 1, "b": 2}, {"a": 3, "b": 4}],
            "image": [
                pil.new("RGB", (100, 100), color=(255, 0, 0)),
                pil.new("RGB", (100, 100), color=(0, 255, 0)),
            ],
        }
    )
    dataset = dataset.cast_column("label", ClassLabel(num_classes=2, names=["neg", "pos"]))
    columns = parse_dataset_schema(dataset)
    assert columns == [
        ColumnInfo(name="text", type=ColumnType.STRING),
        ColumnInfo(name="score", type=ColumnType.FLOAT),
        ColumnInfo(name="label", type=ColumnType.ENUM, enum_options=["neg", "pos"]),
        ColumnInfo(name="list", type=ColumnType.OTHER),
        ColumnInfo(name="metadata", type=ColumnType.OTHER),
        ColumnInfo(name="image", type=ColumnType.IMAGE),
    ]


def test_parse_dataset_schema_with_int_column():
    """Test that int_values field is populated correctly for INT columns"""
    dataset = Dataset.from_dict(
        {
            "text": ["hello", "world", "test"],
            "int_label": [2, 0, 1],
        }
    )
    columns = parse_dataset_schema(dataset)
    assert len(columns) == 2

    # Text column should have no int_values
    text_column = next(col for col in columns if col.name == "text")
    assert text_column.type == ColumnType.STRING
    assert text_column.int_values is None

    # Int column should have sorted distinct values
    int_column = next(col for col in columns if col.name == "int_label")
    assert int_column.type == ColumnType.INT
    assert int_column.int_values == [0, 1, 2]  # Should be sorted


def test_remove_duplicates():
    dataset = Dataset.from_dict({"text": ["hello", "world", "hello", "world"], "label": [0, 0, 1, 1]})
    dataset = remove_duplicates(dataset, "text")
    assert len(dataset) == 2
    assert dataset["text"] == ["hello", "world"]
    assert dataset["label"] == [0, 0]


def test_remove_duplicate_images():
    dataset = Dataset.from_dict(
        {
            "image": [
                pil.new("RGB", (100, 100), color=(255, 0, 0)),
                pil.new("RGB", (100, 100), color=(0, 255, 0)),
                pil.new("RGB", (100, 100), color=(255, 0, 0)),
                pil.new("RGB", (100, 100), color=(0, 255, 0)),
            ],
            "label": [0, 0, 1, 1],
        }
    )
    dataset = remove_duplicates(dataset, "image")
    assert len(dataset) == 2
    assert dataset["label"] == [0, 0]


@pytest.fixture
def sample_dataset():
    # Use ClassLabel for label to support stratify
    dataset = Dataset.from_dict({"text": ["a", "b", "c", "d", "e"], "label": [0, 1, 0, 1, 0]})
    dataset = dataset.cast_column("label", ClassLabel(num_classes=2, names=["0", "1"]))
    return dataset


@pytest.fixture
def sample_dataset_small():
    dataset = Dataset.from_dict({"text": ["a", "b", "c"], "label": [0, 1, 0]})
    dataset = dataset.cast_column("label", ClassLabel(num_classes=2, names=["0", "1"]))
    return dataset


@pytest.fixture
def sample_datasetdict(sample_dataset):
    splits = {"train": sample_dataset, "test": sample_dataset}
    return DatasetDict(splits)


def test_reduce_dataset_keep_percent(sample_dataset):
    reduced = reduce_dataset(sample_dataset, keep_percent=0.4)
    assert len(reduced) == 2  # 5 * 0.4 = 2
    assert set(reduced["text"]).issubset(set(sample_dataset["text"]))


def test_reduce_dataset_max_rows(sample_dataset):
    reduced = reduce_dataset(sample_dataset, max_rows=3)
    assert len(reduced) == 3
    assert set(reduced["text"]).issubset(set(sample_dataset["text"]))


def test_reduce_dataset_keep_percent_and_max_rows_error(sample_dataset_small):
    with pytest.raises(ValueError):
        reduce_dataset(sample_dataset_small, keep_percent=0.5, max_rows=2)


def test_reduce_dataset_invalid_keep_percent(sample_dataset_small):
    with pytest.raises(ValueError):
        reduce_dataset(sample_dataset_small, keep_percent=0.0)
    with pytest.raises(ValueError):
        reduce_dataset(sample_dataset_small, keep_percent=1.1)


def test_reduce_dataset_stratify_by_column(sample_dataset):
    reduced = reduce_dataset(sample_dataset, keep_percent=0.4, stratify_by_column="label")
    assert len(reduced) == 2
    # Should have one of each label
    assert sorted(reduced["label"]) == [0, 1]


def test_reduce_dataset_stratify_by_column_missing(sample_dataset_small):
    # Remove label column for this test
    dataset = sample_dataset_small.remove_columns("label")
    with pytest.raises(ValueError):
        reduce_dataset(dataset, keep_percent=0.5, stratify_by_column="label")


def test_reduce_dataset_dict(sample_datasetdict):
    reduced = reduce_dataset(sample_datasetdict, keep_percent=0.4)
    assert isinstance(reduced, DatasetDict)
    assert set(reduced.keys()) == {"train", "test"}
    assert all(len(split) == 2 for split in reduced.values())


def test_reduce_dataset_dict_max_rows(sample_datasetdict):
    reduced = reduce_dataset(sample_datasetdict, max_rows=3)
    assert isinstance(reduced, DatasetDict)
    assert all(len(split) == 3 for split in reduced.values())
