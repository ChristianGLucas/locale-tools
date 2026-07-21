from babel import numbers

from gen.messages_pb2 import FormatCurrencyInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_code, parse_locale

_STANDARD_FORMAT_TYPES = ("standard", "name", "accounting")


def format_currency(ax: AxiomContext, input: FormatCurrencyInput) -> FormattedText:
    """Format an amount with an ISO 4217 currency code per CLDR locale
    conventions (symbol placement, grouping, fraction digits), e.g. 1234.5
    USD -> "$1,234.50" (en_US) / "1.234,50 €" (de_DE). format_type selects
    "standard" (symbol, default), "name" (spelled-out, e.g. "1.00 US
    dollars"), or "accounting" (parenthesized negatives). Set compact=true
    for compact notation (e.g. "$1M") — compact mode always renders in
    "short" style; format_type is ignored when compact=true.
    """
    try:
        loc = parse_locale(input.locale)
        check_code(input.currency, "currency")
        if not input.currency:
            raise LocaleToolsError("BAD_CURRENCY", "currency is required")
        if not numbers.is_currency(input.currency):
            # format_currency itself doesn't validate — an unrecognized code
            # like "ZZZ" would silently render as "ZZZ1.00" instead of
            # erroring, so check first.
            raise LocaleToolsError("BAD_CURRENCY", f"unrecognized currency {input.currency!r}")
        if input.compact:
            text = numbers.format_compact_currency(
                input.value, input.currency, locale=loc
            )
        else:
            format_type = input.format_type or "standard"
            if format_type not in _STANDARD_FORMAT_TYPES:
                raise LocaleToolsError(
                    "BAD_VALUE",
                    f"format_type must be one of {_STANDARD_FORMAT_TYPES}, got {format_type!r}",
                )
            text = numbers.format_currency(
                input.value, input.currency, locale=loc, format_type=format_type
            )
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except numbers.UnknownCurrencyError:
        return FormattedText(error="BAD_CURRENCY")
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
