from babel import units

from gen.messages_pb2 import FormatCompoundUnitInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_code, parse_locale

_LENGTHS = ("long", "short", "narrow")


def format_compound_unit(ax: AxiomContext, input: FormatCompoundUnitInput) -> FormattedText:
    """Format a rate expressed as one CLDR unit per another, e.g. 5
    "length-kilometer" per "duration-hour" -> "5 kilometers per hour"
    (en_US, long) / "5 km/h" (short).
    """
    try:
        loc = parse_locale(input.locale)
        check_code(input.numerator_unit, "numerator_unit")
        check_code(input.denominator_unit, "denominator_unit")
        if not input.numerator_unit or not input.denominator_unit:
            raise LocaleToolsError("BAD_UNIT", "numerator_unit and denominator_unit are required")
        length = input.length or "long"
        if length not in _LENGTHS:
            raise LocaleToolsError(
                "BAD_VALUE", f"length must be one of {_LENGTHS}, got {length!r}"
            )
        text = units.format_compound_unit(
            input.value,
            numerator_unit=input.numerator_unit,
            denominator_unit=input.denominator_unit,
            length=length,
            locale=loc,
        )
        if text is None:
            raise LocaleToolsError("BAD_UNIT", "no compound pattern for this unit combination")
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except units.UnknownUnitError:
        return FormattedText(error="BAD_UNIT")
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
