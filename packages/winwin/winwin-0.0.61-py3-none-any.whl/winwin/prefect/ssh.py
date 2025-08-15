import logging
from io import StringIO
from typing import Optional

from fabric import Connection
from paramiko.rsakey import RSAKey
from prefect.blocks.abstract import CredentialsBlock
from pydantic import Field, SecretStr


class SshCredentials(CredentialsBlock):
    _block_type_name = "SSH Credentials"

    _block_type_slug = "ssh"

    _description = "SSH credentials."

    host: str = Field(
        default=...,
        description="A specific server host.",
        title="Server Host",
    )

    port: Optional[int] = Field(
        default=22,
        description="A specific server port.",
        title="Server Port",
    )

    username: str = Field(
        default=...,
        description="A specific server username.",
        title="Server Username",
    )

    private_key: SecretStr = Field(
        default=...,
        description="A specific server private key.",
        title="Server Private Key",
    )

    env: dict[str, str] = Field(
        default_factory=dict,
        description="A specific server env.",
        title="Server Env",
    )

    working_dir: Optional[str] = Field(
        default=None,
        description="A specific server working dir.",
        title="Server Working Dir",
    )

    def __hash__(self):
        return hash((self.host, self.port, self.username, self.private_key, self.env))

    def get_client(self, *args, **kwargs):
        private_key = RSAKey.from_private_key(
            StringIO(self.private_key.get_secret_value())
        )

        conn = Connection(
            host=self.host,
            port=self.port,
            user=self.username,
            connect_kwargs={"pkey": private_key},
            inline_ssh_env=self.env is not None,
        )
        if self.env is not None:
            conn.config.run.env = self.env
        return conn

    def run(self, command: str, **kwargs):
        logging.info(f"run {command}")
        conn = self.get_client()
        if self.working_dir is not None:
            with conn.cd(self.working_dir):
                return conn.run(command, **kwargs)
        else:
            return conn.run(command)
