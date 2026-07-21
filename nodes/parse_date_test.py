from gen.messages_pb2 import ParseDateInput, ParsedDate
from nodes.parse_date import parse_date


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


def test_parse_date_short_en_us():
    # Independent oracle: US short-date order is month/day/year, so
    # "7/20/26" is 2026-07-20.
    ax = _TestContext()
    result = parse_date(ax, ParseDateInput(text="7/20/26", locale="en_US", format="short"))
    assert result.error == ""
    assert result.date == "2026-07-20"


def test_parse_date_short_de_de():
    # Independent oracle: German short-date order is day.month.year.
    ax = _TestContext()
    result = parse_date(ax, ParseDateInput(text="20.07.26", locale="de_DE", format="short"))
    assert result.error == ""
    assert result.date == "2026-07-20"


def test_parse_date_round_trip_with_format_date_short():
    from nodes.format_date import format_date
    from gen.messages_pb2 import FormatDateInput

    ax = _TestContext()
    formatted = format_date(ax, FormatDateInput(date="2026-07-20", locale="en_US", format="short"))
    assert formatted.error == ""
    parsed = parse_date(ax, ParseDateInput(text=formatted.text, locale="en_US", format="short"))
    assert parsed.error == ""
    assert parsed.date == "2026-07-20"


def test_parse_date_spelled_month_can_fail_gracefully_not_crash():
    # Babel's date parser is documented (see the proto field comment) to be
    # unreliable on spelled-out month/weekday styles even for its own
    # output — this asserts the failure mode is a clean structured error,
    # never a raised exception reaching the caller.
    ax = _TestContext()
    result = parse_date(ax, ParseDateInput(text="Jul 20, 2026", locale="en_US", format="medium"))
    assert result.error == "UNPARSEABLE"
    assert result.date == ""


def test_parse_date_unparseable_text_is_structured_error():
    ax = _TestContext()
    result = parse_date(ax, ParseDateInput(text="???", locale="en_US"))
    assert result.error == "UNPARSEABLE"
