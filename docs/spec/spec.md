# ADIF Specification Reference

## About ADIF

The **Amateur Data Interchange Format** (ADIF) is the standard for exchanging Amateur Radio contact logs between software applications. Maintained by the [ADIF Developers Group](https://adif.org.uk), it defines field names, data types, enumerations, and record formats that logging programs use to import and export QSO data.

## Current Version

adif-mcp targets **ADIF 3.1.6** (released 2025-09-15).

- Official specification: [ADIF 3.1.6](https://adif.org.uk/316/ADIF_316.htm)
- Field definitions, data types, and enumerations are bundled as JSON resources within the adif-mcp package

## Key Concepts

### Record Formats

ADIF supports two record formats:

- **ADI** -- tag-based text format (e.g., `<CALL:5>KI7MT <BAND:3>20m <MODE:3>SSB`)
- **ADX** -- XML-based format for structured interchange

adif-mcp parses and validates both formats.

### Fields

ADIF defines ~150 standard fields covering:

- QSO basics: `CALL`, `BAND`, `MODE`, `FREQ`, `QSO_DATE`, `TIME_ON`, `RST_SENT`, `RST_RCVD`
- Location: `GRIDSQUARE`, `MY_GRIDSQUARE`, `DXCC`, `STATE`, `CNTY`
- Awards: `QSL_RCVD`, `LOTW_QSL_RCVD`, `EQSL_QSL_RCVD`, `IOTA`, `SOTA_REF`
- Contest: `CONTEST_ID`, `SRX`, `STX`, `SRX_STRING`, `STX_STRING`

### Enumerations

Many fields use controlled vocabularies (enumerations):

- `Band` -- HF through microwave (e.g., `160m`, `80m`, `40m`, `20m`, `15m`, `10m`)
- `Mode` / `Submode` -- operating modes (SSB, CW, FT8, RTTY, etc.)
- `DXCC_Entity_Code` -- country/entity codes
- `QSL_Rcvd` / `QSL_Sent` -- confirmation status flags

Use the `read_specification_resource` and `search_enumerations` MCP tools to explore enumerations programmatically.

### APP_ Fields

Applications can define custom fields using the `APP_` prefix (e.g., `APP_ADIF-MCP_OP`). These are application-specific extensions that don't conflict with the standard. See the [Program ID Policy](../program-id-policy.md) for adif-mcp's registered Program IDs and APP_ field conventions.

## Spec Coverage

adif-mcp bundles the complete ADIF 3.1.6 specification as structured JSON, including all fields, data types, and enumerations. The `read_specification_resource` and `search_enumerations` MCP tools provide full programmatic access.

*ADIF is a trademark of the ADIF Developers Group. This project is an independent implementation.*
