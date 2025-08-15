from typing import Any

from odps import ODPS
from prefect.blocks.abstract import CredentialsBlock
from pydantic import Field, SecretStr


class OdpsCredentials(CredentialsBlock):
    """
    Block used to manage authentication with Aliyun MaxCompute.

    Args:
        access_id (str): The maxcompute access key id.
        access_key (str): The maxcompute access key secret.
        endpoint (str): The maxcompute endpoint.


    Example:
        Load stored odps credentials:
        ```python
        from winwin.prefect import OdpsCredentials

        odps_credentials_block = OdpsCredentials.load("BLOCK_NAME")
        ```
    """

    _block_type_name = "Odps Credentials"
    _block_type_slug = "odps"
    _logo_url = "https://avatars.githubusercontent.com/u/941070?s=48&v=4"
    _documentation_url = "https://help.aliyun.com/zh/maxcompute/"

    access_id: str = Field(
        ...,
        description="MaxCompute Access Key ID.",
        examples=["LTAI5txxxxxxxxxxxxxxxxxx"],
    )
    access_key: SecretStr = Field(
        default=..., description="MaxCompute Access Key Secret."
    )
    endpoint: str = Field(
        default=...,
        description="MaxCompute endpoint, see https://help.aliyun.com/zh/maxcompute/user-guide/endpoints",
        examples=["https://service.cn-hangzhou-vpc.maxcompute.aliyun-inc.com/api"],
    )
    tunnel_endpoint: str = Field(
        default=...,
        description="MaxCompute endpoint, see https://help.aliyun.com/zh/maxcompute/user-guide/endpoints",
        examples=["https://dt.cn-hangzhou-vpc.maxcompute.aliyun-inc.com"],
    )

    def get_client(self, **connect_kwargs: Any) -> ODPS:
        return ODPS(
            self.access_id,
            self.access_key.get_secret_value(),
            project=connect_kwargs.get("project"),
            endpoint=self.endpoint,
            tunnel_endpoint=self.tunnel_endpoint,
        )
