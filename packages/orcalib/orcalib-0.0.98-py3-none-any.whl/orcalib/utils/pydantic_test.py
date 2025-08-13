import json
from uuid import UUID

import numpy as np
import pytest
from PIL import Image as pil
from pydantic import BaseModel
from uuid_utils.compat import uuid4, uuid7

from .pydantic import (
    UNSET,
    UUID7,
    ColumnInfo,
    ColumnType,
    Image,
    InputType,
    InputTypeList,
    Timeseries,
    Vector,
    base64_encode_image,
    base64_encode_numpy_array,
    decode_base64_image,
    decode_base64_numpy_array,
    input_type_eq,
)

SAMPLE_BASE64_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg=="


def test_base64_encode_image():
    # When we decode the base64 image
    decoded = decode_base64_image(SAMPLE_BASE64_IMAGE)
    # Then the result is an image
    assert isinstance(decoded, pil.Image)
    # And the image is a PNG
    assert decoded.format == "PNG"
    # And the image has the correct size
    assert decoded.size == (9, 9)
    # When we encode the image back to base64
    encoded = base64_encode_image(decoded)
    # Then the result is the same as the original base64 image
    assert encoded == SAMPLE_BASE64_IMAGE


def test_base64_encode_numpy_array():
    # Given a float32 numpy array
    array = np.random.rand(10, 10).astype(np.float32)
    # When we encode it to base64
    encoded = base64_encode_numpy_array(array)
    # Then the result is a string
    assert isinstance(encoded, str)
    # When we decode the base64 string back to a numpy array
    decoded = decode_base64_numpy_array(encoded)
    # Then the result is a numpy array
    assert isinstance(decoded, np.ndarray)
    # And the result has the correct shape
    assert decoded.shape == array.shape
    # And the result has the correct type
    assert decoded.dtype == np.float32
    # And the result is the same as the original array
    assert np.allclose(decoded, array)


@pytest.fixture
def sample_image():
    return decode_base64_image(SAMPLE_BASE64_IMAGE)


@pytest.fixture
def sample_vector():
    return np.random.rand(16).astype(np.float32)


@pytest.fixture
def sample_timeseries():
    return np.random.rand(10, 2).astype(np.float32)


class SampleModel(BaseModel):
    image: Image | None = None
    vector: Vector | None = None
    timeseries: Timeseries | None = None
    uuid7: UUID7 | None = None
    unset: int | None = UNSET
    uuid7_list: list[UUID7] = []
    value: InputType | None = None
    values: InputTypeList = []


def test_unset():
    # Given a model with an unset field
    model = SampleModel()
    # Then the field defaults to UNSET
    assert model.unset is UNSET
    # And it is falsy
    assert not model.unset
    # And the field can be excluded from model dump
    assert model.model_dump(exclude_unset=True) == {}
    # When the field is set to None
    model = SampleModel(unset=None)
    # Then the field is set to None
    assert model.unset != UNSET
    assert model.unset is None
    # And the field is included in model dump
    assert model.model_dump(exclude_unset=True) == {"unset": None}


def test_validate_image(sample_image):
    # When we instantiate a model with a valid image
    model = SampleModel(image=sample_image)
    # Then the image is valid
    assert isinstance(model.image, pil.Image)
    # And the image is the same as the original image
    assert model.image is sample_image


def test_validate_image_invalid():
    # When we instantiate a model with an invalid image
    with pytest.raises(ValueError):
        SampleModel(image="not an image")  # type: ignore


def test_image_json_dump(sample_image):
    # Given a model with an image
    model = SampleModel(image=sample_image)
    # When we dump the model to a json dict
    json_dict = model.model_dump(mode="json", exclude_unset=True)
    # Then the image is encoded to base64
    assert isinstance(json_dict["image"], str)
    assert json_dict["image"] == SAMPLE_BASE64_IMAGE
    # When we dump the model to a json string
    json_str = model.model_dump_json(exclude_unset=True)
    # Then the image is encoded to base64
    assert isinstance(json_str, str)
    assert json.loads(json_str)["image"] == SAMPLE_BASE64_IMAGE


def test_image_python_dump(sample_image):
    # Given a model with an image
    model = SampleModel(image=sample_image)
    # When we dump the model to a Python dict
    dict = model.model_dump(mode="python")
    # Then the image is the same as the original image
    assert dict["image"] is sample_image


def test_image_load_json(sample_image):
    # Given a json string with an image
    json_str = json.dumps({"image": SAMPLE_BASE64_IMAGE})
    # When we load the image from the json string
    model = SampleModel.model_validate_json(json_str)
    # Then the image is parsed as a PIL image
    assert isinstance(model.image, pil.Image)
    # And the image is the same as the original image
    assert model.image == sample_image


