from gen.messages_pb2 import FormatTimedeltaInput, FormattedText
from nodes.format_timedelta import format_timedelta


class _TestContext:
    class _Logger:
        def debug(self, msg: str, **attrs) -> None: pass
        def info(self, msg: str, **attrs) -> None: pass
        def warn(self, msg: str, **attrs) -> None: pass
        def error(self, msg: str, **attrs) -> None: pass

    class _Secrets:
        def __init__(self, m: dict) -> None:
            self._m = m or {}
        def get(self, name: str):
            v = self._m.get(name)
            return (v, True) if v is not None else ("", False)

    def __init__(self, secrets_map: dict | None = None) -> None:
        self.log = self._Logger()
        self.secrets = self._Secrets(secrets_map or {})
        self.execution_id = "test-execution-id"
        self.flow_id = "test-flow-id"
        self.tenant_id = "test-tenant-id"


def test_format_timedelta_no_direction():
    ax = _TestContext()
    result = format_timedelta(ax, FormatTimedeltaInput(seconds=7200, locale="en_US"))
    assert result.error == ""
    assert result.text == "2 hours"


def test_format_timedelta_future_direction():
    ax = _TestContext()
    result = format_timedelta(
        ax, FormatTimedeltaInput(seconds=3600, locale="en_US", add_direction=True)
    )
    assert result.error == ""
    assert result.text == "in 1 hour"


def test_format_timedelta_past_direction():
    ax = _TestContext()
    result = format_timedelta(
        ax, FormatTimedeltaInput(seconds=-3600, locale="en_US", add_direction=True)
    )
    assert result.error == ""
    assert result.text == "1 hour ago"


def test_format_timedelta_narrow_format():
    ax = _TestContext()
    result = format_timedelta(
        ax,
        FormatTimedeltaInput(seconds=3600, locale="en_US", add_direction=True, format="narrow"),
    )
    assert result.error == ""
    assert result.text == "in 1h"


def test_format_timedelta_bad_granularity_is_structured_error():
    ax = _TestContext()
    result = format_timedelta(
        ax, FormatTimedeltaInput(seconds=1, locale="en_US", granularity="fortnight")
    )
    assert result.error == "BAD_VALUE"
