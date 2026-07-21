from babel import dates

from gen.messages_pb2 import FormatTimeInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_pattern, parse_iso_time, parse_locale


def format_time(ax: AxiomContext, input: FormatTimeInput) -> FormattedText:
    """Format a time-of-day per CLDR locale conventions (12h vs 24h clock,
    separators), e.g. 15:04:05 -> "3:04:05 PM" (en_US, medium) / "15:04:05"
    (de_DE, medium).
    """
    try:
        loc = parse_locale(input.locale)
        t = parse_iso_time(input.time)
        check_pattern(input.format)
        text = dates.format_time(t, format=(input.format or "medium"), locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_DATE")
