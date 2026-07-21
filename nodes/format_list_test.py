from gen.messages_pb2 import FormatListInput, FormattedText
from nodes.format_list import format_list


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


def test_format_list_standard_en_us():
    # Independent oracle: English list conjunction is a serial ("Oxford")
    # comma before "and".
    ax = _TestContext()
    result = format_list(ax, FormatListInput(items=["a", "b", "c"], locale="en_US"))
    assert result.error == ""
    assert result.text == "a, b, and c"


def test_format_list_standard_es_uses_y_not_e():
    # Independent oracle: Spanish "y" (and) is a well-known grammatical
    # convention (it becomes "e" only before a word starting with "i"/"hi",
    # which none of these items are).
    ax = _TestContext()
    result = format_list(ax, FormatListInput(items=["a", "b", "c"], locale="es"))
    assert result.error == ""
    assert result.text == "a, b y c"


def test_format_list_or_style():
    ax = _TestContext()
    result = format_list(ax, FormatListInput(items=["a", "b", "c"], locale="en_US", style="or"))
    assert result.error == ""
    assert result.text == "a, b, or c"


def test_format_list_empty_items_returns_empty_string_not_error():
    ax = _TestContext()
    result = format_list(ax, FormatListInput(items=[], locale="en_US"))
    assert result.error == ""
    assert result.text == ""


def test_format_list_bad_style_is_structured_error():
    ax = _TestContext()
    result = format_list(
        ax, FormatListInput(items=["a", "b"], locale="en_US", style="not-a-style")
    )
    assert result.error == "BAD_VALUE"
