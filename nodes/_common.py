"""Shared helpers for christiangeorgelucas/locale-tools nodes.

Centralizes locale parsing (normalizing "de-DE" / "de_DE" alike), ISO
date/time parsing, and the structured-error contract every node follows: a
node never raises out to the caller — on malformed input it returns its
output message with the text/value fields empty and `error` set to one of
the stable tokens documented on that message.

Also centralizes the input-size bounds enforced BEFORE any Babel call, so a
caller-controlled string can't drive unbounded parsing cost.
"""
from __future__ import annotations

import datetime as _dt
import re as _re

from babel import Locale, UnknownLocaleError

# babel.Locale.parse is permissive about trailing junk: it splits on the
# separator and silently drops any component that doesn't look like a
# language/script/territory/variant subtag rather than rejecting the whole
# string — e.g. "en_US; DROP TABLE x;" parses to plain "en" instead of
# raising. That is surprising for a node whose job is to validate a clean
# locale identifier, so we constrain the accepted character set ourselves
# BEFORE handing anything to Babel: only what a real CLDR/BCP-47 identifier
# ever contains (letters, digits, '_', '-', '@' for a modifier like
# "de_AT@euro", '.' for an encoding suffix like "en_US.UTF-8").
_LOCALE_CHARS = _re.compile(r"^[A-Za-z0-9_@.\-]+$")

# Bounds enforced before any Babel/locale-data call. These exist to put a
# hard, tested ceiling on caller-controlled cost, not to be generous
# defaults — legitimate locale identifiers, ISO dates, currency/unit codes,
# and CLDR patterns are all a handful of characters.
MAX_LOCALE_LEN = 64
MAX_PATTERN_LEN = 128
MAX_CODE_LEN = 32
MAX_DATETIME_LEN = 64
MAX_LIST_ITEMS = 1000
MAX_LIST_ITEM_LEN = 1000

# A fixed reference "now" used anywhere Babel would otherwise default to the
# real wall-clock date (e.g. territory-currency and timezone-offset
# lookups). Using a pinned date keeps a node's output deterministic across
# runs/days rather than silently drifting with the calendar; it is well
# within the validity range of every currently-active CLDR currency/zone.
REFERENCE_DATE = _dt.date(2026, 1, 1)
HISTORICAL_START_DATE = _dt.date(1800, 1, 1)


class LocaleToolsError(Exception):
    """Carries a stable machine-readable error token plus a human message."""

    def __init__(self, token: str, message: str = "") -> None:
        super().__init__(message or token)
        self.token = token


def _check_len(value: str, max_len: int, label: str) -> None:
    if value is not None and len(value) > max_len:
        raise LocaleToolsError(
            "BAD_VALUE", f"{label} is {len(value)} chars, exceeding the {max_len} limit"
        )


def parse_locale(locale_str: str) -> Locale:
    """Parse a CLDR/BCP-47 locale identifier ("de_DE" or "de-DE") into a
    babel.Locale. Raises LocaleToolsError(BAD_LOCALE) on anything empty,
    oversized, or unparseable/unknown to CLDR."""
    if not locale_str:
        raise LocaleToolsError("BAD_LOCALE", "locale is required")
    _check_len(locale_str, MAX_LOCALE_LEN, "locale")
    if not _LOCALE_CHARS.match(locale_str):
        raise LocaleToolsError(
            "BAD_LOCALE", f"locale {locale_str!r} contains characters no CLDR identifier uses"
        )
    normalized = locale_str.replace("-", "_")
    try:
        return Locale.parse(normalized)
    except (UnknownLocaleError, ValueError) as e:
        raise LocaleToolsError("BAD_LOCALE", f"unrecognized locale {locale_str!r}: {e}") from e


def check_pattern(pattern: str, label: str = "format") -> None:
    _check_len(pattern, MAX_PATTERN_LEN, label)


def check_code(code: str, label: str) -> None:
    _check_len(code, MAX_CODE_LEN, label)


def parse_iso_date(s: str) -> _dt.date:
    _check_len(s, MAX_DATETIME_LEN, "date")
    try:
        return _dt.date.fromisoformat(s)
    except ValueError as e:
        raise LocaleToolsError("BAD_DATE", f"unparseable ISO 8601 date {s!r}: {e}") from e


def parse_iso_time(s: str) -> _dt.time:
    _check_len(s, MAX_DATETIME_LEN, "time")
    try:
        return _dt.time.fromisoformat(s)
    except ValueError as e:
        raise LocaleToolsError("BAD_DATE", f"unparseable ISO 8601 time {s!r}: {e}") from e


def parse_iso_datetime(s: str) -> _dt.datetime:
    """Parse an ISO 8601 datetime. A trailing 'Z'/offset is accepted and then
    dropped — Babel formats the naive wall-clock fields as given, with no
    timezone conversion, so we normalize to naive up front."""
    _check_len(s, MAX_DATETIME_LEN, "datetime")
    normalized = s[:-1] + "+00:00" if s.endswith("Z") else s
    try:
        parsed = _dt.datetime.fromisoformat(normalized)
    except ValueError as e:
        raise LocaleToolsError("BAD_DATE", f"unparseable ISO 8601 datetime {s!r}: {e}") from e
    if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
    return parsed


def parse_iso_instant(s: str):
    """Parse an ISO 8601 date OR datetime, trying the shorter date-only form
    first (a bare 10-char date is not a valid datetime)."""
    _check_len(s, MAX_DATETIME_LEN, "instant")
    if len(s) == 10:
        try:
            return _dt.date.fromisoformat(s)
        except ValueError:
            pass
    try:
        return parse_iso_datetime(s)
    except LocaleToolsError:
        raise LocaleToolsError("BAD_DATE", f"unparseable ISO 8601 date/datetime: {s!r}")


def check_list(items, label: str = "items") -> None:
    if len(items) > MAX_LIST_ITEMS:
        raise LocaleToolsError(
            "BAD_VALUE", f"{label} has {len(items)} entries, exceeding the {MAX_LIST_ITEMS} limit"
        )
    for i, item in enumerate(items):
        if len(item) > MAX_LIST_ITEM_LEN:
            raise LocaleToolsError(
                "BAD_VALUE",
                f"{label}[{i}] is {len(item)} chars, exceeding the {MAX_LIST_ITEM_LEN} limit",
            )


# Babel's Locale.first_week_day / weekend_start / weekend_end are 0=Monday..
# 6=Sunday. The package's public contract uses ISO 8601 weekday numbering
# (1=Monday..7=Sunday) since that is the convention most callers expect.
def to_iso_weekday(babel_weekday: int) -> int:
    return babel_weekday + 1
