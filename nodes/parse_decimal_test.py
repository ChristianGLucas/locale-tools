from gen.messages_pb2 import ParseDecimalInput, ParsedNumber
from nodes.parse_decimal import parse_decimal


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


def test_parse_decimal_de_de():
    # Independent oracle: "1.234,56" is 1234.56 under German grouping
    # conventions (period=group, comma=decimal) — a fact independent of
    # Babel's own implementation.
    ax = _TestContext()
    result = parse_decimal(ax, ParseDecimalInput(text="1.234,56", locale="de_DE"))
    assert result.error == ""
    assert result.value == 1234.56
    assert result.is_integer is False


def test_parse_decimal_en_us():
    ax = _TestContext()
    result = parse_decimal(ax, ParseDecimalInput(text="1,234.56", locale="en_US"))
    assert result.error == ""
    assert result.value == 1234.56


def test_parse_decimal_round_trip_with_format_decimal():
    # Round-trip against our own FormatDecimal is a consistency check, not
    # the oracle (see the two tests above for the independent oracle), but
    # it demonstrates the pair genuinely inverts.
    from nodes.format_decimal import format_decimal
    from gen.messages_pb2 import FormatDecimalInput

    ax = _TestContext()
    formatted = format_decimal(ax, FormatDecimalInput(value=9876.5, locale="fr_FR"))
    assert formatted.error == ""
    parsed = parse_decimal(ax, ParseDecimalInput(text=formatted.text, locale="fr_FR"))
    assert parsed.error == ""
    assert parsed.value == 9876.5


def test_parse_decimal_unparseable_is_structured_error_not_crash():
    ax = _TestContext()
    result = parse_decimal(ax, ParseDecimalInput(text="not a number at all", locale="en_US"))
    assert result.error == "UNPARSEABLE"


def test_parse_decimal_empty_text_is_structured_error():
    ax = _TestContext()
    result = parse_decimal(ax, ParseDecimalInput(text="", locale="en_US"))
    assert result.error == "UNPARSEABLE"
