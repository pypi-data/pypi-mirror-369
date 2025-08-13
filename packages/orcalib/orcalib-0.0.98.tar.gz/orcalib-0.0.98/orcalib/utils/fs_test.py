import os
import tempfile
from uuid import uuid4

import pytest
from datasets import Dataset

from .fs import (
    delete_dir,
    download_dir,
    exists_dir,
    get_fs,
    is_using_blob_storage,
    list_dir,
    upload_dir,
)


def test_is_using_blob_storage():
    assert not is_using_blob_storage("OrcaDB/clip-ViT-L-14")
    assert not is_using_blob_storage("distilbert-base-uncased")
    assert not is_using_blob_storage("file://test")
    assert not is_using_blob_storage("./temp/something")
    assert is_using_blob_storage("memory://orcalib-tests/something")
    assert is_using_blob_storage("local://orcalib-tests/something")
    assert is_using_blob_storage("gs://orcadb-internal/something")
    assert is_using_blob_storage("minio://orcalib-tests/something")


PROTOCOLS = [
    "local",
    "memory",
    # Cloud protocols:
    # "minio",
    # To run tests against the "minio" backend, run a minio docker as defined in lighthouse
    # "gs",
    # To run tests against the "gs" backend, please run
    # - `gcloud auth application-default login` to authenticate with Google Cloud
    # - `gcloud config set project orcadb-internal` to set the project
]
TEST_BUCKET_PREFIX = "orcalib-test"


@pytest.fixture(params=PROTOCOLS)
def fs(request):
    return get_fs(f"{request.param}://")


@pytest.fixture
def bucket(fs):
    bucket_path = f"{fs.protocol}://{TEST_BUCKET_PREFIX}-{uuid4().hex[:8]}"
    fs.mkdir(bucket_path)
    yield bucket_path


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    for protocol in PROTOCOLS:
        fs = get_fs(f"{protocol}://")
        for bucket_path in fs.ls(f"{protocol}://", detail=False):
            if bucket_path.startswith(TEST_BUCKET_PREFIX):
                fs.rm(bucket_path.strip("/"), recursive=True)


@pytest.fixture()
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_list_dir(fs, bucket):
    # Given a remote bucket with a file and a subfolder
    fs.write_text(f"{bucket}/test.txt", "Hello, world!")
    fs.touch(f"{bucket}/subdir/test.txt")
    # Then we can list the contents of the bucket
    assert f"{bucket}/test.txt" in list_dir(bucket)
    assert f"{bucket}/subdir" in list_dir(bucket)
    # And we can list the contents of the subfolder
    assert f"{bucket}/subdir/test.txt" in list_dir(f"{bucket}/subdir")


def test_delete_dir(fs, bucket):
    # Given a folder with a file and a subfolder
    folder_path = f"{bucket}/test"
    fs.write_text(f"{folder_path}/test.txt", "Hello, world!")
    fs.touch(f"{folder_path}/subdir/test.txt")
    # When the folder is deleted
    delete_dir(folder_path)
    # Then the folder should no longer exist
    assert folder_path not in list_dir(bucket)


def test_exists_dir(fs, bucket):
    # Given a folder that exists
    folder_path = f"{bucket}/test"
    fs.write_text(f"{folder_path}/test.txt", "Hello, world!")
    # Then the folder should exist
    assert exists_dir(folder_path)
    # And a folder that does not exist
    assert not exists_dir(f"{bucket}/non-existent")


def test_upload_dir(fs, bucket, temp_dir):
    # Given a local source folder with a file and a subfolder
    local_source_path = f"{temp_dir}/source"
    os.makedirs(local_source_path, exist_ok=True)
    with open(f"{local_source_path}/test.txt", "w") as f:
        f.write("Hello, world!")
    os.makedirs(f"{local_source_path}/subdir")
    with open(f"{local_source_path}/subdir/test.txt", "w") as f:
        f.write("")
    assert len(os.listdir(local_source_path)) == 2
    # When uploading the local folder to a remote bucket
    remote_target_path = f"{bucket}/target"
    upload_dir(local_source_path, remote_target_path, recursive=False)
    # Then the remote bucket should contain the local folder contents
    assert f"{remote_target_path}/test.txt" in list_dir(remote_target_path)
    # And the subfolder should not be uploaded
    assert f"{remote_target_path}/subdir" not in list_dir(remote_target_path)
    assert fs.cat_file(f"{remote_target_path}/test.txt").decode("utf-8") == "Hello, world!"


