import warnings
from typing import Optional, Union
from urllib.parse import urlparse

import oss2
import ossfs


class OssUri:
    def __init__(self, bucket: str, path: str):
        self.bucket = bucket
        self.path = path.lstrip("/")

    def __str__(self):
        return f"oss://{self.bucket}/{self.path}"

    @classmethod
    def from_path(cls, path: str, bucket: Optional[str] = None):
        if path.startswith("oss://"):
            result = urlparse(path)
            return cls(result.netloc, result.path)
        return cls(bucket, path)

    @property
    def full_path(self):
        return f"/{self.bucket}/{self.path}"


class OssFs:
    def __init__(self, access_id: str, access_key: str, endpoint: str, bucket: str):
        self._access_id = access_id
        self._access_key = access_key
        self._endpoint = endpoint
        self._bucket_name = bucket
        self._bucket = None
        self.fs = ossfs.OSSFileSystem(
            endpoint=self._endpoint,
            key=self._access_id,
            secret=self._access_key,
        )

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def external_endpoint(self) -> str:
        return self._endpoint.replace("-internal.aliyuncs.com", ".aliyuncs.com")

    @property
    def bucket(self) -> oss2.Bucket:
        if not self._bucket:
            self._bucket = self.bucket_for(self._bucket_name)
        return self._bucket

    def bucket_for(self, bucket_name: str, external: bool = False) -> oss2.Bucket:
        auth = oss2.Auth(self._access_id, self._access_key)
        return oss2.Bucket(
            auth, self.external_endpoint if external else self.endpoint, bucket_name
        )

    def _build_uri(self, path) -> OssUri:
        return OssUri.from_path(path, self._bucket_name)

    def _full_path(self, path) -> str:
        return self._build_uri(path).full_path

    def _replace_path(self, p):
        p["Key"] = p["name"] = "oss:/" + p["name"]
        return p

    def write(self, path, data):
        uri = self._build_uri(path)
        if uri.bucket == self._bucket_name:
            self.bucket.put_object(uri.path, data)
        else:
            self.bucket_for(uri.bucket).put_object(uri.path, data)

    def open(self, path, mode=None):
        if mode is None or mode == "rb":
            uri = self._build_uri(path)
            if uri.bucket == self._bucket_name:
                return self.bucket.get_object(uri.path)
            return self.bucket_for(uri.bucket).get_object(uri.path)
        warnings.warn(
            f"OssFs.open({path}, {mode}) 已经废弃, 使用 write 或 read 代替",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.fs.open(self._full_path(path), mode)

    def exists(self, path):
        return self.fs.exists(self._full_path(path))

    def isdir(self, path):
        return self.fs.isdir(self._full_path(path))

    def isfile(self, path):
        return self.fs.isfile(self._full_path(path))

    def copy(self, src, dst, recursive=False):
        self.fs.copy(self._full_path(src), self._full_path(dst), recursive)

    def listdir(self, path):
        return [self._replace_path(p) for p in self.fs.listdir(self._full_path(path))]

    def stat(self, path):
        """
        stat returns:
        {
            "name": "oss://qmgy-private-hz-dev/test/test.txt",
            "type": "file",
            "size": 11,
            "LastModified": 1740624773,
            "Size": 11,
            "Key": "oss://qmgy-private-hz-dev/test/test.txt"
        }
        """
        uri = self._build_uri(path)
        if uri.bucket != self._bucket_name:
            bucket = self.bucket_for(uri.bucket)
        else:
            bucket = self.bucket
        try:
            meta = bucket.get_object_meta(uri.path)
            return {
                "name": str(uri),
                "type": "file",
                "size": meta.content_length,
                "LastModified": meta.last_modified,
                "Size": meta.content_length,
                "Key": str(uri),
            }
        except oss2.exceptions.NoSuchKey:
            return self._replace_path(self.fs.stat(self._full_path(path)))

    def rm(self, path: Union[str, list[str]], recursive=False, maxdepth=None):
        if type(path) is str:
            self.fs.rm(self._full_path(path), recursive, maxdepth)
        else:
            self.fs.rm([self._full_path(p) for p in path], recursive, maxdepth)

    def absolute_path(self, path) -> str:
        return str(self._build_uri(path))

    def sign_url(self, path, expires=864000):
        uri = self._build_uri(path)
        return self.bucket_for(uri.bucket, True).sign_url("GET", uri.path, expires)
