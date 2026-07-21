from gen.messages_pb2 import FormatScientificInput, FormattedText
from nodes.format_scientific import format_scientific


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


def test_format_scientific_en_us():
    # Independent oracle: 12345 in scientific notation is 1.2345 x 10^4,
    # and CLDR's exponential symbol is a plain "E".
    ax = _TestContext()
    result = format_scientific(ax, FormatScientificInput(value=12345.0, locale="en_US"))
    assert result.error == ""
    assert result.text == "1.2345E4"


def test_format_scientific_bad_locale_is_structured_error():
    ax = _TestContext()
    result = format_scientific(ax, FormatScientificInput(value=1.0, locale="!!!"))
    assert result.error == "BAD_LOCALE"
    assert result.text == ""
