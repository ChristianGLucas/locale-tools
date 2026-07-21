from babel import dates

from gen.messages_pb2 import GetCalendarNamesInput, CalendarNames
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, parse_locale

_WIDTHS = ("wide", "abbreviated", "narrow")
_FIELDS = ("weekdays", "months", "quarters", "eras", "periods")


def get_calendar_names(ax: AxiomContext, input: GetCalendarNamesInput) -> CalendarNames:
    """List the localized CLDR names for one calendar field (weekdays,
    months, quarters, eras, or day-periods) in canonical order, e.g.
    field=weekdays, width=abbreviated, en_US ->
    ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].
    """
    try:
        loc = parse_locale(input.locale)
        width = input.width or "wide"
        if width not in _WIDTHS:
            raise LocaleToolsError("BAD_VALUE", f"width must be one of {_WIDTHS}, got {width!r}")
        field = input.field
        if field not in _FIELDS:
            raise LocaleToolsError(
                "UNKNOWN_FIELD", f"field must be one of {_FIELDS}, got {field!r}"
            )

        if field == "weekdays":
            context = input.context or "format"
            data = dates.get_day_names(width, context=context, locale=loc)
            names = [data[k] for k in sorted(data.keys())]
        elif field == "months":
            context = input.context or "format"
            data = dates.get_month_names(width, context=context, locale=loc)
            names = [data[k] for k in sorted(data.keys())]
        elif field == "quarters":
            context = input.context or "format"
            data = dates.get_quarter_names(width, context=context, locale=loc)
            names = [data[k] for k in sorted(data.keys())]
        elif field == "eras":
            data = dates.get_era_names(width, locale=loc)
            names = [data[k] for k in sorted(data.keys())]
        else:  # periods
            context = input.context or "stand-alone"
            data = dates.get_period_names(width, context=context, locale=loc)
            names = list(data.values())

        return CalendarNames(field=field, names=names)
    except LocaleToolsError as e:
        return CalendarNames(field=input.field, error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return CalendarNames(field=input.field, error="BAD_VALUE")
