# ruff: noqa: T201
import os
from os import environ
import logging
import pytest

from pathlib import Path
from winwin.tos import TosFs, TosConfig


@pytest.fixture
def fs():
    print(f"Env: {os.environ}")
    return create_fs()


def create_fs():
    tos_config = TosConfig()
    logging.info(f"tos_config: {tos_config}")
    return TosFs(tos_config)


def test_tos(fs):
    fs.write("test/test.txt", b"hello world")
    assert fs.exists("test/test.txt")
    assert fs.open("test/test.txt").read() == b"hello world"


def test_upload(fs):
    file = Path(__file__).parent / "resource/data.jsonl"
    with open(file, "rb") as f:
        fs.write("test/data.jsonl", f.read())
