from babel import dates

from gen.messages_pb2 import FormatTimedeltaInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, parse_locale

_GRANULARITIES = ("year", "month", "week", "day", "hour", "minute", "second")
_FORMATS = ("narrow", "short", "medium", "long")


def format_timedelta(ax: AxiomContext, input: FormatTimedeltaInput) -> FormattedText:
    """Format a duration as localized relative time, e.g. 7200 seconds ->
    "2 hours" (add_direction=false) or "in 2 hours" (add_direction=true,
    positive) / "2 hours ago" (add_direction=true, negative).
    """
    try:
        loc = parse_locale(input.locale)
        granularity = input.granularity or "second"
        if granularity not in _GRANULARITIES:
            raise LocaleToolsError(
                "BAD_VALUE", f"granularity must be one of {_GRANULARITIES}, got {granularity!r}"
            )
        fmt = input.format or "long"
        if fmt not in _FORMATS:
            raise LocaleToolsError("BAD_VALUE", f"format must be one of {_FORMATS}, got {fmt!r}")
        threshold = input.threshold if input.threshold else 0.85
        text = dates.format_timedelta(
            input.seconds,
            granularity=granularity,
            threshold=threshold,
            add_direction=input.add_direction,
            format=fmt,
            locale=loc,
        )
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
