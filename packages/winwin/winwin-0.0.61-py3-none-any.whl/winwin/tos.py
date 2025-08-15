import os
import logging
import warnings
from typing import Optional, Union, Dict, Any
from urllib.parse import urlparse

import importlib
from pydantic import Field, field_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

tos = importlib.import_module("tos")
import tosfs


from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class TosConfig(BaseSettings):
    access_key: str = Field(
        ...,
        json_schema_extra={
            "description": "Access Key for client authentication",
        }
    )
    secret_key: str = Field(
        ...,
        json_schema_extra={
            "description": "Secret Key for client authentication",
        }
    )
    endpoint: str = Field(
        default="tos-cn-beijing.volces.com",
        json_schema_extra={
            "description": "API endpoint for the client",
            "example": "tos-cn-beijing.volces.com"
        }
    )

    model_config = SettingsConfigDict(
        env_prefix="",
        json_schema_extra={
            "title": "Client Configuration",
            "description": "Configuration for initializing a client with access key, secret key, and endpoint."
        }
    )

    @classmethod
    @field_validator("access_key", mode="before")
    def validate_ak(cls, value: Optional[str]) -> str:
        if value is None:
            value = cls._get_env("TOS_ACCESS_KEY") or cls._get_env("VOLC_ACCESSKEY")
        if not value:
            raise ValueError("Access Key (ak) must be provided or set in environment variables 'TOS_ACCESS_KEY' or 'VOLC_ACCESSKEY'")
        return value


    @classmethod
    @field_validator("sk", mode="before")
    def validate_sk(cls, value: Optional[str]) -> str:
        if value is None:
            value = cls._get_env("TOS_SECRET_KEY") or cls._get_env("VOLC_SECRETKEY")
        if not value:
            raise ValueError("Secret Key (sk) must be provided or set in environment variables 'TOS_SECRET_KEY' or 'VOLC_SECRETKEY'")
        return value

    @classmethod
    @field_validator("endpoint", mode="before")
    def validate_endpoint(cls, value: Optional[str]) -> str:
        if value is None:
            value = cls._get_env("ENDPOINT")
        return value or "tos-cn-beijing.volces.com"

    @staticmethod
    def _get_env(key: str) -> Optional[str]:
        """Helper method to access environment variables."""
        return os.getenv(key)


class TosUri:
    def __init__(self, bucket: str, path: str):
        self.bucket = bucket
        self.path = path.lstrip("/")

    def __str__(self) -> str:
        return f"tos://{self.bucket}/{self.path}"

    @classmethod
    def from_path(cls, path: str, bucket: Optional[str] = None) -> 'TosUri':
        if path.startswith("tos://"):
            result = urlparse(path)
            return cls(result.netloc, result.path)
        if bucket is None:
            raise ValueError("Bucket must be provided for non-tos:// paths")
        return cls(bucket, path)

    @property
    def full_path(self) -> str:
        return f"/{self.bucket}/{self.path}"


class TosFs:
    def __init__(self, config: TosConfig):
        self._config = config
        self._client: Optional[tos.TosClientV2] = None
        self.fs = tosfs.TosFileSystem(
            key=config.access_key,
            secret=config.secret_key,
            endpoint=config.endpoint,
            region=config.region,
        )

    @property
    def endpoint(self) -> str:
        return self._config.endpoint

    @property
    def external_endpoint(self) -> str:
        return self._config.endpoint

    @property
    def client(self) -> tos.TosClientV2:
        if not self._client:
            self._client = self._create_client(self._config.bucket)
        return self._client

    def _create_client(self, bucket_name: str, external: bool = False) -> tos.TosClientV2:
        logging.info(f"TosClient Config: {self._config}")
        return tos.TosClientV2(
            ak=self._config.access_key,
            sk=self._config.secret_key,
            endpoint=self.external_endpoint if external else self.endpoint,
            region=self._config.region,
        )

    def _build_uri(self, path: str) -> TosUri:
        return TosUri.from_path(path, self._config.bucket)

    def _full_path(self, path: str) -> str:
        return self._build_uri(path).full_path

    def _replace_path(self, p: Dict[str, Any]) -> Dict[str, Any]:
        p["Key"] = p["name"] = f"tos:/{p['name']}"
        return p

    def write(self, path: str, data: bytes) -> None:
        uri = self._build_uri(path)
        client = self.client if uri.bucket == self._config.bucket else self._create_client(uri.bucket)
        resp = client.put_object(uri.bucket, uri.path, content=data)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to write to {path}: {resp.status_code}")

    def open(self, path: str, mode: Optional[str] = None):
        if mode is None or mode == "rb":
            uri = self._build_uri(path)
            client = self.client if uri.bucket == self._config.bucket else self._create_client(uri.bucket)
            return client.get_object(uri.bucket, uri.path)
        warnings.warn(
            f"TosFs.open({path}, {mode}) is deprecated, use write or read instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.fs.open(self._full_path(path), mode)

    def exists(self, path: str) -> bool:
        return self.fs.exists(self._full_path(path))

    def isdir(self, path: str) -> bool:
        return self.fs.isdir(self._full_path(path))

    def isfile(self, path: str) -> bool:
        return self.fs.isfile(self._full_path(path))

    def copy(self, src: str, dst: str, recursive: bool = False) -> None:
        self.fs.copy(self._full_path(src), self._full_path(dst), recursive)

    def listdir(self, path: str) -> list:
        return [self._replace_path(p) for p in self.fs.listdir(self._full_path(path))]

    def stat(self, path: str) -> Dict[str, Any]:
        uri = self._build_uri(path)
        client = self.client if uri.bucket == self._config.bucket else self._create_client(uri.bucket)
        try:
            meta = client.head_object(uri.bucket, uri.path)
            return {
                "name": str(uri),
                "type": "file",
                "size": meta.content_length,
                "LastModified": meta.last_modified,
                "Size": meta.content_length,
                "Key": str(uri),
            }
        except tos.exceptions.TosServerError as e:
            if e.status_code == 404:
                return self._replace_path(self.fs.stat(self._full_path(path)))
            raise

    def rm(self, path: Union[str, list[str]], recursive: bool = False, maxdepth: Optional[int] = None) -> None:
        if isinstance(path, str):
            self.fs.rm(self._full_path(path), recursive, maxdepth)
        else:
            self.fs.rm([self._full_path(p) for p in path], recursive, maxdepth)

    def absolute_path(self, path: str) -> str:
        return str(self._build_uri(path))

    def sign_url(self, path: str, expires: int = 864000) -> str:
        uri = self._build_uri(path)
        client = self._create_client(uri.bucket, external=True)
        return client.pre_signed_url("GET", uri.bucket, uri.path, expires)
