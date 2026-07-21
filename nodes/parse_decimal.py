from babel import numbers

from gen.messages_pb2 import ParseDecimalInput, ParsedNumber
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, parse_locale

_MAX_TEXT_LEN = 128


def parse_decimal(ax: AxiomContext, input: ParseDecimalInput) -> ParsedNumber:
    """Parse a localized decimal string back into a numeric value (the
    inverse of FormatDecimal), respecting the locale's grouping and decimal
    separators, e.g. "1.234,56" in de_DE -> 1234.56.
    """
    try:
        loc = parse_locale(input.locale)
        if not input.text:
            raise LocaleToolsError("UNPARSEABLE", "text is required")
        if len(input.text) > _MAX_TEXT_LEN:
            raise LocaleToolsError(
                "BAD_VALUE", f"text is {len(input.text)} chars, exceeding the {_MAX_TEXT_LEN} limit"
            )
        value = numbers.parse_decimal(input.text, locale=loc)
        fvalue = float(value)
        return ParsedNumber(value=fvalue, is_integer=(fvalue == int(fvalue)))
    except LocaleToolsError as e:
        return ParsedNumber(error=e.token)
    except numbers.NumberFormatError:
        return ParsedNumber(error="UNPARSEABLE")
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return ParsedNumber(error="UNPARSEABLE")
