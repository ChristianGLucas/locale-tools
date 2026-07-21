from gen.messages_pb2 import ParseTimeInput, ParsedTime
from nodes.parse_time import parse_time


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


def test_parse_time_en_us_12h():
    # Independent oracle: 3:04:05 PM is 15:04:05 in 24-hour time.
    ax = _TestContext()
    result = parse_time(ax, ParseTimeInput(text="3:04:05 PM", locale="en_US"))
    assert result.error == ""
    assert result.time == "15:04:05"


def test_parse_time_de_de_24h():
    ax = _TestContext()
    result = parse_time(ax, ParseTimeInput(text="15:04:05", locale="de_DE"))
    assert result.error == ""
    assert result.time == "15:04:05"


def test_parse_time_unparseable_text_is_structured_error():
    ax = _TestContext()
    result = parse_time(ax, ParseTimeInput(text="???", locale="en_US"))
    assert result.error == "UNPARSEABLE"
    assert result.time == ""
