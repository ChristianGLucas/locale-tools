from babel import units

from gen.messages_pb2 import FormatUnitInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_code, parse_locale

_LENGTHS = ("long", "short", "narrow")


def format_unit(ax: AxiomContext, input: FormatUnitInput) -> FormattedText:
    """Format a measurement value with its CLDR unit display name at a
    chosen length, e.g. 5 "length-meter" -> "5 meters" (en_US, long) /
    "5 m" (short).
    """
    try:
        loc = parse_locale(input.locale)
        check_code(input.unit, "unit")
        if not input.unit:
            raise LocaleToolsError("BAD_UNIT", "unit is required")
        length = input.length or "long"
        if length not in _LENGTHS:
            raise LocaleToolsError(
                "BAD_VALUE", f"length must be one of {_LENGTHS}, got {length!r}"
            )
        text = units.format_unit(input.value, input.unit, length=length, locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except units.UnknownUnitError:
        return FormattedText(error="BAD_UNIT")
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
