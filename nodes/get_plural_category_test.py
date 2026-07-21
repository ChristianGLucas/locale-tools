from gen.messages_pb2 import GetPluralCategoryInput, PluralCategory
from nodes.get_plural_category import get_plural_category


class _TestContext:
    class _Logger:
        def debug(self, msg: str, **attrs) -> None: pass
        def info(self, msg: str, **attrs) -> None: pass
        def warn(self, msg: str, **attrs) -> None: pass
        def error(self, msg: str, **attrs) -> None: pass

    class _Secrets:
        def __init__(self, m: dict) -> None:
            self._m = m or {}
        def get(self, name: str):
            v = self._m.get(name)
            return (v, True) if v is not None else ("", False)

    def __init__(self, secrets_map: dict | None = None) -> None:
        self.log = self._Logger()
        self.secrets = self._Secrets(secrets_map or {})
        self.execution_id = "test-execution-id"
        self.flow_id = "test-flow-id"
        self.tenant_id = "test-tenant-id"


def test_get_plural_category_english_one_vs_other():
    # Independent oracle: English cardinal plurals have exactly two
    # categories — "one" for exactly 1, "other" for everything else — a
    # well-known linguistic fact about English, not a Babel artifact.
    ax = _TestContext()
    one = get_plural_category(ax, GetPluralCategoryInput(number=1, locale="en_US"))
    other = get_plural_category(ax, GetPluralCategoryInput(number=2, locale="en_US"))
    assert one.error == "" and one.category == "one"
    assert other.error == "" and other.category == "other"


def test_get_plural_category_czech_few():
    # Independent oracle: Czech (and other Slavic languages) has a "few"
    # category for small counts like 2-4 — a documented CLDR plural-rule
    # fact for cs, independent of this package's implementation.
    ax = _TestContext()
    result = get_plural_category(ax, GetPluralCategoryInput(number=3, locale="cs_CZ"))
    assert result.error == ""
    assert result.category == "few"


def test_get_plural_category_arabic_has_dual_and_zero():
    # Independent oracle: Arabic is well known for having distinct "zero",
    # "one", "two", "few", "many", and "other" plural categories — richer
    # than English.
    ax = _TestContext()
    zero = get_plural_category(ax, GetPluralCategoryInput(number=0, locale="ar"))
    two = get_plural_category(ax, GetPluralCategoryInput(number=2, locale="ar"))
    assert zero.error == "" and zero.category == "zero"
    assert two.error == "" and two.category == "two"


def test_get_plural_category_ordinal_form():
    # Independent oracle: English ordinals distinguish "one" (1st), "two"
    # (2nd), "few" (3rd) from "other" (4th, 5th, ...).
    ax = _TestContext()
    result = get_plural_category(ax, GetPluralCategoryInput(number=3, locale="en_US", form="ordinal"))
    assert result.error == ""
    assert result.category == "few"


def test_get_plural_category_bad_form_is_structured_error():
    ax = _TestContext()
    result = get_plural_category(ax, GetPluralCategoryInput(number=1, locale="en_US", form="fractional"))
    assert result.error == "UNKNOWN_FORM"
