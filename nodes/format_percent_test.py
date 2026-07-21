from gen.messages_pb2 import FormatPercentInput, FormattedText
from nodes.format_percent import format_percent


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


def test_format_percent_en_us():
    # Independent oracle: CLDR's default percent pattern has no decimal
    # places, so 0.256 rounds to 26%.
    ax = _TestContext()
    result = format_percent(ax, FormatPercentInput(value=0.256, locale="en_US"))
    assert result.error == ""
    assert result.text == "26%"


def test_format_percent_de_de_space_before_sign():
    # Independent oracle: German convention inserts a non-breaking space
    # before the "%" sign.
    ax = _TestContext()
    result = format_percent(ax, FormatPercentInput(value=0.256, locale="de_DE"))
    assert result.error == ""
    assert result.text == "26\xa0%"


def test_format_percent_bad_locale_is_structured_error():
    ax = _TestContext()
    result = format_percent(ax, FormatPercentInput(value=0.5, locale=""))
    assert result.error == "BAD_LOCALE"
    assert result.text == ""