def test_image_json_schema(sample_image):
    # Given a model with an image
    model = SampleModel(image=sample_image)
    # When we get the json schema
    schema = model.model_json_schema()
    image_schema = schema["properties"]["image"]["anyOf"][0]
    # Then the schema is a string
    assert image_schema["type"] == "string"
    assert image_schema["contentEncoding"] == "base64"
    assert image_schema["contentMediaType"] == "image"
    assert image_schema["format"] == "binary"


def test_validate_vector(sample_vector):
    # When we instantiate a model with a valid vector
    model = SampleModel(vector=sample_vector)
    # Then the vector is valid
    assert isinstance(model.vector, np.ndarray)
    # And the vector has the correct type and shape
    assert model.vector.dtype == np.float32
    assert model.vector.shape == sample_vector.shape
    # And the vector is the same as the original vector
    assert model.vector is sample_vector


def test_validate_vector_shape():
    # When an vector is instantiated with the wrong shape an error is raised
    with pytest.raises(ValueError):
        SampleModel(vector=np.random.rand(4, 16).astype(np.float32))  # type: ignore


def test_validate_vector_dtype():
    # When an vector is instantiated with the wrong dtype an error is raised
    with pytest.raises(ValueError):
        SampleModel(vector=np.random.rand(16).astype(np.float64))  # type: ignore


def test_vector_json_dump(sample_vector):
    # Given a model with an vector
    model = SampleModel(vector=sample_vector)
    # When we dump the model to a json dict
    json_dict = model.model_dump(mode="json", exclude_unset=True)
    # Then the vector is encoded as a list of floats
    assert isinstance(json_dict["vector"], list)
    assert json_dict["vector"] == sample_vector.tolist()
    # When we dump the model to a json string
    json_str = model.model_dump_json(exclude_unset=True)
    # Then the vector is encoded as a list of floats
    assert isinstance(json_str, str)
    assert json.loads(json_str)["vector"] == sample_vector.tolist()


def test_vector_python_dump(sample_vector):
    # Given a model with an vector
    model = SampleModel(vector=sample_vector)
    # When we dump the model to a Python dict
    dict = model.model_dump(mode="python")
    # Then the vector is the same as the original vector
    assert dict["vector"] is sample_vector


def test_vector_load_json(sample_vector):
    # Given a json string with an vector
    json_str = json.dumps({"vector": sample_vector.tolist()})
    # When we load the vector from the json string
    model = SampleModel.model_validate_json(json_str)
    # Then the vector is parsed as a numpy array
    assert isinstance(model.vector, np.ndarray)
    # And the vector has the correct type and shape
    assert model.vector.dtype == np.float32
    assert model.vector.shape == sample_vector.shape
    # And the vector is the same as the original vector
    assert (model.vector == sample_vector).all()


def test_vector_json_schema(sample_vector):
    # Given a model with a vector
    model = SampleModel(vector=sample_vector)
    # When we get the json schema
    schema = model.model_json_schema()
    vector_schema = schema["properties"]["vector"]["anyOf"][0]
    # Then the schema is a list of floats
    assert vector_schema["type"] == "array"
    assert vector_schema["items"] == {"type": "number"}


def test_validate_timeseries(sample_timeseries):
    # When we instantiate a model with a valid timeseries
    model = SampleModel(timeseries=sample_timeseries)
    # Then the timeseries is valid
    assert isinstance(model.timeseries, np.ndarray)
    # And the timeseries has the correct type and shape
    assert model.timeseries.dtype == np.float32
    assert model.timeseries.shape == sample_timeseries.shape
    # And the timeseries is the same as the original timeseries
    assert model.timeseries is sample_timeseries


def test_validate_timeseries_shape():
    # When a timeseries is instantiated with the wrong shape an error is raised
    with pytest.raises(ValueError):
        SampleModel(timeseries=np.random.rand(10).astype(np.float32))  # type: ignore


def test_validate_timeseries_dtype():
    # When a timeseries is instantiated with the wrong dtype an error is raised
    with pytest.raises(ValueError):
        SampleModel(timeseries=np.random.rand(10).astype(np.float64))  # type: ignore


def test_timeseries_json_dump(sample_timeseries):
    # Given a model with a timeseries
    model = SampleModel(timeseries=sample_timeseries)
    # When we dump the model to a json dict
    json_dict = model.model_dump(mode="json", exclude_unset=True)
    # Then the timeseries is encoded as a base64 encoded numpy array
    assert isinstance(json_dict["timeseries"], str)
    assert json_dict["timeseries"] == base64_encode_numpy_array(sample_timeseries)
    # When we dump the model to a json string
    json_str = model.model_dump_json(exclude_unset=True)
    # Then the timeseries is encoded as a base64 encoded numpy array
    assert isinstance(json_str, str)
    assert json.loads(json_str)["timeseries"] == base64_encode_numpy_array(sample_timeseries)


