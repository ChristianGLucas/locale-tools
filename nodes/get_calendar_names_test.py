from gen.messages_pb2 import GetCalendarNamesInput, CalendarNames
from nodes.get_calendar_names import get_calendar_names


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


def test_get_calendar_names_weekdays_abbreviated_en_us():
    # Independent oracle: English weekday abbreviations in CLDR's
    # Monday-first canonical order.
    ax = _TestContext()
    result = get_calendar_names(
        ax, GetCalendarNamesInput(locale="en_US", field="weekdays", width="abbreviated")
    )
    assert result.error == ""
    assert list(result.names) == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def test_get_calendar_names_months_abbreviated_en_us():
    ax = _TestContext()
    result = get_calendar_names(
        ax, GetCalendarNamesInput(locale="en_US", field="months", width="abbreviated")
    )
    assert result.error == ""
    assert list(result.names) == [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]


def test_get_calendar_names_eras_abbreviated_en_us():
    # Independent oracle: the Gregorian calendar's two eras are BC and AD.
    ax = _TestContext()
    result = get_calendar_names(ax, GetCalendarNamesInput(locale="en_US", field="eras", width="abbreviated"))
    assert result.error == ""
    assert list(result.names) == ["BC", "AD"]


def test_get_calendar_names_quarters_wide_en_us():
    ax = _TestContext()
    result = get_calendar_names(ax, GetCalendarNamesInput(locale="en_US", field="quarters"))
    assert result.error == ""
    assert list(result.names) == ["1st quarter", "2nd quarter", "3rd quarter", "4th quarter"]


def test_get_calendar_names_unknown_field_is_structured_error():
    ax = _TestContext()
    result = get_calendar_names(ax, GetCalendarNamesInput(locale="en_US", field="fortnights"))
    assert result.error == "UNKNOWN_FIELD"
