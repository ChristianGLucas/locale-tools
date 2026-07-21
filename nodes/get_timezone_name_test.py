from gen.messages_pb2 import GetTimezoneNameInput, TimezoneName
from nodes.get_timezone_name import get_timezone_name


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


def test_get_timezone_name_default_reference_is_standard_time():
    # Independent oracle: the package's fixed reference date (Jan 1) falls
    # outside US daylight saving time, so New York is on EST at UTC-5.
    ax = _TestContext()
    result = get_timezone_name(ax, GetTimezoneNameInput(timezone="America/New_York", locale="en_US"))
    assert result.error == ""
    assert result.display_name == "Eastern Standard Time"
    assert result.gmt_offset == "GMT-05:00"


def test_get_timezone_name_explicit_july_instant_is_daylight_time():
    # Independent oracle: in July, US Eastern time observes daylight
    # saving (EDT, UTC-4) — a real-world DST-calendar fact.
    ax = _TestContext()
    result = get_timezone_name(
        ax,
        GetTimezoneNameInput(timezone="America/New_York", locale="en_US", at="2026-07-20T12:00:00"),
    )
    assert result.error == ""
    assert result.display_name == "Eastern Daylight Time"
    assert result.gmt_offset == "GMT-04:00"


def test_get_timezone_name_short_width():
    ax = _TestContext()
    result = get_timezone_name(
        ax, GetTimezoneNameInput(timezone="Europe/London", locale="en_US", width="short")
    )
    assert result.error == ""
    assert result.display_name == "GMT"


def test_get_timezone_name_unknown_timezone_is_structured_error():
    ax = _TestContext()
    result = get_timezone_name(ax, GetTimezoneNameInput(timezone="Not/AZone", locale="en_US"))
    assert result.error == "UNKNOWN_TIMEZONE"
