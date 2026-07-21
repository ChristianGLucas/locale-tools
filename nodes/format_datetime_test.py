from gen.messages_pb2 import FormatDatetimeInput, FormattedText
from nodes.format_datetime import format_datetime


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


def test_format_datetime_medium_en_us():
    ax = _TestContext()
    result = format_datetime(ax, FormatDatetimeInput(datetime="2026-07-20T15:04:05", locale="en_US"))
    assert result.error == ""
    assert result.text == "Jul 20, 2026, 3:04:05 PM"


def test_format_datetime_medium_de_de():
    ax = _TestContext()
    result = format_datetime(ax, FormatDatetimeInput(datetime="2026-07-20T15:04:05", locale="de_DE"))
    assert result.error == ""
    assert result.text == "20.07.2026, 15:04:05"


def test_format_datetime_trailing_z_offset_dropped():
    # A trailing "Z" is accepted and the naive wall-clock fields are
    # formatted as given (no timezone conversion) — same result as the
    # offset-free input above.
    ax = _TestContext()
    result = format_datetime(
        ax, FormatDatetimeInput(datetime="2026-07-20T15:04:05Z", locale="de_DE")
    )
    assert result.error == ""
    assert result.text == "20.07.2026, 15:04:05"


def test_format_datetime_long_style_appends_utc_designator():
    # "long"/"full" styles include a zone designator; a naive (offset-free)
    # input is treated as UTC for that designator — documented on the
    # datetime field so a caller isn't surprised by "UTC" appearing.
    ax = _TestContext()
    result = format_datetime(
        ax, FormatDatetimeInput(datetime="2026-11-03T08:15:00", locale="en_GB", format="long")
    )
    assert result.error == ""
    assert result.text == "3 November 2026, 08:15:00 UTC"


def test_format_datetime_bad_datetime_is_structured_error():
    ax = _TestContext()
    result = format_datetime(ax, FormatDatetimeInput(datetime="garbage", locale="en_US"))
    assert result.error == "BAD_DATE"
