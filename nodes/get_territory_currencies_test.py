from gen.messages_pb2 import GetTerritoryCurrenciesInput, TerritoryCurrencies
from nodes.get_territory_currencies import get_territory_currencies


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


def test_get_territory_currencies_de_current():
    # Independent oracle: Germany's current currency is the Euro — a
    # real-world fact.
    ax = _TestContext()
    result = get_territory_currencies(ax, GetTerritoryCurrenciesInput(territory="de"))
    assert result.error == ""
    assert result.territory == "DE"
    assert list(result.currencies) == ["EUR"]


def test_get_territory_currencies_de_historical_includes_deutsche_mark():
    # Independent oracle: Germany used the Deutsche Mark (DEM) before
    # adopting the Euro in 1999/2002 — a real-world historical fact.
    ax = _TestContext()
    result = get_territory_currencies(
        ax, GetTerritoryCurrenciesInput(territory="DE", include_historical=True)
    )
    assert result.error == ""
    assert "DEM" in list(result.currencies)
    assert "EUR" in list(result.currencies)
    # Most-recent first.
    assert list(result.currencies).index("EUR") < list(result.currencies).index("DEM")


def test_get_territory_currencies_us():
    ax = _TestContext()
    result = get_territory_currencies(ax, GetTerritoryCurrenciesInput(territory="US"))
    assert result.error == ""
    assert list(result.currencies) == ["USD"]


def test_get_territory_currencies_unknown_territory_is_structured_error():
    ax = _TestContext()
    result = get_territory_currencies(ax, GetTerritoryCurrenciesInput(territory="ZZ"))
    assert result.error == "UNKNOWN_TERRITORY"