def test_timeseries_python_dump(sample_timeseries):
    # Given a model with a timeseries
    model = SampleModel(timeseries=sample_timeseries)
    # When we dump the model to a Python dict
    dict = model.model_dump(mode="python")
    # Then the timeseries is the same as the original timeseries
    assert dict["timeseries"] is sample_timeseries


def test_timeseries_load_json(sample_timeseries):
    # Given a json string with a timeseries
    json_str = json.dumps({"timeseries": base64_encode_numpy_array(sample_timeseries)})
    # When we load the timeseries from the json string
    model = SampleModel.model_validate_json(json_str)
    # Then the timeseries is parsed as a numpy array
    assert isinstance(model.timeseries, np.ndarray)
    # And the timeseries has the correct type and shape
    assert model.timeseries.dtype == np.float32
    assert model.timeseries.shape == sample_timeseries.shape
    # And the timeseries is the same as the original timeseries
    assert (model.timeseries == sample_timeseries).all()


def test_timeseries_json_schema(sample_timeseries):
    # Given a model with a timeseries
    model = SampleModel(timeseries=sample_timeseries)
    # When we get the json schema
    schema = model.model_json_schema()
    timeseries_schema = schema["properties"]["timeseries"]["anyOf"][0]
    # Then the schema is a base64 encoded numpy array
    assert timeseries_schema["type"] == "string"
    assert timeseries_schema["contentEncoding"] == "base64"
    assert timeseries_schema["contentMediaType"] == "numpy"
    assert timeseries_schema["format"] == "binary"


def test_validate_uuid7():
    # When we instantiate a model with a valid uuid7
    model = SampleModel(uuid7=uuid7())
    # Then the uuid is valid
    assert isinstance(model.uuid7, UUID)
    # And the uuid has the correct version
    assert model.uuid7.version == 7


def test_validate_uuid7_type():
    # When an uuid is instantiated with the wrong type an error is raised
    with pytest.raises(ValueError):
        SampleModel(uuid7="123")  # type: ignore


def test_validate_uuid7_version():
    # When an uuid is instantiated with the wrong version an error is raised
    with pytest.raises(ValueError):
        SampleModel(uuid7=uuid4())


def test_uuid7_json_dump():
    # Given a model with a uuid7
    uuid7_val = uuid7()
    model = SampleModel(uuid7=uuid7_val)
    # When we dump the model to a json dict
    json_dict = model.model_dump(mode="json", exclude_unset=True)
    # Then the uuid7 is encoded as a string
    assert isinstance(json_dict["uuid7"], str)
    assert json_dict["uuid7"] == str(uuid7_val)
    # When we dump the model to a json string
    json_str = model.model_dump_json(exclude_unset=True)
    # Then the uuid7 is encoded as a string
    assert isinstance(json_str, str)
    assert json.loads(json_str)["uuid7"] == str(uuid7_val)


def test_uuid7_python_dump():
    # Given a model with a uuid7
    uuid7_val = uuid7()
    model = SampleModel(uuid7=uuid7_val)
    # When we dump the model to a Python dict
    dict = model.model_dump(mode="python")
    # Then the uuid7 is the same as the original uuid7
    assert dict["uuid7"] is uuid7_val


def test_uuid7_load_json():
    # Given a json string with a uuid7
    uuid7_val = uuid7()
    json_str = json.dumps({"uuid7": str(uuid7_val)})
    # When we load the uuid7 from the json string
    model = SampleModel.model_validate_json(json_str)
    # Then the uuid7 is parsed as a uuid7
    assert isinstance(model.uuid7, UUID)
    assert model.uuid7.version == 7
    assert model.uuid7 == uuid7_val


def test_uuid7_list_load_json():
    # Given a json string with a list of uuid7
    uuid7_val = uuid7()
    json_str = json.dumps({"uuid7_list": [str(uuid7_val)]})
    # When we load the uuid7 from the json string
    model = SampleModel.model_validate_json(json_str)
    # Then the uuid7 is parsed as a uuid7
    assert isinstance(model.uuid7_list[0], UUID)
    assert model.uuid7_list[0].version == 7
    assert model.uuid7_list[0] == uuid7_val


def test_uuid7_json_schema():
    # Given a model with a uuid7
    model = SampleModel(uuid7=uuid7())
    # When we get the json schema
    schema = model.model_json_schema()
    # Then the schema is a string
    assert schema["properties"]["uuid7"]["anyOf"][0]["type"] == "string"
    assert schema["properties"]["uuid7"]["anyOf"][0]["format"] == "uuid"


