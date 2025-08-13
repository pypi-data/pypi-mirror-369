import base64
import hashlib
import io
import re
from enum import Enum
from typing import Annotated, Any, Literal

import numpy as np
from numpy.typing import DTypeLike, NDArray
from PIL import Image as pil
from pydantic import BaseModel, GetPydanticSchema, model_validator
from pydantic_core import core_schema
from uuid_utils.compat import UUID


def base64_encode_image(image: pil.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format=image.format)
    bytes = buffer.getvalue()
    header = f"data:image/{image.format.lower()};base64," if image.format else "data:image;base64,"
    return header + base64.b64encode(bytes).decode("utf-8")


def decode_base64_image(base64_image: str) -> pil.Image:
    if not re.match(r"^data:image(?:/[a-z0-9-]+)?;base64,", base64_image):
        raise ValueError("Expected a base64 encoded image")
    return pil.open(io.BytesIO(base64.b64decode(base64_image.split(",")[1])))


def validate_pil_image(image, format: str | None = None) -> pil.Image:
    if not isinstance(image, pil.Image):
        image = decode_base64_image(image)
    if not image.format:
        raise ValueError("Expected a PIL image with a valid format")
    if format is not None and image.format != format:
        raise ValueError(f"Expected a PIL image with format {format}, got {image.format}")
    return image


Image = Annotated[
    pil.Image,
    GetPydanticSchema(
        get_pydantic_core_schema=lambda _, handler: core_schema.with_info_plain_validator_function(
            lambda val, info: validate_pil_image(val),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda val, info: base64_encode_image(val) if info.mode == "json" else val,
                info_arg=True,
            ),
        ),
        get_pydantic_json_schema=lambda _, handler: {
            **handler(core_schema.bytes_schema()),
            "contentEncoding": "base64",
            "contentMediaType": "image",
            "pattern": "^data:image(?:/[a-z0-9.-]+)?;base64,[A-Za-z0-9+/=]+$",
        },
    ),
]


# this is about 2.2x more space efficient in JSON than plain list[float] encoding for 768-dim
# float32 arrays when using gzip compression, we only use it for timeseries for now
def base64_encode_numpy_array(array: NDArray) -> str:
    buffer = io.BytesIO()
    np.save(buffer, array)
    header = f"data:numpy/{array.dtype.name};base64,"
    return header + base64.b64encode(buffer.getvalue()).decode("utf-8")


def decode_base64_numpy_array(base64_array: str) -> NDArray:
    if not re.match(r"^data:numpy(?:/[a-z0-9-]+)?;base64,", base64_array):
        raise ValueError("Expected a base64 encoded numpy array")
    buffer = io.BytesIO(base64.b64decode(base64_array.split(",")[1]))
    return np.load(buffer)


def validate_numpy_array(
    arr,
    dtype: DTypeLike | None = None,
    ndim: int | None = None,
    shape: tuple[int, ...] | None = None,
) -> NDArray:
    if isinstance(arr, str):
        arr = decode_base64_numpy_array(arr)
    elif not isinstance(arr, np.ndarray):
        arr = np.array(arr, dtype=dtype)
    if dtype is not None:
        if arr.dtype != dtype:
            raise ValueError(f"Expected a numpy array with dtype {dtype}, got {arr.dtype}")
    if ndim is not None:
        if arr.ndim != ndim:
            raise ValueError(f"Expected a numpy array with {ndim} dimensions, got {arr.ndim}")
    if shape is not None:
        if arr.shape != shape:
            raise ValueError(f"Expected a numpy array with shape {shape}, got {arr.shape}")
    return arr


Vector = Annotated[
    NDArray[np.float32],
    GetPydanticSchema(
        get_pydantic_core_schema=lambda _, handler: core_schema.with_info_plain_validator_function(
            lambda val, info: validate_numpy_array(val, dtype=np.float32, ndim=1),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda val, info: val.tolist() if info.mode == "json" else val,
                info_arg=True,
            ),
        ),
        get_pydantic_json_schema=lambda _, handler: handler(core_schema.list_schema(core_schema.float_schema())),
    ),
]
"""Vector is a 1D numpy array of shape (embedding_dim,)"""


