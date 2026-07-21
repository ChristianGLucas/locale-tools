from babel import dates

from gen.messages_pb2 import FormatDateInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_pattern, parse_iso_date, parse_locale


def format_date(ax: AxiomContext, input: FormatDateInput) -> FormattedText:
    """Format a calendar date per CLDR locale conventions and length style,
    e.g. 2026-07-20 -> "Jul 20, 2026" (en_US, medium) / "20.07.2026"
    (de_DE, medium) / "Monday, July 20, 2026" (en_US, full).
    """
    try:
        loc = parse_locale(input.locale)
        d = parse_iso_date(input.date)
        check_pattern(input.format)
        text = dates.format_date(d, format=(input.format or "medium"), locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_DATE")
