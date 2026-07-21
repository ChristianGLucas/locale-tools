from gen.messages_pb2 import FormatDecimalInput, FormattedText
from nodes.format_decimal import format_decimal


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


def test_format_decimal_en_us():
    # Independent oracle: en_US grouping/decimal convention is a comma
    # thousands separator and a period decimal point — a fact independent
    # of Babel's implementation, not derived from it.
    ax = _TestContext()
    result = format_decimal(ax, FormatDecimalInput(value=1234567.891, locale="en_US"))
    assert isinstance(result, FormattedText)
    assert result.error == ""
    assert result.text == "1,234,567.891"
    assert result.locale == "en_US"


def test_format_decimal_de_de():
    # Independent oracle: German uses a period thousands separator and a
    # comma decimal point — the reverse of en_US.
    ax = _TestContext()
    result = format_decimal(ax, FormatDecimalInput(value=1234567.891, locale="de_DE"))
    assert result.error == ""
    assert result.text == "1.234.567,891"


def test_format_decimal_hindi_lakh_grouping():
    # Independent oracle: the Indian numbering system groups digits as
    # 3, then 2, then 2 from the right (lakh/crore), not 3-3-3 like
    # en_US/de_DE — a real-world convention, not a Babel-specific choice.
    ax = _TestContext()
    result = format_decimal(ax, FormatDecimalInput(value=1234567, locale="hi_IN"))
    assert result.error == ""
    assert result.text == "12,34,567"


def test_format_decimal_compact():
    ax = _TestContext()
    result = format_decimal(
        ax, FormatDecimalInput(value=1234.0, locale="en_US", compact=True)
    )
    assert result.error == ""
    assert result.text == "1K"


def test_format_decimal_bad_locale_is_structured_error_not_crash():
    ax = _TestContext()
    result = format_decimal(ax, FormatDecimalInput(value=1.0, locale="not-a-real-locale!!"))
    assert result.error == "BAD_LOCALE"
    assert result.text == ""
