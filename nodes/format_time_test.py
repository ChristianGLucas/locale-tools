from gen.messages_pb2 import FormatTimeInput, FormattedText
from nodes.format_time import format_time


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


def test_format_time_medium_en_us_12h_clock():
    # Independent oracle: US convention is a 12-hour clock with an AM/PM
    # marker; CLDR joins the marker with a narrow no-break space (U+202F).
    ax = _TestContext()
    result = format_time(ax, FormatTimeInput(time="15:04:05", locale="en_US"))
    assert result.error == ""
    assert result.text == "3:04:05 PM"


def test_format_time_medium_de_de_24h_clock():
    # Independent oracle: German convention is a 24-hour clock.
    ax = _TestContext()
    result = format_time(ax, FormatTimeInput(time="15:04:05", locale="de_DE"))
    assert result.error == ""
    assert result.text == "15:04:05"


def test_format_time_bad_time_is_structured_error_not_crash():
    ax = _TestContext()
    result = format_time(ax, FormatTimeInput(time="25:99:99", locale="en_US"))
    assert result.error == "BAD_DATE"
    assert result.text == ""
