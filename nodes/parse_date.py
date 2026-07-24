from babel import dates

from gen.messages_pb2 import ParseDateInput, ParsedDate
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, parse_locale


def parse_date(ax: AxiomContext, input: ParseDateInput) -> ParsedDate:
    """Parse a localized date string (formatted at a given CLDR length
    style) back into an ISO 8601 date, the inverse of FormatDate. Babel's
    parser reliably round-trips numeric styles ("short", and "medium" in
    many locales); a spelled-out month/weekday name can fail even for
    Babel's own output — this returns UNPARSEABLE rather than crashing.
    """
    try:
        loc = parse_locale(input.locale)
        if not input.text:
            raise LocaleToolsError("UNPARSEABLE", "text is required")
        fmt = input.format or "medium"
        d = dates.parse_date(input.text, locale=loc, format=fmt)
        return ParsedDate(date=d.isoformat())
    except LocaleToolsError as e:
        return ParsedDate(error=e.token)
    except Exception:  # noqa: BLE001 - Babel's parser can raise IndexError/ParseError on
        # patterns it can't resolve (e.g. spelled month names); never let that reach the caller.
        return ParsedDate(error="UNPARSEABLE")
