from babel import dates

from gen.messages_pb2 import ParseTimeInput, ParsedTime
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, parse_locale

_MAX_TEXT_LEN = 64


def parse_time(ax: AxiomContext, input: ParseTimeInput) -> ParsedTime:
    """Parse a localized time string (formatted at a given CLDR length
    style) back into an ISO 8601 time, the inverse of FormatTime.
    """
    try:
        loc = parse_locale(input.locale)
        if not input.text:
            raise LocaleToolsError("UNPARSEABLE", "text is required")
        if len(input.text) > _MAX_TEXT_LEN:
            raise LocaleToolsError(
                "BAD_VALUE", f"text is {len(input.text)} chars, exceeding the {_MAX_TEXT_LEN} limit"
            )
        fmt = input.format or "medium"
        t = dates.parse_time(input.text, locale=loc, format=fmt)
        return ParsedTime(time=t.isoformat())
    except LocaleToolsError as e:
        return ParsedTime(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return ParsedTime(error="UNPARSEABLE")
