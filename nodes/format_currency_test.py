from gen.messages_pb2 import FormatCurrencyInput, FormattedText
from nodes.format_currency import format_currency


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


def test_format_currency_en_us():
    # Independent oracle: US dollar convention is a leading "$" symbol.
    ax = _TestContext()
    result = format_currency(ax, FormatCurrencyInput(value=1234.5, currency="USD", locale="en_US"))
    assert result.error == ""
    assert result.text == "$1,234.50"


def test_format_currency_de_de_trailing_symbol():
    # Independent oracle: German currency convention places the symbol
    # after the amount, with a non-breaking space, "." grouping and ","
    # decimal separator.
    ax = _TestContext()
    result = format_currency(ax, FormatCurrencyInput(value=1234.5, currency="EUR", locale="de_DE"))
    assert result.error == ""
    assert result.text == "1.234,50\xa0€"


def test_format_currency_name_style():
    ax = _TestContext()
    result = format_currency(
        ax, FormatCurrencyInput(value=1.0, currency="USD", locale="de_DE", format_type="name")
    )
    assert result.error == ""
    assert result.text == "1,00 US-Dollar"


def test_format_currency_accounting_negative():
    ax = _TestContext()
    result = format_currency(
        ax, FormatCurrencyInput(value=-1234.5, currency="USD", locale="en_US", format_type="accounting")
    )
    assert result.error == ""
    assert result.text == "($1,234.50)"


def test_format_currency_compact():
    ax = _TestContext()
    result = format_currency(
        ax, FormatCurrencyInput(value=1234567, currency="USD", locale="en_US", compact=True)
    )
    assert result.error == ""
    assert result.text == "$1M"


def test_format_currency_unknown_currency_is_structured_error():
    ax = _TestContext()
    result = format_currency(ax, FormatCurrencyInput(value=1.0, currency="ZZZ", locale="en_US"))
    assert result.error == "BAD_CURRENCY"
    assert result.text == ""
