---
hide:
  - navigation
---

# ADIF Basics

The **Amateur Data Interchange Format** (ADIF) is the universal standard for Amateur Radio logging. Nearly every logging program -- from paper-log converters to cloud-based platforms -- speaks ADIF for import and export.

## Records

An ADIF file is a sequence of QSO records. Each record contains tagged fields:

```
<CALL:5>KI7MT <BAND:3>20m <MODE:3>SSB <QSO_DATE:8>20250315 <TIME_ON:4>1830 <RST_SENT:2>59 <RST_RCVD:2>59 <EOR>
```

- Each field is wrapped in angle brackets: `<FIELD_NAME:LENGTH>VALUE`
- `<EOR>` marks the end of a record
- Files may include an optional header ending with `<EOH>`

## Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `CALL` | String | Callsign of the station worked |
| `BAND` | Enumeration | Operating band (e.g., `20m`, `40m`) |
| `MODE` | Enumeration | Operating mode (e.g., `SSB`, `CW`, `FT8`) |
| `FREQ` | Number | Frequency in MHz |
| `QSO_DATE` | Date | Contact date (YYYYMMDD) |
| `TIME_ON` | Time | Contact start time (HHMM or HHMMSS, UTC) |
| `RST_SENT` | String | Signal report sent |
| `RST_RCVD` | String | Signal report received |
| `GRIDSQUARE` | String | Maidenhead locator of the station worked |

## Data Types

ADIF defines several data types:

- **String** -- free-form text
- **Number** -- integer or decimal
- **Date** -- 8-digit date (YYYYMMDD)
- **Time** -- 4 or 6-digit UTC time (HHMM or HHMMSS)
- **Enumeration** -- value from a controlled list (Band, Mode, DXCC, etc.)
- **Boolean** -- `Y` or `N`

## Enumerations

Many fields are constrained to specific values defined by the spec. For example, `BAND` must be one of `2190m`, `630m`, `560m`, `160m`, `80m`, ... through to `submm`. Use the `read_specification_resource` MCP tool to explore enumerations programmatically.

## Validation

adif-mcp validates records against the ADIF 3.1.6 specification:

- Field names must be recognized (standard or APP_ prefixed)
- Data types must match (e.g., dates must be valid YYYYMMDD)
- Enumeration values must be in the allowed set
- Length tags must match actual value lengths

Use the `validate_adif_record` MCP tool to check any ADIF string.
