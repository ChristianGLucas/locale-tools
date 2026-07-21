from babel import numbers

from gen.messages_pb2 import GetTerritoryCurrenciesInput, TerritoryCurrencies
from gen.axiom_context import AxiomContext
from nodes._common import (
    HISTORICAL_START_DATE,
    REFERENCE_DATE,
    LocaleToolsError,
    check_code,
)


def get_territory_currencies(ax: AxiomContext, input: GetTerritoryCurrenciesInput) -> TerritoryCurrencies:
    """List the ISO 4217 currency codes a territory uses or has used,
    most-recent first, e.g. "DE" -> ["EUR"] (the default) or also the
    pre-Euro Deutsche Mark when include_historical=true. Uses a fixed
    reference date rather than the real wall-clock date, so the result is
    deterministic.
    """
    try:
        check_code(input.territory, "territory")
        if not input.territory:
            raise LocaleToolsError("UNKNOWN_TERRITORY", "territory is required")
        territory = input.territory.upper()
        if input.include_historical:
            currencies = numbers.get_territory_currencies(
                territory,
                start_date=HISTORICAL_START_DATE,
                end_date=REFERENCE_DATE,
                tender=True,
                non_tender=True,
            )
        else:
            currencies = numbers.get_territory_currencies(
                territory, start_date=REFERENCE_DATE, tender=True, non_tender=False
            )
        if not currencies:
            raise LocaleToolsError("UNKNOWN_TERRITORY", f"no currency data for {territory!r}")
        # Most-recent first: Babel returns them in CLDR (chronological)
        # order, so reverse.
        return TerritoryCurrencies(territory=territory, currencies=list(reversed(currencies)))
    except LocaleToolsError as e:
        return TerritoryCurrencies(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return TerritoryCurrencies(error="UNKNOWN_TERRITORY")
