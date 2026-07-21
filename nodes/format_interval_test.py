from gen.messages_pb2 import FormatIntervalInput, FormattedText
from nodes.format_interval import format_interval

# CLDR's en_US interval separator: an en dash (U+2013) padded by thin spaces
# (U+2009) on each side — built explicitly by code point so the exact
# characters are unambiguous in this source file.
_THIN_SPACE = chr(0x2009)
_EN_DASH = chr(0x2013)
_SEP = f"{_THIN_SPACE}{_EN_DASH}{_THIN_SPACE}"


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


def test_format_interval_default_style():
    ax = _TestContext()
    result = format_interval(
        ax, FormatIntervalInput(start="2026-01-01", end="2026-01-05", locale="en_US")
    )
    assert result.error == ""
    assert result.text == f"Jan 1, 2026{_SEP}Jan 5, 2026"


def test_format_interval_compact_skeleton():
    ax = _TestContext()
    result = format_interval(
        ax,
        FormatIntervalInput(
            start="2026-01-01", end="2026-01-05", locale="en_US", skeleton="yMMMd"
        ),
    )
    assert result.error == ""
    assert result.text == f"Jan 1{_SEP}5, 2026"


def test_format_interval_mismatched_kinds_is_structured_error():
    ax = _TestContext()
    result = format_interval(
        ax, FormatIntervalInput(start="2026-01-01", end="2026-01-05T10:00:00", locale="en_US")
    )
    assert result.error == "BAD_DATE"


def test_format_interval_bad_date_is_structured_error():
    ax = _TestContext()
    result = format_interval(
        ax, FormatIntervalInput(start="not-a-date", end="2026-01-05", locale="en_US")
    )
    assert result.error == "BAD_DATE"
