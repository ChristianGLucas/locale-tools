import datetime
import zoneinfo

from babel import dates

from gen.messages_pb2 import GetTimezoneNameInput, TimezoneName
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, REFERENCE_DATE, check_code, parse_iso_datetime, parse_locale

_WIDTHS = ("long", "short")


def get_timezone_name(ax: AxiomContext, input: GetTimezoneNameInput) -> TimezoneName:
    """Look up the localized display name and UTC offset for an IANA time
    zone at a given instant (defaulting to a fixed reference date so the
    result is deterministic rather than depending on today's DST state),
    e.g. "America/New_York" in en_US on a July date -> "Eastern Daylight
    Time", "GMT-04:00".
    """
    try:
        loc = parse_locale(input.locale)
        check_code(input.timezone, "timezone")
        if not input.timezone:
            raise LocaleToolsError("UNKNOWN_TIMEZONE", "timezone is required")
        try:
            tz = zoneinfo.ZoneInfo(input.timezone)
        except (zoneinfo.ZoneInfoNotFoundError, ValueError) as e:
            raise LocaleToolsError("UNKNOWN_TIMEZONE", str(e)) from e

        width = input.width or "long"
        if width not in _WIDTHS:
            raise LocaleToolsError("BAD_VALUE", f"width must be one of {_WIDTHS}, got {width!r}")

        if input.at:
            naive = parse_iso_datetime(input.at)
        else:
            naive = datetime.datetime(
                REFERENCE_DATE.year, REFERENCE_DATE.month, REFERENCE_DATE.day, 12, 0, 0
            )
        dt = naive.replace(tzinfo=tz)

        display_name = dates.get_timezone_name(dt, width=width, locale=loc)
        gmt_offset = dates.get_timezone_gmt(dt, locale=loc)
        return TimezoneName(display_name=display_name, gmt_offset=gmt_offset)
    except LocaleToolsError as e:
        return TimezoneName(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return TimezoneName(error="UNKNOWN_TIMEZONE")
