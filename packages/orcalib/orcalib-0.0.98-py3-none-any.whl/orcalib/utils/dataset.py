import hashlib
import logging
from typing import Any, overload

import numpy as np
from datasets import Array2D, ClassLabel, Dataset, DatasetDict, Image, Sequence, Value
from datasets.utils.logging import disable_progress_bar
from PIL import Image as pil

from .pydantic import ColumnInfo, ColumnType

disable_progress_bar()

_PARSED_BUILDER_NAME_SUFFIX = "*orca"


def is_parsed(dataset: Dataset) -> bool:
    return dataset.info.builder_name is not None and dataset.info.builder_name.endswith(_PARSED_BUILDER_NAME_SUFFIX)


def parse_dataset(
    dataset: Dataset,
    *,
    value_column: str,
    label_column: str | None = None,
    score_column: str | None = None,
    source_id_column: str | None = None,
    other_columns_as_metadata: bool = False,
    label_names: list[str] | None = None,
    num_classes: int | None = None,
    sample: int | float | None = None,
) -> Dataset:
    """
    Transforms a dataset to have canonical value, label, score, source_id, and metadata columns or raises an error

    Args:
        dataset: The dataset to transform
        value_column: The name of the column containing the string or image values to embed
        label_column: Optional name of the column containing the integer labels
        score_column: Optional name of the column containing the float scores
        source_id_column: Optional name of a column containing unique IDs for each data point in a system of reference
        other_columns_as_metadata: Optionally collect all other column values in a dictionary in the metadata column
        label_names: Optional list of label names to use when casting the label column to a ClassLabel
        num_classes: Optional number of classes to use when casting the label column to a ClassLabel
        sample: Optional number of rows or fraction of rows to sample from the dataset
    Returns:
        The transformed dataset which is guaranteed to have the following features:
            - 'value' image column or string value column
            - 'label' class label column (optional), if casted from int column will use the
                label names if provided or the number of classes if provided or find the number of
                unique values in the column
            - 'score' float value column (optional)
            - 'source_id' string value column (optional)
            - 'metadata' dictionary column (optional)

    Raises:
        ValueError: If the specified columns are not found or have the wrong data type
    """
    if is_parsed(dataset):
        return dataset

    out_dataset = dataset
    columns_to_keep = ["value"]

    # validate value column
    if value_column not in dataset.features:
        raise ValueError(f"Specified value column `{value_column}` not found in dataset")

    value_column_error = ValueError(
        f"The specified value column `{value_column}` must be of type string, image, or float 1D or 2D sequence/array"
    )
    if isinstance(dataset.features[value_column], Sequence):  # timeseries
        # transform 1D sequences to 2D sequences
        if isinstance(dataset.features[value_column].feature, Value):
            out_dataset = out_dataset.map(lambda x: {value_column: [[v] for v in x[value_column]]})
        # cast the column into a 2D array to validate that it has a consistent shape and dtype
        shape = (None, out_dataset.with_format("np")[value_column][0].shape[1])
        try:
            out_dataset = out_dataset.cast_column(value_column, Array2D(dtype="float32", shape=shape))
            out_dataset[value_column][0]  # need to access a value to trigger validation
        except Exception:
            raise value_column_error
    elif isinstance(dataset.features[value_column], Array2D):  # timeseries
        if dataset.features[value_column].dtype != "float32":
            out_dataset = dataset.cast_column(
                value_column, Array2D(dtype="float32", shape=dataset.features[value_column].shape)
            )
    elif not (
        isinstance(dataset.features[value_column], Image)
        or (isinstance(dataset.features[value_column], Value) and dataset.features[value_column].dtype == "string")
    ):
        raise value_column_error

    if value_column != "value":
        out_dataset = out_dataset.rename_column(value_column, "value")

    # ensure image is decoded if value column is image
    if isinstance(out_dataset.features["value"], Image) and not out_dataset.features["value"].decode:
        out_dataset = out_dataset.cast_column("value", Image(decode=True))

    # ensure timeseries values get returned as numpy arrays
    if isinstance(out_dataset.features["value"], Array2D):
        out_dataset.set_transform(
            lambda batch: {
                "value": [
                    np.array(v, dtype=out_dataset.features["value"].dtype) for v in batch["value"]
                ]  # return a list of 2d numpy arrays
            },
            columns=["value"],
            output_all_columns=True,
        )

    # validate label column
    if label_column is not None:
        if label_column not in dataset.features:
            raise ValueError(f"Specified label column `{label_column}` not found in dataset")
        if not (
            (
                isinstance(dataset.features[label_column], Value)
                or isinstance(dataset.features[label_column], ClassLabel)
            )
            and dataset.features[label_column].dtype == "int64"
        ):
            raise ValueError(
                f"Specified label column `{label_column}` must be a class label or an integer value column"
            )
        if not isinstance(dataset.features[label_column], ClassLabel):
            out_dataset = out_dataset.cast_column(
                label_column,
                (
                    ClassLabel(names=label_names)
                    if label_names is not None
                    else ClassLabel(num_classes=num_classes or len(set(dataset[label_column])))
                ),
            )
        columns_to_keep.append("label")
        if label_column != "label":
            out_dataset = out_dataset.rename_column(label_column, "label")

    # sample the dataset if specified
    if sample is not None:
        if sample >= len(out_dataset):
            logging.warning(f"Skipping sampling since dataset only has {len(out_dataset)} <= {sample} rows")
        else:
            out_dataset = out_dataset.train_test_split(
                test_size=sample, seed=42, shuffle=True, stratify_by_column="label" if label_column else None
            )["test"]

    # validate score column
    if score_column is not None:
        if score_column not in dataset.features:
            raise ValueError(f"Specified score column `{score_column}` not found in dataset")
        if not (
            isinstance(dataset.features[score_column], Value)
            and dataset.features[score_column].dtype in ("float32", "float64", "int8", "int16", "int32", "int64")
        ):
            raise ValueError(
                f"The specified score column `{score_column}` must be of type float or int but got {dataset.features[score_column].dtype}"
            )

        # Convert integer score columns to float
        if dataset.features[score_column].dtype in ("int8", "int16", "int32", "int64"):
            out_dataset = out_dataset.cast_column(score_column, Value(dtype="float32"))

        columns_to_keep.append("score")
        if score_column != "score":
            out_dataset = out_dataset.rename_column(score_column, "score")

    # add source ID column if specified
    if source_id_column:
        if source_id_column not in dataset.features:
            raise ValueError(f"Specified source ID column `{source_id_column}` not found in dataset")
        if dataset.features[source_id_column].dtype != "string":
            raise ValueError(f"The specified source ID column `{source_id_column}` must be of type string")
        if source_id_column != "source_id":
            out_dataset = out_dataset.rename_column(source_id_column, "source_id")
        columns_to_keep.append("source_id")

    # add metadata column if specified
    if other_columns_as_metadata:
        incompatible_columns = [
            k
            for k, v in dataset.features.items()
            if k not in columns_to_keep and not (isinstance(v, Value) or isinstance(v, ClassLabel))
        ]
        if len(incompatible_columns) > 0:
            logging.warning(f"Excluding non-scalar columns {', '.join(incompatible_columns)} from metadata: ")
        out_dataset = out_dataset.map(
            lambda x: {"metadata": {k: v for k, v in x.items() if k not in columns_to_keep + incompatible_columns}}
        )
        columns_to_keep.append("metadata")

    # mark the dataset as parsed to avoid re-parsing
    out_dataset.info.builder_name = f"{out_dataset.info.builder_name or ''}{_PARSED_BUILDER_NAME_SUFFIX}"
    return out_dataset.select_columns(columns_to_keep)