Timeseries = Annotated[
    NDArray[np.float32],
    GetPydanticSchema(
        get_pydantic_core_schema=lambda _, handler: core_schema.with_info_plain_validator_function(
            lambda val, info: validate_numpy_array(val, dtype=np.float32, ndim=2),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda val, info: base64_encode_numpy_array(val) if info.mode == "json" else val,
                info_arg=True,
            ),
        ),
        get_pydantic_json_schema=lambda _, handler: {
            **handler(core_schema.bytes_schema()),
            "contentEncoding": "base64",
            "contentMediaType": "numpy",
            "pattern": "^data:numpy(?:/[a-z0-9-]+)?;base64,[A-Za-z0-9+/=]+$",
        },
    ),
]
"""Timeseries are a 2D numpy array of shape (num_timestamps, num_features), may contain NaN values"""


def validate_uuid(val, version: Literal[4, 7]) -> UUID:
    if not isinstance(val, UUID):
        val = UUID(val)
    if val.version != version:
        raise ValueError(f"Expected a UUID{version}, got UUID{val.version}")
    return val


UUID7 = Annotated[
    UUID,
    GetPydanticSchema(
        get_pydantic_core_schema=lambda _, handler: core_schema.with_info_plain_validator_function(
            lambda val, info: validate_uuid(val, version=7),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda val, info: str(val) if info.mode == "json" else val,
                info_arg=True,
            ),
        ),
        get_pydantic_json_schema=lambda _, handler: {**handler(core_schema.str_schema()), "format": "uuid"},
    ),
]


class _UnsetSentinel:
    """
    Default value for fields that do not allow passing None (`null` in JSON) but are not required to
    be set either (i.e. IF they are passed in, they are required and CANNOT be None, BUT they are
    allowed to not be set at all in which case they will be defaulted to UNSET)

    The most common use case for this is on a PATCH update request where a field NOT being set means
    we do not want to update that field but a field being set to None means we want to update that
    field value to None

    see also: https://github.com/pydantic/pydantic/issues/5326
    """

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "UNSET"


UNSET: Any = _UnsetSentinel()

# Restricting metadata values to primitive types in order to better support Milvus filtering
Metadata = dict[str, str | int | float | bool | None]


InputType = str | Timeseries | Image
InputTypeList = (
    list[str] | list[Timeseries] | list[Image] | list[InputType]
)  # this is not equivalent to list[InputType]


def input_type_eq(a: InputType, b: InputType) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    if isinstance(a, pil.Image) and isinstance(b, pil.Image):
        # compare images by checking the bounding boxes
        hash_image = lambda image: hashlib.md5(image.convert("RGB").tobytes()).hexdigest()  # noqa: E731
        return hash_image(a) == hash_image(b)
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        # compare timeseries by checking if they are close enough
        return np.allclose(a, b)
    return False


class ColumnType(str, Enum):
    """The type of a column in a datasource"""

    STRING = "STRING"
    FLOAT = "FLOAT"
    INT = "INT"
    BOOL = "BOOL"
    ENUM = "ENUM"
    IMAGE = "IMAGE"
    OTHER = "OTHER"


class ColumnInfo(BaseModel):
    """
    Information about a column in a datasource
    """

    name: str
    """Name of the column"""

    type: ColumnType
    """
    Simplified dtype of the column:
        - STRING: Value column with dtype 'string'
        - FLOAT: Value column with dtype 'float', 'float16', 'float32', 'double', or 'float64'
        - INT: Value column with dtype 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', or 'uint64'
        - BOOL: Value column with dtype 'bool'
        - ENUM: ClassLabel column
        - IMAGE: Image column
        - OTHER: Any other column type / dtype combination including datetimes, lists, dicts, etc.
    """

    enum_options: list[str] | None = None
    """The options for the column if it is a categorical column."""

    int_values: list[int] | None = None
    """The distinct integer values in the column, only for INT type columns."""

    @model_validator(mode="after")
    def check_column_constraints(self):
        if self.type == ColumnType.ENUM and self.enum_options is None:
            raise ValueError("enum_options must be set for ENUM column types")
        if self.type != ColumnType.ENUM and self.enum_options is not None:
            raise ValueError("enum_options is only valid for ENUM column types")
        if self.type != ColumnType.INT and self.int_values is not None:
            raise ValueError("int_values is only valid for INT column types")
        return self
