from babel import numbers

from gen.messages_pb2 import FormatPercentInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_pattern, parse_locale


def format_percent(ax: AxiomContext, input: FormatPercentInput) -> FormattedText:
    """Format a fraction as a localized percentage per CLDR rules, e.g.
    0.256 -> "26%" (en_US, the default pattern has no decimal places) /
    "26 %" (de_DE, space before the sign).
    """
    try:
        loc = parse_locale(input.locale)
        check_pattern(input.format)
        text = numbers.format_percent(input.value, format=(input.format or None), locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
