# locale-tools

Composable **internationalization / locale-aware formatting & parsing** nodes
for the [Axiom](https://axiomide.com) marketplace, published as
`christiangeorgelucas/locale-tools`. Format and parse numbers, currencies,
percentages, dates/times, relative time, date/time intervals, lists, and
measurement units the way a native reader of a given locale expects — plus
CLDR pluralization-category lookup and rich locale metadata. Entirely
offline, deterministic, and stateless.

Written in **Python**, wrapping [Babel](https://babel.pocoo.org/)
(`python-babel/babel`), the standard CLDR-backed (Unicode Common Locale Data
Repository) internationalization library — **BSD-3-Clause**, zero runtime
dependencies. CLDR's own data files ship inside the Babel wheel under the
**Unicode-3.0** license (also permissive). Both licenses are verified from
source in this repo's build.

Every node is a small, stateless `(value, locale, options) -> result` call —
no session, no persisted state, no external network calls, no signup/API key.
Malformed input always returns a structured `error` token, never a crash.

## Use it from your agent or app

Every node in this package is a **live, auto-scaling API endpoint** on the
[Axiom](https://axiomide.com) marketplace — call it from an AI agent or your own
code, with nothing to self-host.

**📦 See it on the marketplace:**
https://dev.axiomide.com/marketplace/christiangeorgelucas/locale-tools@0.1.0

**Hook it up to an AI agent (MCP).** Add Axiom's hosted MCP server to any MCP
client and every node becomes a typed tool your agent can call — search the
catalog, inspect a schema, and invoke it directly.

```bash
# Claude Code
claude mcp add --transport http axiom https://api.axiomide.com/mcp \
  --header "Authorization: Bearer $AXIOM_API_KEY"
```

Claude Desktop, Cursor, or any config-based client:

```json
{
  "mcpServers": {
    "axiom": {
      "type": "http",
      "url": "https://api.axiomide.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_AXIOM_API_KEY" }
    }
  }
}
```

**Call it from the CLI.**

```bash
axiom invoke christiangeorgelucas/locale-tools/FormatDecimal --input '{ ... }'
```

**Call it over HTTP.**

```bash
curl -X POST https://api.axiomide.com/invocations/v1/nodes/christiangeorgelucas/locale-tools/0.1.0/FormatDecimal \
  -H "Authorization: Bearer $AXIOM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{ ... }'
```

> Input/output schema for each node is on the marketplace page above, or via
> `axiom inspect node christiangeorgelucas/locale-tools/FormatDecimal`.

### Get started free

Install the CLI:

```bash
# macOS / Linux — Homebrew
brew install axiomide/tap/axiom

# macOS / Linux — install script
curl -fsSL https://raw.githubusercontent.com/AxiomIDE/axiom-releases/main/install.sh | sh
```

**Windows:** download the `windows/amd64` `.zip` from the
[releases page](https://github.com/AxiomIDE/axiom-releases/releases), unzip it,
and put `axiom.exe` on your `PATH`.

Then `axiom version` to verify, `axiom login` (GitHub or Google) to authenticate,
and create an API key under **Console → API Keys**. Docs and sign-up at
**[axiomide.com](https://axiomide.com)**.

## Nodes

| Node | Input → Output | Purpose |
|---|---|---|
| `FormatDecimal` | `FormatDecimalInput` → `FormattedText` | Localized decimal number formatting (with optional compact notation) |
| `FormatCurrency` | `FormatCurrencyInput` → `FormattedText` | Localized currency formatting (standard/name/accounting, compact) |
| `FormatPercent` | `FormatPercentInput` → `FormattedText` | Localized percentage formatting |
| `FormatScientific` | `FormatScientificInput` → `FormattedText` | Localized scientific notation |
| `ParseDecimal` | `ParseDecimalInput` → `ParsedNumber` | Parse a localized decimal string back to a number |
| `GetCurrencyInfo` | `GetCurrencyInfoInput` → `CurrencyInfo` | Localized currency name/symbol + fraction-digit precision |
| `GetTerritoryCurrencies` | `GetTerritoryCurrenciesInput` → `TerritoryCurrencies` | Currencies a territory uses/used |
| `FormatDate` | `FormatDateInput` → `FormattedText` | Localized calendar-date formatting |
| `FormatTime` | `FormatTimeInput` → `FormattedText` | Localized time-of-day formatting |
| `FormatDatetime` | `FormatDatetimeInput` → `FormattedText` | Localized combined date+time formatting |
| `FormatTimedelta` | `FormatTimedeltaInput` → `FormattedText` | Localized relative time ("2 hours ago") |
| `FormatInterval` | `FormatIntervalInput` → `FormattedText` | Localized date/time range formatting |
| `ParseDate` | `ParseDateInput` → `ParsedDate` | Parse a localized date string back to ISO 8601 |
| `ParseTime` | `ParseTimeInput` → `ParsedTime` | Parse a localized time string back to ISO 8601 |
| `GetCalendarNames` | `GetCalendarNamesInput` → `CalendarNames` | Localized weekday/month/quarter/era/day-period names |
| `GetTimezoneName` | `GetTimezoneNameInput` → `TimezoneName` | Localized IANA-timezone display name + UTC offset |
| `FormatList` | `FormatListInput` → `FormattedText` | Localized grammatical list joining ("a, b, and c") |
| `FormatUnit` | `FormatUnitInput` → `FormattedText` | Localized measurement-unit formatting |
| `FormatCompoundUnit` | `FormatCompoundUnitInput` → `FormattedText` | Localized rate formatting ("5 km/h") |
| `GetPluralCategory` | `GetPluralCategoryInput` → `PluralCategory` | CLDR cardinal/ordinal plural-category lookup |
| `DescribeLocale` | `DescribeLocaleInput` → `LocaleInfo` | Rich locale metadata (names, direction, week data, number symbols) |

## Design

Every formatting node shares one output envelope, `FormattedText { text,
locale, error }`, so the family reads as one coherent domain rather than N
bespoke shapes. `locale` is always a CLDR/BCP-47 identifier string (e.g.
`"de_DE"`, `"fr"`, `"zh_Hant_TW"`; `-`/`_` are interchangeable on input).
Every output carries a stable `error` token (e.g. `BAD_LOCALE`,
`UNKNOWN_CURRENCY`, `UNPARSEABLE`) instead of throwing — malformed input is
data, not a crash. Bounds are enforced on every caller-controlled string
(locale identifiers, patterns, currency/unit codes, list length) before any
Babel/CLDR call, so pathological input fails fast and cheap rather than
driving unbounded parsing cost.

Built for the Axiom marketplace. MIT licensed.
