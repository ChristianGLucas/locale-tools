from gen.messages_pb2 import GetCurrencyInfoInput, CurrencyInfo
from nodes.get_currency_info import get_currency_info


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


def test_get_currency_info_jpy():
    # Independent oracle: the Japanese Yen has no minor unit (fraction
    # digits = 0) — a real-world ISO 4217 fact, not derived from Babel.
    ax = _TestContext()
    result = get_currency_info(ax, GetCurrencyInfoInput(currency="JPY", locale="en_US"))
    assert result.error == ""
    assert result.name == "Japanese Yen"
    assert result.symbol == "¥"
    assert result.fraction_digits == 0


def test_get_currency_info_usd():
    ax = _TestContext()
    result = get_currency_info(ax, GetCurrencyInfoInput(currency="usd", locale="en_US"))
    assert result.error == ""
    assert result.currency == "USD"
    assert result.name == "US Dollar"
    assert result.symbol == "$"
    assert result.fraction_digits == 2


def test_get_currency_info_unknown_currency_is_structured_error():
    ax = _TestContext()
    result = get_currency_info(ax, GetCurrencyInfoInput(currency="ZZZ", locale="en_US"))
    assert result.error == "UNKNOWN_CURRENCY"
