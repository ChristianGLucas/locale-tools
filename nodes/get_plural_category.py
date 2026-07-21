from gen.messages_pb2 import GetPluralCategoryInput, PluralCategory
from gen.axiom_context import AxiomContext
from nodes._common import LocaleToolsError, parse_locale

_FORMS = ("cardinal", "ordinal")


def get_plural_category(ax: AxiomContext, input: GetPluralCategoryInput) -> PluralCategory:
    """Resolve which CLDR plural category a number falls into for a locale
    — the standard way to pick between "1 file" / "2 files" in English, or
    the richer few/many/other buckets of languages like Polish, Arabic, or
    Russian, e.g. number=3, locale="cs_CZ", form=cardinal -> "few".
    """
    try:
        loc = parse_locale(input.locale)
        form = input.form or "cardinal"
        if form not in _FORMS:
            raise LocaleToolsError("UNKNOWN_FORM", f"form must be one of {_FORMS}, got {form!r}")
        rule = loc.ordinal_form if form == "ordinal" else loc.plural_form
        category = rule(input.number)
        return PluralCategory(category=str(category), locale=str(loc))
    except LocaleToolsError as e:
        return PluralCategory(error=e.token)
    except Exception:  # noqa: BLE001 - malformed input must never crash the node
        return PluralCategory(error="BAD_VALUE")
