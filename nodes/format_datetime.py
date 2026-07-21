from babel import dates

from gen.messages_pb2 import FormatDatetimeInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_pattern, parse_iso_datetime, parse_locale


def format_datetime(ax: AxiomContext, input: FormatDatetimeInput) -> FormattedText:
    """Format a combined date and time per CLDR locale conventions and
    length style, e.g. 2026-07-20T15:04:05 -> "Jul 20, 2026, 3:04:05 PM"
    (en_US, medium). A trailing "Z"/offset on the input is accepted and
    dropped — the naive wall-clock fields are formatted as given, with no
    timezone conversion. "full"/"long" styles append a timezone designator
    and treat the naive input as UTC for it — "long" renders it short
    (e.g. "...08:15:00 UTC"), "full" spelled out (e.g. "...08:15:00
    Coordinated Universal Time").
    """
    try:
        loc = parse_locale(input.locale)
        dt = parse_iso_datetime(input.datetime)
        check_pattern(input.format)
        text = dates.format_datetime(dt, format=(input.format or "medium"), locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_DATE")
