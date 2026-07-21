from gen.messages_pb2 import FormatDateInput, FormattedText
from nodes.format_date import format_date


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


def test_format_date_full_en_us():
    # Independent oracle: 2026-07-20 is a Monday (a calendar fact
    # independently verifiable, not derived from Babel), and "full" style
    # spells out the weekday and month name in English.
    ax = _TestContext()
    result = format_date(ax, FormatDateInput(date="2026-07-20", locale="en_US", format="full"))
    assert result.error == ""
    assert result.text == "Monday, July 20, 2026"


def test_format_date_medium_de_de_day_month_year_order():
    # Independent oracle: German date convention is day.month.year with
    # period separators.
    ax = _TestContext()
    result = format_date(ax, FormatDateInput(date="2026-07-20", locale="de_DE"))
    assert result.error == ""
    assert result.text == "20.07.2026"


def test_format_date_bad_date_is_structured_error_not_crash():
    ax = _TestContext()
    result = format_date(ax, FormatDateInput(date="not-a-date", locale="en_US"))
    assert result.error == "BAD_DATE"
    assert result.text == ""
