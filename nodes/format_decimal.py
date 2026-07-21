from babel import numbers

from gen.messages_pb2 import FormatDecimalInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_pattern, parse_locale


def format_decimal(ax: AxiomContext, input: FormatDecimalInput) -> FormattedText:
    """Format a number as a localized decimal string per CLDR grouping and
    decimal-separator rules, e.g. 1234.5 -> "1,234.5" (en_US) / "1.234,5"
    (de_DE). Set compact=true for CLDR compact notation (e.g. "1K").
    """
    try:
        loc = parse_locale(input.locale)
        check_pattern(input.format)
        if input.compact:
            format_type = input.compact_format_type or "short"
            if format_type not in ("short", "long"):
                raise LocaleToolsError(
                    "BAD_VALUE", f"compact_format_type must be short or long, got {format_type!r}"
                )
            text = numbers.format_compact_decimal(
                input.value, format_type=format_type, locale=loc
            )
        else:
            text = numbers.format_decimal(
                input.value, format=(input.format or None), locale=loc
            )
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