@pytest.mark.parametrize(
    "column_type,enum_options,int_values,expected_error",
    [
        (ColumnType.ENUM, None, None, "enum_options must be set for ENUM column types"),
        (ColumnType.STRING, ["test1", "test2"], None, "enum_options is only valid for ENUM column types"),
        (ColumnType.STRING, None, [1, 2, 3], "int_values is only valid for INT column types"),
    ],
)
def test_column_info_validation_errors(column_type, enum_options, int_values, expected_error):
    # When a column info is instantiated with invalid configuration
    with pytest.raises(ValueError, match=expected_error):
        ColumnInfo(name="test", type=column_type, enum_options=enum_options, int_values=int_values)


def test_column_info_int_values_valid():
    """Test that INT columns can have int_values set correctly"""
    # When a column info is instantiated with INT type and int_values
    column_info = ColumnInfo(name="test", type=ColumnType.INT, int_values=[0, 1, 2])
    assert column_info.name == "test"
    assert column_info.type == ColumnType.INT
    assert column_info.int_values == [0, 1, 2]
    assert column_info.enum_options is None


def test_input_type_load_json():
    # Can load image value
    model = SampleModel.model_validate_json(json.dumps({"value": SAMPLE_BASE64_IMAGE}))
    assert isinstance(model.value, pil.Image)

    # Can load timeseries value
    model = SampleModel.model_validate_json(json.dumps({"value": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]}))
    assert isinstance(model.value, np.ndarray)
    assert model.value.shape == (2, 3)
    assert model.value.dtype == np.float32

    # Can load string value
    model = SampleModel.model_validate_json(json.dumps({"value": "test"}))
    assert isinstance(model.value, str)
    assert model.value == "test"


def test_input_type_load_python(sample_image, sample_timeseries):
    # Can load image value
    model = SampleModel.model_validate({"value": sample_image})
    assert isinstance(model.value, pil.Image)

    # Can load timeseries value
    model = SampleModel.model_validate({"value": sample_timeseries})
    assert isinstance(model.value, np.ndarray)

    # Can load string value
    model = SampleModel.model_validate({"value": "test"})
    assert isinstance(model.value, str)
    assert model.value == "test"


def test_input_type_dump_json(sample_image, sample_timeseries):
    # Can dump image value
    payload = SampleModel(value=sample_image).model_dump(mode="json", exclude_unset=True)
    assert isinstance(payload["value"], str)
    assert payload["value"] == SAMPLE_BASE64_IMAGE

    # Can dump timeseries value
    payload = SampleModel(value=sample_timeseries).model_dump(mode="json", exclude_unset=True)
    assert isinstance(payload["value"], str)
    assert payload["value"] == base64_encode_numpy_array(sample_timeseries)

    # Can dump string value
    payload = SampleModel(value="test").model_dump(mode="json", exclude_unset=True)
    assert isinstance(payload["value"], str)
    assert payload["value"] == "test"


def test_input_type_list_load_json():
    # Can load list of images
    model = SampleModel.model_validate_json(json.dumps({"values": [SAMPLE_BASE64_IMAGE, SAMPLE_BASE64_IMAGE]}))
    assert isinstance(model.values, list)
    assert len(model.values) == 2
    assert all(isinstance(item, pil.Image) for item in model.values)

    # Can load list of timeseries
    model = SampleModel.model_validate_json(
        json.dumps({"values": [np.random.rand(10, 2).tolist(), np.random.rand(10, 2).tolist()]})
    )
    assert isinstance(model.values, list)
    assert len(model.values) == 2
    assert all(isinstance(item, np.ndarray) for item in model.values)

    # Can load list of strings
    model = SampleModel.model_validate_json(json.dumps({"values": ["test1", "test2"]}))
    assert isinstance(model.values, list)
    assert len(model.values) == 2
    assert all(isinstance(item, str) for item in model.values)


def test_compare_input_type():
    # Can identify identical images
    image1 = decode_base64_image(SAMPLE_BASE64_IMAGE)
    image2 = decode_base64_image(SAMPLE_BASE64_IMAGE)
    assert input_type_eq(image1, image2)

    # Can identify different images
    image3 = decode_base64_image(SAMPLE_BASE64_IMAGE)
    image3.putpixel((0, 0), (10, 10, 10))
    assert not input_type_eq(image1, image3)

    # Can identify identical timeseries
    timeseries1 = np.random.rand(10, 2).astype(np.float32)
    timeseries2 = timeseries1.copy()
    assert input_type_eq(timeseries1, timeseries2)

    # Can identify different timeseries
    timeseries3 = np.random.rand(10, 2).astype(np.float32)
    assert not input_type_eq(timeseries1, timeseries3)

    # Can identify identical strings
    assert input_type_eq("test", "test")

    # Can identify different strings
    assert not input_type_eq("test", "Test")

    # Can identify mismatched types
    assert not input_type_eq("test", np.random.rand(10, 2).astype(np.float32))