def parse_label_names(dataset: Dataset, *, label_column: str) -> list[str] | None:
    """
    Parses the label names from a dataset if the label column is a ClassLabel

    Args:
        dataset: The dataset to parse
        label_column: The name of the column containing the class labels

    Returns:
        The list of label names or None if the label column is not a ClassLabel
    """
    if isinstance(dataset.features[label_column], ClassLabel):
        return dataset.features[label_column].names
    return None


def parse_dataset_schema(dataset: Dataset) -> list[ColumnInfo]:
    features = dataset.features

    def get_type(feature) -> ColumnType:
        match feature:
            case Value() if feature.dtype == "string":
                return ColumnType.STRING
            case Value() if "float" in feature.dtype:
                return ColumnType.FLOAT
            case Value() if "int" in feature.dtype:
                return ColumnType.INT
            case Value() if feature.dtype == "bool":
                return ColumnType.BOOL
            case ClassLabel():
                return ColumnType.ENUM
            case Image():
                return ColumnType.IMAGE
            case _:
                return ColumnType.OTHER

    column_infos = []
    for name, feature in features.items():
        column_type = get_type(feature)
        enum_options = feature.names if isinstance(feature, ClassLabel) else None
        int_values = None

        # For INT columns, collect distinct values
        if column_type == ColumnType.INT:
            distinct_values = list(set(dataset[name]))
            int_values = sorted(distinct_values)

        column_infos.append(
            ColumnInfo(
                name=name,
                type=column_type,
                enum_options=enum_options,
                int_values=int_values,
            )
        )

    return column_infos


