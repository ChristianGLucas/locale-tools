from babel import numbers

from gen.messages_pb2 import GetCurrencyInfoInput, CurrencyInfo
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_code, parse_locale


def get_currency_info(ax: AxiomContext, input: GetCurrencyInfoInput) -> CurrencyInfo:
    """Look up locale-specific display metadata for an ISO 4217 currency
    code: its localized full name, localized symbol, and conventional
    fraction-digit count, e.g. "JPY" in en_US -> name "Japanese Yen",
    symbol "¥", fraction_digits 0.
    """
    try:
        loc = parse_locale(input.locale)
        check_code(input.currency, "currency")
        if not input.currency:
            raise LocaleToolsError("BAD_CURRENCY", "currency is required")
        currency = input.currency.upper()
        if not numbers.is_currency(currency):
            # get_currency_name/symbol/precision silently fall back to
            # echoing the code for a currency they've never heard of,
            # rather than raising — check first instead of returning that
            # confusing no-op "identity" result.
            raise LocaleToolsError("UNKNOWN_CURRENCY", f"unrecognized currency {currency!r}")
        name = numbers.get_currency_name(currency, locale=loc)
        symbol = numbers.get_currency_symbol(currency, locale=loc)
        precision = numbers.get_currency_precision(currency)
        return CurrencyInfo(
            currency=currency, name=name, symbol=symbol, fraction_digits=precision
        )
    except LocaleToolsError as e:
        return CurrencyInfo(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return CurrencyInfo(error="BAD_VALUE")
