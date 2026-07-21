from babel import dates

from gen.messages_pb2 import FormatIntervalInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_pattern, parse_iso_instant, parse_locale


def format_interval(ax: AxiomContext, input: FormatIntervalInput) -> FormattedText:
    """Format a date/time range as one localized span, e.g.
    2026-01-01..2026-01-05 -> "Jan 1, 2026 – Jan 5, 2026" (en_US, default)
    or the more compact "Jan 1 – 5, 2026" with skeleton="yMMMd". start and
    end may each be an ISO date or an ISO datetime, but must be the same
    kind (both dates, or both datetimes).
    """
    try:
        loc = parse_locale(input.locale)
        start = parse_iso_instant(input.start)
        end = parse_iso_instant(input.end)
        if type(start) is not type(end):
            raise LocaleToolsError(
                "BAD_DATE", "start and end must both be dates or both be datetimes"
            )
        check_pattern(input.skeleton, "skeleton")
        text = dates.format_interval(start, end, skeleton=(input.skeleton or None), locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_DATE")