def test_upload_dir_recursive(fs, bucket, temp_dir):
    # Given a local source folder with a file and a subfolder
    local_source_path = f"{temp_dir}/source"
    os.makedirs(local_source_path, exist_ok=True)
    with open(f"{local_source_path}/test.txt", "w") as f:
        f.write("Hello, world!")
    os.makedirs(f"{local_source_path}/subdir")
    with open(f"{local_source_path}/subdir/test.txt", "w") as f:
        f.write("")
    assert len(os.listdir(local_source_path)) == 2
    # When uploading the local folder to a remote bucket
    remote_target_path = f"{bucket}/target"
    upload_dir(local_source_path, remote_target_path, recursive=True)
    # Then the remote bucket should contain the local folder contents
    assert f"{remote_target_path}/test.txt" in list_dir(remote_target_path)
    assert fs.cat_file(f"{remote_target_path}/test.txt").decode("utf-8") == "Hello, world!"
    assert f"{remote_target_path}/subdir" in list_dir(remote_target_path)
    # And the subfolder should be uploaded as well
    assert f"{remote_target_path}/subdir/test.txt" in list_dir(f"{remote_target_path}/subdir")


def test_download_dir(fs, bucket, temp_dir):
    # Given a remote source folder with a file and a subfolder
    remote_source_path = f"{bucket}/source"
    fs.write_text(f"{remote_source_path}/test.txt", "Hello, world!")
    fs.touch(f"{remote_source_path}/subdir/test.txt")
    assert len(list_dir(remote_source_path)) == 2
    # When downloading the remote folder to a local folder
    local_target_path = f"{temp_dir}/target"
    download_dir(remote_source_path, local_target_path, recursive=False)
    # Then the local folder should contain the remote folders direct contents
    assert "test.txt" in os.listdir(local_target_path)
    with open(f"{local_target_path}/test.txt", "r") as f:
        assert f.read() == "Hello, world!"
    # And the subfolder should not be downloaded
    assert "subdir" not in os.listdir(local_target_path)


def test_download_dir_recursive(fs, bucket, temp_dir):
    # Given a remote source folder with a file and a subfolder
    remote_source_path = f"{bucket}/source"
    fs.write_text(f"{remote_source_path}/test.txt", "Hello, world!")
    fs.touch(f"{remote_source_path}/subdir/test.txt")
    assert len(list_dir(remote_source_path)) == 2
    # When downloading the remote folder and its subdirectories to a local folder
    local_target_path = f"{temp_dir}/target"
    download_dir(remote_source_path, local_target_path, recursive=True)
    # Then the local folder should contain the remote folders direct contents
    assert "test.txt" in os.listdir(local_target_path)
    with open(f"{local_target_path}/test.txt", "r") as f:
        assert f.read() == "Hello, world!"
    assert "subdir" in os.listdir(local_target_path)
    assert "test.txt" in os.listdir(f"{local_target_path}/subdir")


def test_upload_download_dir(bucket, temp_dir):
    # Given a local source folder with a file
    local_source_path = f"{temp_dir}/source"
    os.makedirs(local_source_path, exist_ok=True)
    with open(f"{local_source_path}/test.txt", "w") as f:
        f.write("Hello, world!")
    # When uploading the local folder to a remote bucket
    remote_target_path = f"{bucket}/subdir"
    upload_dir(local_source_path, remote_target_path)
    assert f"{remote_target_path}/test.txt" in list_dir(remote_target_path)
    # And then downloading the remote folder back to a local folder
    local_target_path = f"{temp_dir}/target"
    os.makedirs(local_target_path)
    download_dir(remote_target_path, local_target_path)
    # Then the local folder should contain the file
    assert "test.txt" in os.listdir(local_target_path)
    with open(f"{local_target_path}/test.txt", "r") as f:
        assert f.read() == "Hello, world!"


def test_dataset_support(bucket):
    # Given a dataset
    dataset = Dataset.from_dict({"text": ["Hello", "world", "!"]})
    # When saving the dataset to a remote bucket
    remote_dataset_path = f"{bucket}/dataset"
    dataset.save_to_disk(remote_dataset_path)
    # Then the remote bucket should contain the dataset files
    dataset_files = list_dir(remote_dataset_path)
    assert len(dataset_files) > 0
    assert f"{remote_dataset_path}/dataset_info.json" in dataset_files
    # When loading the dataset from the remote bucket
    reloaded_dataset = Dataset.load_from_disk(remote_dataset_path)
    assert reloaded_dataset.num_rows == 3
    assert reloaded_dataset.column_names == ["text"]
    assert reloaded_dataset["text"] == ["Hello", "world", "!"]
