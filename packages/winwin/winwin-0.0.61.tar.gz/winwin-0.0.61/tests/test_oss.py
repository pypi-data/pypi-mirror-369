# ruff: noqa: T201
import os
from os import environ as env
from time import sleep

import pytest

from winwin.oss import OssFs


@pytest.fixture
def fs():
    return create_fs()


def create_fs():
    return OssFs(
        access_id=env["OSS_ACCESS_KEY_ID"],
        access_key=env["OSS_ACCESS_KEY_SECRET"],
        endpoint=env["OSS_ENDPOINT"],
        bucket=env["OSS_BUCKET"],
    )


def test_oss(fs):
    assert fs.endpoint == "https://oss-cn-hangzhou.aliyuncs.com"
    assert fs.external_endpoint == "https://oss-cn-hangzhou.aliyuncs.com"

    fs.write("test/test.txt", "hello world")
    assert fs.bucket.get_object("test/test.txt").read() == b"hello world"


def test_oss_stat(fs):
    st = fs.stat("test")
    print(st)
    assert "Size" in st

    meta = fs.bucket.get_object_meta("test/")
    print(meta)


def test_oss_fs(fs):
    for i in range(3):
        file = f"test/{i}.txt"
        path = fs.absolute_path(file)
        cmd = f"/Users/wenbinye/work/bin/ossutil cp -f /tmp/test.txt {path}"
        print("cmd", cmd)
        ret = os.system(cmd)
        assert ret == 0
        try:
            if create_fs().stat(file):
                print("file exists")
                fs.open(file, "rb")
        except FileNotFoundError:
            print(f"===={file} not found")
            while True:
                try:
                    if create_fs().stat(file):
                        print("file exists")
                        fs.open(file, "rb")
                        break
                except FileNotFoundError:
                    print(f"===={file} not found")
                    sleep(1)
                    continue


def test_stat(fs):
    st = fs.stat("test/test.txt")
    print(st)
