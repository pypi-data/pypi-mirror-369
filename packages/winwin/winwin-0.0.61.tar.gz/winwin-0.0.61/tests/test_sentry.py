import pytest
import winwin
import sentry_sdk
from sentry_sdk import capture_message, capture_exception, set_tag, set_user


@pytest.fixture
def init_sentry():
    sentry_sdk.init(
        dsn=winwin.support.sentry_dsn(),
        traces_sample_rate=1.0
    )
    yield
    sentry_sdk.init(dsn=None)  # 重置 Sentry 配置


def test_sentry_initialization(init_sentry):
    assert sentry_sdk.get_client().dsn == winwin.support.sentry_dsn()
    assert sentry_sdk.get_client().is_active()


def test_capture_message(init_sentry):
    event_id = capture_message("test message", level="debug")
    assert event_id is not None
