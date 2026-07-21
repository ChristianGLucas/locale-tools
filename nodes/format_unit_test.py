from gen.messages_pb2 import FormatUnitInput, FormattedText
from nodes.format_unit import format_unit


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


def test_format_unit_long_en_us():
    ax = _TestContext()
    result = format_unit(ax, FormatUnitInput(value=5, unit="length-meter", locale="en_US"))
    assert result.error == ""
    assert result.text == "5 meters"


def test_format_unit_short_en_us():
    ax = _TestContext()
    result = format_unit(
        ax, FormatUnitInput(value=5, unit="length-meter", locale="en_US", length="short")
    )
    assert result.error == ""
    assert result.text == "5 m"


def test_format_unit_narrow_en_us():
    ax = _TestContext()
    result = format_unit(
        ax, FormatUnitInput(value=5, unit="length-meter", locale="en_US", length="narrow")
    )
    assert result.error == ""
    assert result.text == "5m"


def test_format_unit_unknown_unit_is_structured_error():
    ax = _TestContext()
    result = format_unit(ax, FormatUnitInput(value=5, unit="not-a-real-unit", locale="en_US"))
    assert result.error == "BAD_UNIT"
    assert result.text == ""
