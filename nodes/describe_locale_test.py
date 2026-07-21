from gen.messages_pb2 import DescribeLocaleInput, LocaleInfo
from nodes.describe_locale import describe_locale


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


def test_describe_locale_de_de():
    # Independent oracle: Germany's week starts on Monday (ISO weekday 1)
    # with a Saturday/Sunday weekend (ISO 6, 7); the German native name for
    # Germany is "Deutschland"; German is written left-to-right; and German
    # number formatting uses "," as the decimal separator and "." as the
    # grouping separator — all real-world, independently-known facts.
    ax = _TestContext()
    result = describe_locale(ax, DescribeLocaleInput(locale="de_DE"))
    assert result.error == ""
    assert result.locale == "de_DE"
    assert result.language == "de"
    assert result.territory == "DE"
    assert result.script == ""
    assert result.display_name == "Deutsch (Deutschland)"
    assert result.english_name == "German (Germany)"
    assert result.text_direction == "ltr"
    assert result.first_week_day == 1
    assert list(result.weekend_days) == [6, 7]
    assert result.decimal_symbol == ","
    assert result.group_symbol == "."
    assert result.percent_symbol == "%"


def test_describe_locale_arabic_is_rtl():
    # Independent oracle: Arabic script is written right-to-left.
    ax = _TestContext()
    result = describe_locale(ax, DescribeLocaleInput(locale="ar"))
    assert result.error == ""
    assert result.text_direction == "rtl"


def test_describe_locale_script_subtag():
    # Independent oracle: Traditional Chinese as used in Taiwan is tagged
    # with the Han-Traditional script subtag "Hant".
    ax = _TestContext()
    result = describe_locale(ax, DescribeLocaleInput(locale="zh_Hant_TW"))
    assert result.error == ""
    assert result.language == "zh"
    assert result.script == "Hant"
    assert result.territory == "TW"


def test_describe_locale_display_locale_translates_name():
    # Independent oracle: "Germany" translated into French is "Allemagne",
    # and German is "allemand" — ordinary French vocabulary.
    ax = _TestContext()
    result = describe_locale(ax, DescribeLocaleInput(locale="de_DE", display_locale="fr"))
    assert result.error == ""
    assert result.display_name == "allemand (Allemagne)"
    # english_name is always English regardless of display_locale.
    assert result.english_name == "German (Germany)"


def test_describe_locale_bad_locale_is_structured_error():
    ax = _TestContext()
    result = describe_locale(ax, DescribeLocaleInput(locale="not a locale!!"))
    assert result.error == "BAD_LOCALE"
