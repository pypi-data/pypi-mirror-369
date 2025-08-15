# ruff: noqa: E501
import asyncio
import os
import shutil
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union

import oss2
from prefect._internal.compatibility.async_dispatch import async_dispatch
from prefect.blocks.abstract import CredentialsBlock, ObjectStorageBlock
from prefect.filesystems import WritableDeploymentStorage, WritableFileSystem
from prefect.logging import get_run_logger
from prefect.utilities.asyncutils import run_sync_in_worker_thread
from prefect.utilities.dispatch import register_type
from prefect.utilities.filesystem import filter_files
from pydantic import Field, SecretStr

from winwin.oss import OssFs


@lru_cache(maxsize=8, typed=True)
def get_oss_bucket(oss, bucket_name: str) -> oss2.Bucket:
    auth = oss2.Auth(
        oss.access_key_id,
        oss.access_key_secret.get_secret_value(),
    )
    return oss2.Bucket(auth, oss.endpoint_url, bucket_name)


class AliyunOssCredentials(CredentialsBlock):
    """
    Block used to manage Aliyun OSS credentials.
    Attributes:
        access_key: The access key ID for your account.
        secret_key: The secret access key for your account.
        region: The region where your bucket is located.
    """

    _block_type_name = "Aliyun Credentials"

    _description = "Aliyun credentials."

    access_key_id: str = Field(
        default=...,
        description="A specific Aliyun access key ID.",
        title="Aliyun Access Key ID",
    )

    access_key_secret: SecretStr = Field(
        default=...,
        description="A specific Aliyun secret access key.",
        title="Aliyun Access Key Secret",
    )

    region_name: Optional[str] = Field(
        default=None,
        description="The Aliyun Region where you want to create new connections.",
    )

    endpoint_url: Optional[str] = Field(
        default=None,
        description="The Aliyun endpoint to use.",
    )

    def __hash__(self):
        return hash(
            (
                self.access_key_id,
                self.access_key_secret.get_secret_value(),
                self.region_name,
                self.endpoint_url,
            )
        )

    def get_client(self, bucket_name: str):
        return get_oss_bucket(self, bucket_name)


