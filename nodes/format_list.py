from babel import lists

from gen.messages_pb2 import FormatListInput, FormattedText
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, check_list, parse_locale

_STYLES = (
    "standard",
    "standard-short",
    "or",
    "or-short",
    "unit",
    "unit-short",
    "unit-narrow",
)


def format_list(ax: AxiomContext, input: FormatListInput) -> FormattedText:
    """Join items into one localized, grammatically correct list phrase per
    CLDR list patterns, e.g. ["a","b","c"] -> "a, b, and c" (en_US,
    standard) / "a, b y c" (es, standard — "y" not "e").
    """
    try:
        loc = parse_locale(input.locale)
        items = list(input.items)
        check_list(items)
        style = input.style or "standard"
        if style not in _STYLES:
            raise LocaleToolsError("BAD_VALUE", f"style must be one of {_STYLES}, got {style!r}")
        text = lists.format_list(items, style=style, locale=loc)
        return FormattedText(text=text, locale=str(loc))
    except LocaleToolsError as e:
        return FormattedText(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return FormattedText(error="BAD_VALUE")
