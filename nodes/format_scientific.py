from babel import numbers

from gen.messages_pb2 import FormatScientificInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_pattern, parse_locale


def format_scientific(ax: AxiomContext, input: FormatScientificInput) -> FormattedText:
    """Format a number in localized scientific notation per CLDR patterns,
    e.g. 12345.0 -> "1.2345E4".
    """
    try:
        loc = parse_locale(input.locale)
        check_pattern(input.format)
        text = numbers.format_scientific(input.value, format=(input.format or None), locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
