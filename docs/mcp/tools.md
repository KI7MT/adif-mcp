# Tools Reference

ADIF-MCP exposes **7 tools** and **1 resource** via the Model Context Protocol. All tools operate locally against the bundled ADIF 3.1.6 specification -- no network calls required.

---

## validate_adif_record

Validates an ADIF record string against the 3.1.6 specification. Checks that field names exist in the spec and that data types match (e.g., Number fields contain valid numbers).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `adif_string` | `str` | Yes | Raw ADIF record text |

**Example input:**

```
<CALL:5>KI7MT <BAND:3>20m <MODE:3>FT8 <FREQ:6>14.074 <QSO_DATE:8>20250315 <EOR>
```

**Example output:**

```json
{
  "status": "success",
  "errors": [],
  "warnings": [],
  "record": {
    "CALL": "KI7MT",
    "BAND": "20m",
    "MODE": "FT8",
    "FREQ": "14.074",
    "QSO_DATE": "20250315"
  }
}
```

If a field violates its data type:

```json
{
  "status": "invalid",
  "errors": ["Field 'FREQ' expects Number, got 'abc'."],
  "warnings": [],
  "record": {"FREQ": "abc"}
}
```

---

## parse_adif

Streaming parser for large ADIF files. Reads from an absolute file path and returns records with pagination support.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file_path` | `str` | Yes | -- | Absolute path to the `.adi` file |
| `start_at` | `int` | No | `1` | First record number to return (1-based) |
| `limit` | `int` | No | `20` | Maximum records to return |

**Example input:**

```json
{
  "file_path": "/home/user/logs/mylog.adi",
  "start_at": 1,
  "limit": 5
}
```

**Example output:**

```
FILE: /home/user/logs/mylog.adi
TOTAL RECORDS: 1247
DISPLAYING: 1 to 5

--- RECORD 1 ---
<CALL:5>KI7MT <BAND:3>20m <MODE:3>FT8 <QSO_DATE:8>20250315 <EOR>

--- RECORD 2 ---
<CALL:4>W1AW <BAND:3>40m <MODE:2>CW <QSO_DATE:8>20250316 <EOR>
...
```

!!! tip
    Use `start_at` and `limit` to page through large files without loading everything at once.

---

## read_specification_resource

Loads a named ADIF 3.1.6 specification module as raw JSON. Handles the modular file structure (30 JSON files) with a smart router that tries enumeration files first, then general files, then falls back to the `all.json` catalog.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `resource_name` | `str` | Yes | Spec module name (e.g., `band`, `mode`, `fields`, `dxcc_entity_code`, `primary_administrative_subdivision`) |

**Example input:**

```json
{"resource_name": "band"}
```

**Example output:** (truncated)

```json
{
  "Adif": {
    "Enumerations": {
      "Band": {
        "Records": {
          "2190m": {"Lower Freq (MHz)": 0.1357, "Upper Freq (MHz)": 0.1378},
          "630m": {"Lower Freq (MHz)": 0.472, "Upper Freq (MHz)": 0.479},
          "...": "..."
        }
      }
    }
  }
}
```

---

## search_enumerations

Searches the `Primary_Administrative_Subdivision` enumeration records. Matches on subdivision code or name. Useful for resolving international code collisions (e.g., `MA` = Moscow in DXCC 54 vs Massachusetts in DXCC 291).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `search_term` | `str` | Yes | Code or name to search (case-insensitive) |

**Example input:**

```json
{"search_term": "MA"}
```

**Example output:**

```json
{
  "MA.54": {
    "Code": "MA",
    "Primary Administrative Subdivision": "Moscow",
    "DXCC Entity Code": "54"
  },
  "MA.291": {
    "Code": "MA",
    "Primary Administrative Subdivision": "Massachusetts",
    "DXCC Entity Code": "291"
  }
}
```

---

## calculate_distance

Calculates the Great Circle distance in kilometers between two Maidenhead grid locators using the Haversine formula. Computed locally -- no external API calls.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `start` | `str` | Yes | Maidenhead grid locator (e.g., `DN13`, `FN31pr`) |
| `end` | `str` | Yes | Maidenhead grid locator |

**Example input:**

```json
{"start": "DN13", "end": "JN48"}
```

**Example output:**

```json
8455.2
```

---

## calculate_heading

Calculates the initial beam heading (azimuth in degrees) from one Maidenhead grid locator to another. Use this to determine antenna pointing direction.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `start` | `str` | Yes | Maidenhead grid locator (your QTH) |
| `end` | `str` | Yes | Maidenhead grid locator (target station) |

**Example input:**

```json
{"start": "DN13", "end": "JN48"}
```

**Example output:**

```json
42.7
```

---

## get_version_info

Returns the ADIF-MCP service version and the ADIF specification version it implements. No parameters required.

**Parameters:** None

**Example output:**

```json
{
  "service_version": "0.6.1",
  "adif_spec_version": "3.1.6"
}
```

---

## Resource: adif://system/version

In addition to the 7 tools above, ADIF-MCP exposes one MCP resource at `adif://system/version`. This provides the same version information as `get_version_info` but via the MCP resource protocol (read-only, agent-discoverable).

**URI:** `adif://system/version`

**Example output:**

```json
{
  "service_version": "0.6.1",
  "adif_spec_version": "3.1.6",
  "status": "online"
}
```

---

## Tool Summary

| Tool | Category | Description |
|------|----------|-------------|
| `validate_adif_record` | Validation | Validate ADIF records against 3.1.6 |
| `parse_adif` | Parsing | Stream and paginate ADIF log files |
| `read_specification_resource` | Spec Intelligence | Load any spec module as JSON |
| `search_enumerations` | Spec Intelligence | Search administrative subdivision records |
| `calculate_distance` | Geospatial | Great Circle distance between grids |
| `calculate_heading` | Geospatial | Beam heading between grids |
| `get_version_info` | System | Service and spec version |