class AliyunOss(WritableFileSystem, WritableDeploymentStorage, ObjectStorageBlock):
    """
    Block used to store data using AWS S3 or S3-compatible object storage like MinIO.

    Attributes:
        bucket_name: Name of your bucket.
        credentials: A block containing your credentials to AWS or MinIO.
        bucket_folder: A default path to a folder within the S3 bucket to use
            for reading and writing objects.
    """

    _logo_url = "https://icons.veryicon.com/png/o/miscellaneous/2022-complete-collection-of-alibaba-cloud/object-storage-oss-1.png"
    _block_type_name = "Aliyun OSS"
    _block_type_slug = "aliyun-oss"
    _documentation_url = "https://help.aliyun.com/zh/oss/getting-started/"

    bucket_name: str = Field(default=..., description="Name of your bucket.")
    bucket_folder: Optional[str] = Field(
        default=None,
        description="A default path to a folder within the OSS bucket to use.",
    )
    append_date_folder: bool = Field(
        default=False,
        description="Append current date as sub folder to the base path.",
    )
    credentials: AliyunOssCredentials = Field(
        default=...,
        description="A block containing your credentials to Aliyun.",
    )

    # Property to maintain compatibility with storage block based deployments
    @property
    def basepath(self) -> str:
        """
        The base path of the S3 bucket.

        Returns:
            str: The base path of the S3 bucket.
        """
        if self.append_date_folder:
            return f"{self.bucket_folder}/{self._today()}"
        return self.bucket_folder

    @basepath.setter
    def basepath(self, value: str) -> None:
        self.bucket_folder = value

    def _today(self):
        return datetime.now().strftime("%Y%m%d")

    def _resolve_path(self, path: str) -> str:
        """
        A helper function used in write_path to join `self.basepath` and `path`.

        Args:

            path: Name of the key, e.g. "file1". Each object in your
                bucket has a unique key (or key name).

        """
        # If bucket_folder provided, it means we won't write to the root dir of
        # the bucket. So we need to add it on the front of the path.
        #
        # AWS object key naming guidelines require '/' for bucket folders.
        # Get POSIX path to prevent `pathlib` from inferring '\' on Windows OS
        return (
            (Path(self.basepath) / path).as_posix()
            if self.bucket_folder or self.append_date_folder
            else path
        )

    def _get_bucket_resource(self) -> oss2.Bucket:
        """
        Authenticate MinIO credentials or AWS credentials and return an S3 client.
        This is a helper function called by read_path() or write_path().
        """
        return self.credentials.get_client(self.bucket_name)

    @property
    def fs(self):
        return OssFs(
            access_id=self.credentials.access_key_id,
            access_key=self.credentials.access_key_secret.get_secret_value(),
            endpoint=self.credentials.endpoint_url,
            bucket=self.bucket_name,
        )

    async def aget_directory(
        self, from_path: Optional[str] = None, local_path: Optional[str] = None
    ) -> None:
        """
        Asynchronously copies a folder from the configured S3 bucket to a local directory.

        Defaults to copying the entire contents of the block's basepath to the current
        working directory.

        Args:
            from_path: Path in S3 bucket to download from. Defaults to the block's
                configured basepath.
            local_path: Local path to download S3 contents to. Defaults to the current
                working directory.
        """
        bucket_folder = self.bucket_folder
        if from_path is None:
            from_path = str(bucket_folder) if bucket_folder else ""

        if local_path is None:
            local_path = str(Path("").absolute())
        else:
            local_path = str(Path(local_path).expanduser())

        bucket = self._get_bucket_resource()
        result = None
        while True:
            result = (
                bucket.list_objects(prefix=from_path)
                if result is None
                else bucket.list_objects(prefix=from_path, marker=result.next_marker)
            )
            for obj in result.object_list:
                if obj.key[-1] == "/":
                    # object is a folder and will be created if it contains any objects
                    continue
                target = os.path.join(
                    local_path,
                    os.path.relpath(obj.key, from_path),
                )
                os.makedirs(os.path.dirname(target), exist_ok=True)
                await run_sync_in_worker_thread(
                    bucket.get_object_to_file, obj.key, target
                )
            if not result.is_truncated:
                break

    @async_dispatch(aget_directory)
    def get_directory(
        self, from_path: Optional[str] = None, local_path: Optional[str] = None
    ) -> None:
        """
        Copies a folder from the configured S3 bucket to a local directory.

        Defaults to copying the entire contents of the block's basepath to the current
        working directory.

        Args:
            from_path: Path in S3 bucket to download from. Defaults to the block's
                configured basepath.
            local_path: Local path to download S3 contents to. Defaults to the current
                working directory.
        """
        bucket_folder = self.bucket_folder
        if from_path is None:
            from_path = str(bucket_folder) if bucket_folder else ""

        if local_path is None:
            local_path = str(Path("").absolute())
        else:
            local_path = str(Path(local_path).expanduser())

        bucket = self._get_bucket_resource()

        result = None
        while True:
            result = (
                bucket.list_objects(prefix=from_path)
                if result is None
                else bucket.list_objects(prefix=from_path, marker=result.next_marker)
            )
            for obj in result.object_list:
                if obj.key[-1] == "/":
                    # object is a folder and will be created if it contains any objects
                    continue
                target = os.path.join(
                    local_path,
                    os.path.relpath(obj.key, from_path),
                )
                os.makedirs(os.path.dirname(target), exist_ok=True)
                bucket.get_object_to_file(obj.key, target)
            if not result.is_truncated:
                break

    async def aput_directory(
        self,
        local_path: Optional[str] = None,
        to_path: Optional[str] = None,
        ignore_file: Optional[str] = None,
    ) -> int:
        """
        Asynchronously uploads a directory from a given local path to the configured S3 bucket in a
        given folder.

        Defaults to uploading the entire contents the current working directory to the
        block's basepath.

        Args:
            local_path: Path to local directory to upload from.
            to_path: Path in S3 bucket to upload to. Defaults to block's configured
                basepath.
            ignore_file: Path to file containing gitignore style expressions for
                filepaths to ignore.

        """
        to_path = "" if to_path is None else to_path

        if local_path is None:
            local_path = ""

        included_files = None
        if ignore_file:
            with open(ignore_file) as f:
                ignore_patterns = f.readlines()

            included_files = filter_files(local_path, ignore_patterns)

        uploaded_file_count = 0
        for local_file_path in Path(local_path).expanduser().rglob("*"):
            if (
                included_files is not None
                and str(local_file_path.relative_to(local_path)) not in included_files
            ):
                continue
            if not local_file_path.is_dir():
                remote_file_path = Path(to_path) / local_file_path.relative_to(
                    local_path
                )
                with open(local_file_path, "rb") as local_file:
                    local_file_content = local_file.read()

                await self.awrite_path(
                    remote_file_path.as_posix(), content=local_file_content
                )
                uploaded_file_count += 1

        return uploaded_file_count

    @async_dispatch(aput_directory)
    def put_directory(
        self,
        local_path: Optional[str] = None,
        to_path: Optional[str] = None,
        ignore_file: Optional[str] = None,
    ) -> int:
        """
        Uploads a directory from a given local path to the configured S3 bucket in a
        given folder.

        Defaults to uploading the entire contents the current working directory to the
        block's basepath.

        Args:
            local_path: Path to local directory to upload from.
            to_path: Path in S3 bucket to upload to. Defaults to block's configured
                basepath.
            ignore_file: Path to file containing gitignore style expressions for
                filepaths to ignore.

        """
        to_path = "" if to_path is None else to_path

        if local_path is None:
            local_path = ""

        included_files = None
        if ignore_file:
            with open(ignore_file) as f:
                ignore_patterns = f.readlines()

            included_files = filter_files(local_path, ignore_patterns)

        uploaded_file_count = 0
        for local_file_path in Path(local_path).expanduser().rglob("*"):
            if (
                included_files is not None
                and str(local_file_path.relative_to(local_path)) not in included_files
            ):
                continue
            if not local_file_path.is_dir():
                remote_file_path = Path(to_path) / local_file_path.relative_to(
                    local_path
                )
                with open(local_file_path, "rb") as local_file:
                    local_file_content = local_file.read()

                self.write_path(
                    remote_file_path.as_posix(), content=local_file_content, _sync=True
                )
                uploaded_file_count += 1

        return uploaded_file_count

    def _read_sync(self, key: str) -> bytes:
        """
        Called by read_path(). Creates an S3 client and retrieves the
        contents from  a specified path.
        """
        return self._get_bucket_resource().get_object(key).read()

    async def aread_path(self, path: str) -> bytes:
        """
        Asynchronously reads the contents of a specified path from the S3 bucket.
        Provide the entire path to the key in S3.

        Args:
            path: Entire path to (and including) the key.

        Example:
            Read "subfolder/file1" contents from an S3 bucket named "bucket":
            ```python
            from prefect_aws import AwsCredentials
            from prefect_aws.s3 import S3Bucket

            aws_creds = AwsCredentials(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )

            s3_bucket_block = S3Bucket(
                bucket_name="bucket",
                credentials=aws_creds,
                bucket_folder="subfolder"
            )

            key_contents = await s3_bucket_block.aread_path(path="subfolder/file1")
            ```
        """
        path = self._resolve_path(path)
        return await run_sync_in_worker_thread(self._read_sync, path)

    @async_dispatch(aread_path)
    def read_path(self, path: str) -> bytes:
        """
        Read specified path from S3 and return contents. Provide the entire
        path to the key in S3.

        Args:
            path: Entire path to (and including) the key.

        Example:
            Read "subfolder/file1" contents from an S3 bucket named "bucket":
            ```python
            from prefect_aws import AwsCredentials
            from prefect_aws.s3 import S3Bucket

            aws_creds = AwsCredentials(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )

            s3_bucket_block = S3Bucket(
                bucket_name="bucket",
                credentials=aws_creds,
                bucket_folder="subfolder"
            )

            key_contents = s3_bucket_block.read_path(path="subfolder/file1")
            ```
        """
        path = self._resolve_path(path)

        return self._read_sync(path)

    def _write_sync(self, key: str, data: bytes) -> None:
        """
        Called by write_path(). Creates an S3 client and uploads a file
        object.
        """
        get_run_logger().info(f"Writing to oss oss://{self.bucket_name}/{key}")
        self._get_bucket_resource().put_object(key, data)

    async def awrite_path(self, path: str, content: bytes) -> str:
        """
        Asynchronously writes to an S3 bucket.

        Args:

            path: The key name. Each object in your bucket has a unique
                key (or key name).
            content: What you are uploading to S3.

        Example:

            Write data to the path `dogs/small_dogs/havanese` in an S3 Bucket:
            ```python
            from prefect_aws import MinioCredentials
            from prefect_aws.s3 import S3Bucket

            minio_creds = MinIOCredentials(
                minio_root_user = "minioadmin",
                minio_root_password = "minioadmin",
            )

            s3_bucket_block = S3Bucket(
                bucket_name="bucket",
                minio_credentials=minio_creds,
                bucket_folder="dogs/smalldogs",
                endpoint_url="http://localhost:9000",
            )
            s3_havanese_path = await s3_bucket_block.awrite_path(path="havanese", content=data)
            ```
        """

        path = self._resolve_path(path)

        await run_sync_in_worker_thread(self._write_sync, path, content)

        return path

    @async_dispatch(awrite_path)
    def write_path(self, path: str, content: bytes) -> str:
        """
        Writes to an S3 bucket.

        Args:

            path: The key name. Each object in your bucket has a unique
                key (or key name).
            content: What you are uploading to S3.

        Example:

            Write data to the path `dogs/small_dogs/havanese` in an S3 Bucket:
            ```python
            from prefect_aws import MinioCredentials
            from prefect_aws.s3 import S3Bucket

            minio_creds = MinIOCredentials(
                minio_root_user = "minioadmin",
                minio_root_password = "minioadmin",
            )

            s3_bucket_block = S3Bucket(
                bucket_name="bucket",
                minio_credentials=minio_creds,
                bucket_folder="dogs/smalldogs",
                endpoint_url="http://localhost:9000",
            )
            s3_havanese_path = s3_bucket_block.write_path(path="havanese", content=data)
            ```
        """

        path = self._resolve_path(path)

        self._write_sync(path, content)

        return path

    def _join_bucket_folder(self, bucket_path: str = "") -> str:
        """
        Joins the base bucket folder to the bucket path.
        NOTE: If a method reuses another method in this class, be careful to not
        call this  twice because it'll join the bucket folder twice.
        See https://github.com/PrefectHQ/prefect-aws/issues/141 for a past issue.
        """
        if not self.bucket_folder and not bucket_path:
            # there's a difference between "." and "", at least in the tests
            return ""

        bucket_path = str(bucket_path)
        if self.bucket_folder != "" and bucket_path.startswith(self.bucket_folder):
            self.logger.info(
                f"Bucket path {bucket_path!r} is already prefixed with "
                f"bucket folder {self.bucket_folder!r}; is this intentional?"
            )

        return (Path(self.bucket_folder) / bucket_path).as_posix() + (
            "" if not bucket_path.endswith("/") else "/"
        )

    async def alist_objects(
        self,
        folder: str = "",
        delimiter: str = "",
        page_size: Optional[int] = None,
        max_items: Optional[int] = None,
        jmespath_query: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Asynchronously lists objects in the S3 bucket.

        Args:
            folder: Folder to list objects from.
            delimiter: Character used to group keys of listed objects.
            page_size: Number of objects to return in each request to the AWS API.
            max_items: Maximum number of objects that to be returned by task.
            jmespath_query: Query used to filter objects based on object attributes refer to
                the [boto3 docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html#filtering-results-with-jmespath)
                for more information on how to construct queries.

        Returns:
            List of objects and their metadata in the bucket.

        Examples:
            List objects under the `base_folder`.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            await s3_bucket.alist_objects("base_folder")
            ```
        """
        return await run_sync_in_worker_thread(
            self.list_objects,
            folder=folder,
            delimiter=delimiter,
            page_size=page_size,
            max_items=max_items,
            jmespath_query=jmespath_query,
        )

    @async_dispatch(alist_objects)
    def list_objects(
        self,
        folder: str = "",
        delimiter: str = "",
        page_size: Optional[int] = None,
        max_items: Optional[int] = None,
        jmespath_query: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Args:
            folder: Folder to list objects from.
            delimiter: Character used to group keys of listed objects.
            page_size: Number of objects to return in each request to the AWS API.
            max_items: Maximum number of objects that to be returned by task.
            jmespath_query: Query used to filter objects based on object attributes refer to
                the [boto3 docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html#filtering-results-with-jmespath)
                for more information on how to construct queries.

        Returns:
            List of objects and their metadata in the bucket.

        Examples:
            List objects under the `base_folder`.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.list_objects("base_folder")
            ```
        """
        result = None
        objects = []
        bucket = self._get_bucket_resource()
        while True:
            result = bucket.list_objects(
                prefix=self._join_bucket_folder(folder),
                delimiter=delimiter,
                page_size=page_size,
                max_keys=max_items,
                next_marker=result.next_marker if result else None,
            )
            for obj in result.object_list:
                objects.append(
                    {
                        "Key": obj.key,
                        "LastModified": obj.last_modified,
                        "Size": obj.size,
                        "ETag": obj.etag,
                        "StorageClass": obj.storage_class,
                    }
                )
            if not result.is_truncated:
                break
        return objects

    async def adownload_object_to_path(
        self,
        from_path: str,
        to_path: Optional[Union[str, Path]],
        **download_kwargs: dict[str, Any],
    ) -> Path:
        """
        Asynchronously downloads an object from the S3 bucket to a path.

        Args:
            from_path: The path to the object to download; this gets prefixed
                with the bucket_folder.
            to_path: The path to download the object to. If not provided, the
                object's name will be used.
            **download_kwargs: Additional keyword arguments to pass to
                `Client.download_file`.

        Returns:
            The absolute path that the object was downloaded to.

        Examples:
            Download my_folder/notes.txt object to notes.txt.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            await s3_bucket.adownload_object_to_path("my_folder/notes.txt", "notes.txt")
            ```
        """
        if to_path is None:
            to_path = Path(from_path).name

        # making path absolute, but converting back to str here
        # since !r looks nicer that way and filename arg expects str
        to_path = str(Path(to_path).absolute())
        bucket_path = self._join_bucket_folder(from_path)
        bucket = self._get_bucket_resource()

        self.logger.debug(
            f"Preparing to download object from bucket {self.bucket_name!r} "
            f"path {bucket_path!r} to {to_path!r}."
        )
        await run_sync_in_worker_thread(
            bucket.get_object_to_file,
            bucket_path,
            to_path,
            **download_kwargs,
        )
        self.logger.info(
            f"Downloaded object from bucket {self.bucket_name!r} path {bucket_path!r} "
            f"to {to_path!r}."
        )
        return Path(to_path)

    @async_dispatch(adownload_object_to_path)
    def download_object_to_path(
        self,
        from_path: str,
        to_path: Optional[Union[str, Path]],
        **download_kwargs: dict[str, Any],
    ) -> Path:
        """
        Downloads an object from the S3 bucket to a path.

        Args:
            from_path: The path to the object to download; this gets prefixed
                with the bucket_folder.
            to_path: The path to download the object to. If not provided, the
                object's name will be used.
            **download_kwargs: Additional keyword arguments to pass to
                `Client.download_file`.

        Returns:
            The absolute path that the object was downloaded to.

        Examples:
            Download my_folder/notes.txt object to notes.txt.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.download_object_to_path("my_folder/notes.txt", "notes.txt")
            ```
        """
        if to_path is None:
            to_path = Path(from_path).name

        # making path absolute, but converting back to str here
        # since !r looks nicer that way and filename arg expects str
        to_path = str(Path(to_path).absolute())
        bucket_path = self._join_bucket_folder(from_path)
        bucket = self._get_bucket_resource()

        self.logger.debug(
            f"Preparing to download object from bucket {self.bucket_name!r} "
            f"path {bucket_path!r} to {to_path!r}."
        )
        bucket.get_object_to_file(bucket_path, to_path, **download_kwargs)
        self.logger.info(
            f"Downloaded object from bucket {self.bucket_name!r} path {bucket_path!r} "
            f"to {to_path!r}."
        )
        return Path(to_path)

    async def adownload_object_to_file_object(
        self,
        from_path: str,
        to_file_object: BinaryIO,
        **download_kwargs: dict[str, Any],
    ) -> BinaryIO:
        """
        Asynchronously downloads an object from the object storage service to a file-like object,
        which can be a BytesIO object or a BufferedWriter.

        Args:
            from_path: The path to the object to download from; this gets prefixed
                with the bucket_folder.
            to_file_object: The file-like object to download the object to.
            **download_kwargs: Additional keyword arguments to pass to
                `Client.download_fileobj`.

        Returns:
            The file-like object that the object was downloaded to.

        Examples:
            Download my_folder/notes.txt object to a BytesIO object.
            ```python
            from io import BytesIO

            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with BytesIO() as buf:
                await s3_bucket.adownload_object_to_file_object("my_folder/notes.txt", buf)
            ```

            Download my_folder/notes.txt object to a BufferedWriter.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with open("notes.txt", "wb") as f:
                await s3_bucket.adownload_object_to_file_object("my_folder/notes.txt", f)
            ```
        """
        return await run_sync_in_worker_thread(
            self.download_object_to_file_object,
            from_path=from_path,
            to_file_object=to_file_object,
            **download_kwargs,
        )

    @async_dispatch(adownload_object_to_file_object)
    def download_object_to_file_object(
        self,
        from_path: str,
        to_file_object: BinaryIO,
        **download_kwargs: dict[str, Any],
    ) -> BinaryIO:
        """
        Downloads an object from the object storage service to a file-like object,
        which can be a BytesIO object or a BufferedWriter.

        Args:
            from_path: The path to the object to download from; this gets prefixed
                with the bucket_folder.
            to_file_object: The file-like object to download the object to.
            **download_kwargs: Additional keyword arguments to pass to
                `Client.download_fileobj`.

        Returns:
            The file-like object that the object was downloaded to.

        Examples:
            Download my_folder/notes.txt object to a BytesIO object.
            ```python
            from io import BytesIO

            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with BytesIO() as buf:
                s3_bucket.download_object_to_file_object("my_folder/notes.txt", buf)
            ```

            Download my_folder/notes.txt object to a BufferedWriter.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with open("notes.txt", "wb") as f:
                s3_bucket.download_object_to_file_object("my_folder/notes.txt", f)
            ```
        """
        bucket_path = self._join_bucket_folder(from_path)

        self.logger.debug(
            f"Preparing to download object from bucket {self.bucket_name!r} "
            f"path {bucket_path!r} to file object."
        )

        result = self._get_bucket_resource().get_object(bucket_path, **download_kwargs)
        shutil.copyfileobj(result, to_file_object)

        self.logger.info(
            f"Downloaded object from bucket {self.bucket_name!r} path {bucket_path!r} "
            "to file object."
        )
        return to_file_object

    async def adownload_folder_to_path(
        self,
        from_folder: str,
        to_folder: Optional[Union[str, Path]] = None,
        **download_kwargs: dict[str, Any],
    ) -> Path:
        """
        Asynchronously downloads objects *within* a folder (excluding the folder itself)
        from the S3 bucket to a folder.

        Args:
            from_folder: The path to the folder to download from.
            to_folder: The path to download the folder to.
            **download_kwargs: Additional keyword arguments to pass to
                `Client.download_file`.

        Returns:
            The absolute path that the folder was downloaded to.

        Examples:
            Download my_folder to a local folder named my_folder.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            await s3_bucket.adownload_folder_to_path("my_folder", "my_folder")
            ```
        """
        if to_folder is None:
            to_folder = ""
        to_folder = Path(to_folder).absolute()

        objects = await self.list_objects(folder=from_folder)

        # do not call self._join_bucket_folder for filter
        # because it's built-in to that method already!
        # however, we still need to do it because we're using relative_to
        bucket_folder = self._join_bucket_folder(from_folder)
        bucket = self._get_bucket_resource()

        async_coros = []
        for object in objects:
            bucket_path = Path(object["Key"]).relative_to(bucket_folder)
            # this skips the actual directory itself, e.g.
            # `my_folder/` will be skipped
            # `my_folder/notes.txt` will be downloaded
            if bucket_path.is_dir():
                continue
            to_path = to_folder / bucket_path
            to_path.parent.mkdir(parents=True, exist_ok=True)
            to_path = str(to_path)  # must be string
            self.logger.info(
                f"Downloading object from bucket {self.bucket_name!r} path "
                f"{bucket_path.as_posix()!r} to {to_path!r}."
            )
            async_coros.append(
                run_sync_in_worker_thread(
                    bucket.get_object_to_file,
                    object["Key"],
                    to_path,
                    **download_kwargs,
                )
            )
        await asyncio.gather(*async_coros)

        return Path(to_folder)

    @async_dispatch(adownload_folder_to_path)
    def download_folder_to_path(
        self,
        from_folder: str,
        to_folder: Optional[Union[str, Path]] = None,
        **download_kwargs: dict[str, Any],
    ) -> Path:
        """
        Downloads objects *within* a folder (excluding the folder itself)
        from the S3 bucket to a folder.
        Changed in version 0.6.0.

        Args:
            from_folder: The path to the folder to download from.
            to_folder: The path to download the folder to.
            **download_kwargs: Additional keyword arguments to pass to
                `Client.download_file`.

        Returns:
            The absolute path that the folder was downloaded to.

        Examples:
            Download my_folder to a local folder named my_folder.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.download_folder_to_path("my_folder", "my_folder")
            ```
        """
        if to_folder is None:
            to_folder = ""
        to_folder = Path(to_folder).absolute()

        bucket = self._get_bucket_resource()
        objects = self.list_objects(folder=from_folder)

        # do not call self._join_bucket_folder for filter
        # because it's built-in to that method already!
        # however, we still need to do it because we're using relative_to
        bucket_folder = self._join_bucket_folder(from_folder)

        assert isinstance(objects, list), "list of objects expected"
        for object in objects:
            bucket_path = Path(object["Key"]).relative_to(bucket_folder)
            # this skips the actual directory itself, e.g.
            # `my_folder/` will be skipped
            # `my_folder/notes.txt` will be downloaded
            if bucket_path.is_dir():
                continue
            to_path = to_folder / bucket_path
            to_path.parent.mkdir(parents=True, exist_ok=True)
            to_path = str(to_path)  # must be string
            self.logger.info(
                f"Downloading object from bucket {self.bucket_name!r} path "
                f"{bucket_path.as_posix()!r} to {to_path!r}."
            )
            bucket.get_object_to_file(
                object["Key"],
                to_path,
                **download_kwargs,
            )

        return Path(to_folder)

    async def astream_from(
        self,
        bucket: "AliyunOss",
        from_path: str,
        to_path: Optional[str] = None,
        **upload_kwargs: dict[str, Any],
    ) -> str:
        """Asynchronously streams an object from another bucket to this bucket. Requires the
        object to be downloaded and uploaded in chunks. If `self`'s credentials
        allow for writes to the other bucket, try using `S3Bucket.copy_object`.
        Added in version 0.5.3.

        Args:
            bucket: The bucket to stream from.
            from_path: The path of the object to stream.
            to_path: The path to stream the object to. Defaults to the object's name.
            **upload_kwargs: Additional keyword arguments to pass to
                `Client.upload_fileobj`.

        Returns:
            The path that the object was uploaded to.

        Examples:
            Stream notes.txt from your-bucket/notes.txt to my-bucket/landed/notes.txt.

            ```python
            from prefect_aws.s3 import S3Bucket

            your_s3_bucket = S3Bucket.load("your-bucket")
            my_s3_bucket = S3Bucket.load("my-bucket")

            await my_s3_bucket.astream_from(
                your_s3_bucket,
                "notes.txt",
                to_path="landed/notes.txt"
            )
            ```

        """
        if to_path is None:
            to_path = Path(from_path).name

        # Get the source object's StreamingBody
        _from_path: str = bucket._join_bucket_folder(from_path)
        from_client = bucket.credentials.get_s3_client()
        obj = await run_sync_in_worker_thread(
            from_client.get_object, Bucket=bucket.bucket_name, Key=_from_path
        )
        body = obj["Body"]

        # Upload the StreamingBody to this bucket
        bucket_path = str(self._join_bucket_folder(to_path))
        to_client = self.credentials.get_s3_client()
        await run_sync_in_worker_thread(
            to_client.upload_fileobj,
            Fileobj=body,
            Bucket=self.bucket_name,
            Key=bucket_path,
            **upload_kwargs,
        )
        self.logger.info(
            f"Streamed s3://{bucket.bucket_name}/{_from_path} to the bucket "
            f"{self.bucket_name!r} path {bucket_path!r}."
        )
        return bucket_path

    @async_dispatch(astream_from)
    def stream_from(
        self,
        bucket: "AliyunOss",
        from_path: str,
        to_path: Optional[str] = None,
        **upload_kwargs: dict[str, Any],
    ) -> str:
        """Streams an object from another bucket to this bucket. Requires the
        object to be downloaded and uploaded in chunks. If `self`'s credentials
        allow for writes to the other bucket, try using `S3Bucket.copy_object`.

        Args:
            bucket: The bucket to stream from.
            from_path: The path of the object to stream.
            to_path: The path to stream the object to. Defaults to the object's name.
            **upload_kwargs: Additional keyword arguments to pass to
                `Client.upload_fileobj`.

        Returns:
            The path that the object was uploaded to.

        Examples:
            Stream notes.txt from your-bucket/notes.txt to my-bucket/landed/notes.txt.

            ```python
            from prefect_aws.s3 import S3Bucket

            your_s3_bucket = S3Bucket.load("your-bucket")
            my_s3_bucket = S3Bucket.load("my-bucket")

            my_s3_bucket.stream_from(
                your_s3_bucket,
                "notes.txt",
                to_path="landed/notes.txt"
            )
            ```

        """
        if to_path is None:
            to_path = Path(from_path).name

        # Get the source object's StreamingBody
        _from_path: str = bucket._join_bucket_folder(from_path)
        from_client = bucket.credentials.get_s3_client()
        obj = from_client.get_object(Bucket=bucket.bucket_name, Key=_from_path)
        body = obj["Body"]

        # Upload the StreamingBody to this bucket
        bucket_path = str(self._join_bucket_folder(to_path))
        to_client = self.credentials.get_s3_client()
        to_client.upload_fileobj(
            Fileobj=body,
            Bucket=self.bucket_name,
            Key=bucket_path,
            **upload_kwargs,
        )
        self.logger.info(
            f"Streamed s3://{bucket.bucket_name}/{_from_path} to the bucket "
            f"{self.bucket_name!r} path {bucket_path!r}."
        )
        return bucket_path

    async def aupload_from_path(
        self,
        from_path: Union[str, Path],
        to_path: Optional[str] = None,
        **upload_kwargs: dict[str, Any],
    ) -> str:
        """
        Asynchronously uploads an object from a path to the S3 bucket.
        Added in version 0.5.3.

        Args:
            from_path: The path to the file to upload from.
            to_path: The path to upload the file to.
            **upload_kwargs: Additional keyword arguments to pass to `Client.upload`.

        Returns:
            The path that the object was uploaded to.

        Examples:
            Upload notes.txt to my_folder/notes.txt.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            await s3_bucket.aupload_from_path("notes.txt", "my_folder/notes.txt")
            ```
        """
        from_path = str(Path(from_path).absolute())
        if to_path is None:
            to_path = Path(from_path).name

        bucket_path = str(self._join_bucket_folder(to_path))
        bucket = self._get_bucket_resource()

        await run_sync_in_worker_thread(
            bucket.put_object_from_file,
            bucket_path,
            **upload_kwargs,
        )
        self.logger.info(
            f"Uploaded from {from_path!r} to the bucket "
            f"{self.bucket_name!r} path {bucket_path!r}."
        )
        return bucket_path

    @async_dispatch(aupload_from_path)
    def upload_from_path(
        self,
        from_path: Union[str, Path],
        to_path: Optional[str] = None,
        **upload_kwargs: dict[str, Any],
    ) -> str:
        """
        Uploads an object from a path to the S3 bucket.

        Args:
            from_path: The path to the file to upload from.
            to_path: The path to upload the file to.
            **upload_kwargs: Additional keyword arguments to pass to `Client.upload`.

        Returns:
            The path that the object was uploaded to.

        Examples:
            Upload notes.txt to my_folder/notes.txt.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.upload_from_path("notes.txt", "my_folder/notes.txt")
            ```
        """
        from_path = str(Path(from_path).absolute())
        if to_path is None:
            to_path = Path(from_path).name

        bucket_path = str(self._join_bucket_folder(to_path))

        self._get_bucket_resource().put_object_from_file(
            bucket_path,
            from_path,
            **upload_kwargs,
        )
        self.logger.info(
            f"Uploaded from {from_path!r} to the bucket "
            f"{self.bucket_name!r} path {bucket_path!r}."
        )
        return bucket_path

    async def aupload_from_file_object(
        self, from_file_object: BinaryIO, to_path: str, **upload_kwargs: dict[str, Any]
    ) -> str:
        """
        Asynchronously uploads an object to the S3 bucket from a file-like object,
        which can be a BytesIO object or a BufferedReader.

        Args:
            from_file_object: The file-like object to upload from.
            to_path: The path to upload the object to.
            **upload_kwargs: Additional keyword arguments to pass to
                `Client.upload_fileobj`.

        Returns:
            The path that the object was uploaded to.

        Examples:
            Upload BytesIO object to my_folder/notes.txt.
            ```python
            from io import BytesIO

            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with open("notes.txt", "rb") as f:
                await s3_bucket.aupload_from_file_object(f, "my_folder/notes.txt")
            ```

            Upload BufferedReader object to my_folder/notes.txt.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with open("notes.txt", "rb") as f:
                s3_bucket.upload_from_file_object(
                    f, "my_folder/notes.txt"
                )
            ```
        """
        bucket_path = str(self._join_bucket_folder(to_path))
        bucket = self._get_bucket_resource()
        await run_sync_in_worker_thread(
            bucket.put_object,
            bucket_path,
            from_file_object,
            **upload_kwargs,
        )
        self.logger.info(
            "Uploaded from file object to the bucket "
            f"{self.bucket_name!r} path {bucket_path!r}."
        )
        return bucket_path

    @async_dispatch(aupload_from_file_object)
    def upload_from_file_object(
        self, from_file_object: BinaryIO, to_path: str, **upload_kwargs: dict[str, Any]
    ) -> str:
        """
        Uploads an object to the S3 bucket from a file-like object,
        which can be a BytesIO object or a BufferedReader.

        Args:
            from_file_object: The file-like object to upload from.
            to_path: The path to upload the object to.
            **upload_kwargs: Additional keyword arguments to pass to
                `Client.upload_fileobj`.

        Returns:
            The path that the object was uploaded to.

        Examples:
            Upload BytesIO object to my_folder/notes.txt.
            ```python
            from io import BytesIO

            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with open("notes.txt", "rb") as f:
                s3_bucket.upload_from_file_object(f, "my_folder/notes.txt")
            ```

            Upload BufferedReader object to my_folder/notes.txt.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            with open("notes.txt", "rb") as f:
                s3_bucket.upload_from_file_object(
                    f, "my_folder/notes.txt"
                )
            ```
        """
        bucket_path = str(self._join_bucket_folder(to_path))
        client = self._get_bucket_resource()
        client.put_object(bucket_path, from_file_object, **upload_kwargs)
        self.logger.info(
            "Uploaded from file object to the bucket "
            f"{self.bucket_name!r} path {bucket_path!r}."
        )
        return bucket_path

    async def aupload_from_folder(
        self,
        from_folder: Union[str, Path],
        to_folder: Optional[str] = None,
        **upload_kwargs: dict[str, Any],
    ) -> Union[str, None]:
        """
        Asynchronously uploads files *within* a folder (excluding the folder itself)
        to the object storage service folder. Added in version prefect-aws==0.5.3.

        Args:
            from_folder: The path to the folder to upload from.
            to_folder: The path to upload the folder to.
            **upload_kwargs: Additional keyword arguments to pass to
                `Client.upload_fileobj`.

        Returns:
            The path that the folder was uploaded to.

        Examples:
            Upload contents from my_folder to new_folder.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            await s3_bucket.aupload_from_folder("my_folder", "new_folder")
            ```
        """
        from_folder = Path(from_folder)
        bucket_folder = self._join_bucket_folder(to_folder or "")

        num_uploaded = 0
        client = self._get_bucket_resource()

        async_coros = []
        for from_path in from_folder.rglob("**/*"):
            # this skips the actual directory itself, e.g.
            # `my_folder/` will be skipped
            # `my_folder/notes.txt` will be uploaded
            if from_path.is_dir():
                continue
            bucket_path = (
                Path(bucket_folder) / from_path.relative_to(from_folder)
            ).as_posix()
            self.logger.info(
                f"Uploading from {str(from_path)!r} to the bucket "
                f"{self.bucket_name!r} path {bucket_path!r}."
            )
            async_coros.append(
                run_sync_in_worker_thread(
                    client.put_object,
                    bucket_path,
                    str(from_path),
                    **upload_kwargs,
                )
            )
            num_uploaded += 1
        await asyncio.gather(*async_coros)

        if num_uploaded == 0:
            self.logger.warning(f"No files were uploaded from {str(from_folder)!r}.")
        else:
            self.logger.info(
                f"Uploaded {num_uploaded} files from {str(from_folder)!r} to "
                f"the bucket {self.bucket_name!r} path {bucket_path!r}"
            )

        return to_folder

    @async_dispatch(aupload_from_folder)
    def upload_from_folder(
        self,
        from_folder: Union[str, Path],
        to_folder: Optional[str] = None,
        **upload_kwargs: dict[str, Any],
    ) -> Union[str, None]:
        """
        Uploads files *within* a folder (excluding the folder itself)
        to the object storage service folder.

        Args:
            from_folder: The path to the folder to upload from.
            to_folder: The path to upload the folder to.
            **upload_kwargs: Additional keyword arguments to pass to
                `Client.upload_fileobj`.

        Returns:
            The path that the folder was uploaded to.

        Examples:
            Upload contents from my_folder to new_folder.
            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.upload_from_folder("my_folder", "new_folder")
            ```
        """
        from_folder = Path(from_folder)
        bucket_folder = self._join_bucket_folder(to_folder or "")

        num_uploaded = 0
        client = self._get_bucket_resource()

        for from_path in from_folder.rglob("**/*"):
            # this skips the actual directory itself, e.g.
            # `my_folder/` will be skipped
            # `my_folder/notes.txt` will be uploaded
            if from_path.is_dir():
                continue
            bucket_path = (
                Path(bucket_folder) / from_path.relative_to(from_folder)
            ).as_posix()
            self.logger.info(
                f"Uploading from {str(from_path)!r} to the bucket "
                f"{self.bucket_name!r} path {bucket_path!r}."
            )
            client.put_object(bucket_path, str(from_path), **upload_kwargs)
            num_uploaded += 1

        if num_uploaded == 0:
            self.logger.warning(f"No files were uploaded from {str(from_folder)!r}.")
        else:
            self.logger.info(
                f"Uploaded {num_uploaded} files from {str(from_folder)!r} to "
                f"the bucket {self.bucket_name!r} path {bucket_path!r}"
            )

        return to_folder

    def copy_object(
        self,
        from_path: Union[str, Path],
        to_path: Union[str, Path],
        to_bucket: Optional[Union["AliyunOss", str]] = None,
        **copy_kwargs,
    ) -> str:
        """Uses S3's internal
        [CopyObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CopyObject.html)
        to copy objects within or between buckets. To copy objects between buckets,
        `self`'s credentials must have permission to read the source object and write
        to the target object. If the credentials do not have those permissions, try
        using `S3Bucket.stream_from`.

        Args:
            from_path: The path of the object to copy.
            to_path: The path to copy the object to.
            to_bucket: The bucket to copy to. Defaults to the current bucket.
            **copy_kwargs: Additional keyword arguments to pass to
                `S3Client.copy_object`.

        Returns:
            The path that the object was copied to. Excludes the bucket name.

        Examples:

            Copy notes.txt from my_folder/notes.txt to my_folder/notes_copy.txt.

            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.copy_object("my_folder/notes.txt", "my_folder/notes_copy.txt")
            ```

            Copy notes.txt from my_folder/notes.txt to my_folder/notes_copy.txt in
            another bucket.

            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.copy_object(
                "my_folder/notes.txt",
                "my_folder/notes_copy.txt",
                to_bucket="other-bucket"
            )
            ```
        """

        source_bucket_name = self.bucket_name
        source_path = self._resolve_path(Path(from_path).as_posix())

        # Default to copying within the same bucket
        to_bucket = to_bucket or self
        target_bucket_name = None

        target_path: str
        if isinstance(to_bucket, AliyunOss):
            to_bucket = to_bucket._get_bucket_resource()
            target_bucket_name = to_bucket.bucket_name
            target_path = to_bucket._resolve_path(Path(to_path).as_posix())
        elif isinstance(to_bucket, str):
            to_bucket = self.credentials.get_client(to_bucket)
            target_bucket_name = to_bucket
            target_path = Path(to_path).as_posix()
        else:
            raise TypeError(
                f"to_bucket must be a string or AliyunOss, not {type(to_bucket)}"
            )

        self.logger.info(
            "Copying object from bucket %s with key %s to bucket %s with key %s",
            source_bucket_name,
            source_path,
            target_bucket_name,
            target_path,
        )
        # fix target bucket

        to_bucket.copy_object(
            source_bucket_name, source_path, target_path, **copy_kwargs
        )

        return target_path

    async def amove_object(
        self,
        from_path: Union[str, Path],
        to_path: Union[str, Path],
        to_bucket: Optional[Union["AliyunOss", str]] = None,
    ) -> str:
        """Asynchronously uses S3's internal CopyObject and DeleteObject to move objects
        within or between buckets. To move objects between buckets, `self`'s credentials
        must have permission to read and delete the source object and write to the target
        object. If the credentials do not have those permissions, this method will raise
        an error. If the credentials have permission to read the source object but not
        delete it, the object will be copied but not deleted.

        Args:
            from_path: The path of the object to move.
            to_path: The path to move the object to.
            to_bucket: The bucket to move to. Defaults to the current bucket.

        Returns:
            The path that the object was moved to. Excludes the bucket name.

        Examples:

            Move notes.txt from my_folder/notes.txt to my_folder/notes_copy.txt.

            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            await s3_bucket.amove_object("my_folder/notes.txt", "my_folder/notes_copy.txt")
            ```

            Move notes.txt from my_folder/notes.txt to my_folder/notes_copy.txt in
            another bucket.

            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            await s3_bucket.amove_object(
                "my_folder/notes.txt",
                "my_folder/notes_copy.txt",
                to_bucket="other-bucket"
            )
            ```
        """
        return await run_sync_in_worker_thread(
            self.move_object,
            from_path,
            to_path,
            to_bucket,
        )

    @async_dispatch(amove_object)
    def move_object(
        self,
        from_path: Union[str, Path],
        to_path: Union[str, Path],
        to_bucket: Optional[Union["AliyunOss", str]] = None,
    ) -> str:
        """Uses S3's internal CopyObject and DeleteObject to move objects within or
        between buckets. To move objects between buckets, `self`'s credentials must
        have permission to read and delete the source object and write to the target
        object. If the credentials do not have those permissions, this method will raise
        an error. If the credentials have permission to read the source object but not
        delete it, the object will be copied but not deleted.

        Args:
            from_path: The path of the object to move.
            to_path: The path to move the object to.
            to_bucket: The bucket to move to. Defaults to the current bucket.

        Returns:
            The path that the object was moved to. Excludes the bucket name.

        Examples:

            Move notes.txt from my_folder/notes.txt to my_folder/notes_copy.txt.

            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.move_object("my_folder/notes.txt", "my_folder/notes_copy.txt")
            ```

            Move notes.txt from my_folder/notes.txt to my_folder/notes_copy.txt in
            another bucket.

            ```python
            from prefect_aws.s3 import S3Bucket

            s3_bucket = S3Bucket.load("my-bucket")
            s3_bucket.move_object(
                "my_folder/notes.txt",
                "my_folder/notes_copy.txt",
                to_bucket="other-bucket"
            )
            ```
        """
        target_path = self.copy_object(from_path, to_path, to_bucket=to_bucket)
        self._get_bucket_resource().delete_object(
            self._resolve_path(Path(from_path).as_posix())
        )
        return target_path


register_type(AliyunOss)
