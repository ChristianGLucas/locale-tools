from gen.messages_pb2 import DescribeLocaleInput, LocaleInfo
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, parse_locale, to_iso_weekday


def describe_locale(ax: AxiomContext, input: DescribeLocaleInput) -> LocaleInfo:
    """Parse a CLDR/BCP-47 locale identifier and return its rich metadata:
    language/script/territory subtags, localized and English display names,
    text direction, first day of week, weekend days, and number symbols,
    e.g. "de_DE" -> language "de", territory "DE", display_name "Deutsch
    (Deutschland)", first_week_day 1 (Monday), weekend_days [6, 7].
    """
    try:
        loc = parse_locale(input.locale)
        display_target = None
        if input.display_locale:
            display_target = str(parse_locale(input.display_locale))
        display_name = loc.get_display_name(display_target) or ""

        symbols = loc.number_symbols.get("latn") or {}
        weekend_days = [
            to_iso_weekday(d) for d in range(loc.weekend_start, loc.weekend_end + 1)
        ]

        return LocaleInfo(
            locale=str(loc),
            language=loc.language or "",
            script=loc.script or "",
            territory=loc.territory or "",
            display_name=display_name,
            english_name=loc.english_name or "",
            text_direction=loc.text_direction,
            first_week_day=to_iso_weekday(loc.first_week_day),
            weekend_days=weekend_days,
            decimal_symbol=symbols.get("decimal", ""),
            group_symbol=symbols.get("group", ""),
            percent_symbol=symbols.get("percentSign", ""),
        )
    except LocaleToolsError as e:
        return LocaleInfo(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return LocaleInfo(error="BAD_LOCALE")