@overload
def reduce_dataset(
    data: Dataset,
    *,
    keep_percent: float | None = None,
    max_rows: int | None = None,
    stratify_by_column: str | None = None,
    seed: int = 42,
) -> Dataset:
    pass


@overload
def reduce_dataset(
    data: DatasetDict,
    *,
    keep_percent: float | None = None,
    max_rows: int | None = None,
    stratify_by_column: str | None = None,
    seed: int = 42,
) -> DatasetDict:
    pass


def reduce_dataset(
    data: Dataset | DatasetDict,
    *,
    keep_percent: float | None = None,
    max_rows: int | None = None,
    stratify_by_column: str | None = None,
    seed: int = 42,
) -> Dataset | DatasetDict:
    """
    Reduce a Dataset or DatasetDict in size. Applies reduction to each split if DatasetDict.
    If both `keep_percent` and `max_rows` are provided (not recommended):
    - For a Dataset, it will use the smaller of the two.
    - For a DatasetDict, each split will be (separately) reduced using the smaller of the two values; i.e., some splits may be
        reduced by `keep_percent` while others by `max_rows`.

    Args:
        data (Dataset or DatasetDict): The data to reduce.
        keep_percent (float): The percentage of the dataset to keep (0.0 to 1.0).
        max_rows (int): The maximum number of rows to keep.
        stratify_by_column (str|None): Column to stratify by, if any.
        seed (int): Random seed for reproducibility.

    Returns:
        Dataset or DatasetDict: The reduced data.
    """
    if keep_percent is not None and max_rows is not None:
        raise ValueError("Please provide either `keep_percent` or `max_rows`, not both.")
    if keep_percent is not None:
        if not (0.0 < keep_percent <= 1.0):
            raise ValueError("`keep_percent` must be between 0.0 and 1.0.")
    if stratify_by_column is not None and stratify_by_column not in data.column_names:
        raise ValueError(f"Column '{stratify_by_column}' not found in dataset.")

    def _reduce(ds: Dataset) -> Dataset:
        num_rows = len(ds)
        if keep_percent is not None:
            num_rows = int(len(ds) * keep_percent)
        elif max_rows is not None:
            num_rows = min(num_rows, max_rows)

        stratified_data = ds.train_test_split(train_size=num_rows, stratify_by_column=stratify_by_column, seed=seed)
        return stratified_data["train"]

    if isinstance(data, DatasetDict):
        return DatasetDict({k: _reduce(v) for k, v in data.items()})
    else:
        return _reduce(data)


def remove_duplicates(dataset: Dataset, column: str) -> Dataset:
    """
    Removes all duplicate rows from a dataset based on the values in a column.

    Params:
        dataset: The dataset to remove duplicates from.
        column: The column to remove duplicates from.

    Returns:
        The dataset with duplicates removed.
    """

    def get_hash(example: dict[str, Any]):
        value = example[column]
        if isinstance(value, pil.Image):
            hash = hashlib.md5(value.convert("RGB").tobytes()).hexdigest()
        elif isinstance(value, str):
            hash = hashlib.md5(value.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
        return {"hash": hash}

    dataset = dataset.map(get_hash)
    uniques = set(dataset["hash"])

    def check_uniques(example: dict[str, Any]) -> bool:
        """Check if current hash is still in set of unique hashes and remove if true."""
        if example["hash"] in uniques:
            uniques.remove(example["hash"])
            return True
        else:
            return False

    return dataset.filter(lambda example: check_uniques(example)).remove_columns(["hash"])
