import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Generator, Literal

import fsspec
import fsspec.utils
from fsspec import AbstractFileSystem
from fsspec.config import conf as fsspec_conf
from fsspec.implementations.dirfs import DirFileSystem as BaseDirFileSystem
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem
from fsspec.registry import register_implementation
from fsspec.utils import stringify_path
from s3fs import S3FileSystem


class _DirFileSystem(BaseDirFileSystem):
    @classmethod
    def _strip_protocol(cls, path):
        if isinstance(path, list):
            return [cls._strip_protocol(p) for p in path]
        out: str = super()._strip_protocol(path)  # type: ignore
        # ensure trailing slash is not lost, because it is important for cp to work as expected
        return f"{out}/" if stringify_path(path).endswith("/") and not out.endswith("/") else out


class LocalDirFileSystem(_DirFileSystem):
    """A local file system that saves everything relative to a given base path"""

    protocol = "local"
    async_impl = False

    def __init__(self, base_path: str, **kwargs):
        """
        Initialize the local file system

        Args:
            base_path: The base path under which to store all files, this will be read from the
                `LOCAL_BLOB_STORAGE_ROOT` environment variable.
        """
        super().__init__(path=base_path, fs=LocalFileSystem(auto_mkdir=True, **kwargs))
        os.makedirs(self.path, exist_ok=True)


class MemoryDirFileSystem(_DirFileSystem):
    """A memory file system that does not have a leading slash in all paths"""

    protocol = "memory"
    async_impl = False

    def __init__(self):
        # the `/-` path is required to get rid of leading slashes in all paths
        super().__init__(path="/-", fs=MemoryFileSystem())
        self.mkdir(self.path)


class MinioFileSystem(S3FileSystem):
    """A file system implementation for [MinIO](https://min.io/)"""

    protocol = "minio"


# this config is registered globally and applies even when fsspec is used from within datasets or orcalib

register_implementation(MinioFileSystem.protocol, MinioFileSystem, clobber=False)
register_implementation(LocalDirFileSystem.protocol, LocalDirFileSystem, clobber=True)
register_implementation(MemoryDirFileSystem.protocol, MemoryDirFileSystem, clobber=True)

fsspec_conf["local"] = {
    "base_path": os.getenv("LOCAL_BLOB_STORAGE_ROOT", "~/.orca/buckets"),
}
fsspec_conf["gcs"] = {
    "project": os.getenv("GCP_PROJECT_ID", "orcadb-internal"),
}
fsspec_conf["minio"] = {
    "endpoint_url": os.getenv("MINIO_URL", "http://localhost:9000"),
    "key": os.getenv("MINIO_ROOT_USER", "default"),
    "secret": os.getenv("MINIO_ROOT_PASSWORD", "password"),
}

# Helper functions for saving and loading data to remote storage


def is_using_blob_storage(path: str) -> bool:
    """Check if a path is local or pointing to a remote bucket

    Args:
        path: The path to check

    Returns:
        `True` if the path points to a bucket, `False` if it is a normal local file path
    """
    return fsspec.utils.get_protocol(path) != "file"


def get_fs(path: str) -> AbstractFileSystem:
    """
    Get the file system implementation for a given path

    Args:
        path: The path to get the file system implementation for

    Returns:
        The file system implementation
    """
    protocol = fsspec.utils.get_protocol(path)
    fs = fsspec.filesystem(protocol)
    fs.protocol = protocol
    return fs


def list_dir(path: str) -> list[str]:
    """
    Return a list of the names of all files in a folder with protocol prefix

    Args:
        path: The path to list the contents of

    Returns:
        A list of the names of all files in the folder

    Examples:
        >>> list_dir("gs://my-bucket/my-folder")
        ['gs://my-bucket/my-folder/file1.txt', 'gs://my-bucket/my-folder/subdir']
    """
    fs = get_fs(path)
    return [f"{fs.protocol}://{p.strip('/')}" for p in fs.ls(path, detail=False)]


def exists_dir(path: str) -> bool:
    """
    Check if a directory exists

    Args:
        path: The path to check

    Returns:
        `True` if the directory exists, `False` otherwise

    Examples:
        >>> exists_dir("gs://my-bucket/my-folder")
        True
        >>> exists_dir("gs://my-bucket/my-folder/non-existent-subdir")
        False
    """
    fs = get_fs(path)
    return fs.exists(path)


def delete_dir(path: str) -> None:
    """
    Delete a directory and all its contents

    Args:
        path: The path to delete
    """
    fs = get_fs(path)
    fs.rm(path, recursive=True)


def upload_dir(local_source_path: str, remote_target_path: str, *, recursive: bool = False) -> None:
    """
    Upload a local folder to a remote bucket folder

    Args:
        local_source_path: The local path to upload
        remote_target_path: The remote path to upload to
        recursive: Whether to upload sub-folders as well

    Examples:
        >>> upload_dir("./temp/my-model", "gs://my-bucket/my-model")
    """
    fs = get_fs(remote_target_path)
    if recursive:
        # ensure trailing slash on source and target to upload the content of the whole source folder
        fs.upload(f"{local_source_path.rstrip('/')}/", f"{remote_target_path.rstrip('/')}/", recursive=True)
    else:
        # to upload only the direct source folder contents we need to ensure no trailing slash on source
        fs.upload(f"{local_source_path.rstrip('/')}/*", f"{remote_target_path.rstrip('/')}")


def download_dir(remote_source_path: str, local_target_path: str, *, recursive: bool = False) -> None:
    """
    Download a remote bucket folder to a local folder

    Args:
        remote_source_path: The remote path to download from
        local_target_path: The local path to download to
        recursive: Whether to download subfolders

    Examples:
        >>> download_dir("gs://my-bucket/my-model", "./temp/my-model")
    """
    fs = get_fs(remote_source_path)
    if recursive:
        # ensure trailing slash on source to download the content of the source folder
        fs.download(f"{remote_source_path.rstrip('/')}/", local_target_path.rstrip("/"), recursive=True)
    else:
        # to download only the direct source folder contents we need to ensure no trailing slash on source
        fs.download(f"{remote_source_path.rstrip('/')}/*", local_target_path.rstrip("/"))


def download_file(remote_source_path: str, local_target_path: str) -> None:
    """
    Download a remote file to a local file
    """
    fs = get_fs(remote_source_path)
    fs.download(remote_source_path, local_target_path)


@contextmanager
def dir_context(
    path: str, mode: Literal["read", "write", "read-write"], *, recursive: bool = False, create: bool = False
) -> Generator[str, None, None]:
    """Context manager for reading and writing to a possible blob storage directory"""
    if is_using_blob_storage(path):
        with TemporaryDirectory() as temp_dir:
            if "read" in mode:
                download_dir(path, temp_dir, recursive=recursive)
            yield temp_dir
            if "write" in mode:
                upload_dir(temp_dir, path, recursive=recursive)
    else:
        if create:
            os.makedirs(path, exist_ok=True)
        yield path
