# Tools Reference

ADIF-MCP exposes **7 tools** and **1 resource** via the Model Context Protocol. All tools operate locally against the bundled ADIF 3.1.6 specification -- no network calls required.

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

Plus 1 MCP resource: `adif://system/version`

---

## Example Usage

The examples below show what to ask your AI agent and what the tool returns. You don't call these tools directly -- your agent discovers and invokes them automatically.

### validate_adif_record

Validates an ADIF record string against the 3.1.6 specification. Checks that field names exist in the spec and that data types match (e.g., Number fields contain valid numbers).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `adif_string` | `str` | Yes | Raw ADIF record text |

**Ask your agent:**

> "Validate this ADIF record: `<CALL:5>KI7MT <BAND:3>20m <MODE:3>FT8 <FREQ:6>14.074 <QSO_DATE:8>20250315 <EOR>`"

**Returns:**

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

**With a bad field:**

> "Validate this: `<FREQ:3>abc <EOR>`"

```json
{
  "status": "invalid",
  "errors": ["Field 'FREQ' expects Number, got 'abc'."],
  "warnings": [],
  "record": {"FREQ": "abc"}
}
```

---

### parse_adif

Streaming parser for large ADIF files. Reads from an absolute file path and returns records with pagination support.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `str` | Yes | -- | Absolute path to the `.adi` file |
| `start_at` | `int` | No | `1` | First record number to return (1-based) |
| `limit` | `int` | No | `20` | Maximum records to return |

**Ask your agent:**

> "Parse my ADIF log at /home/ki7mt/logs/field-day-2025.adi and show the first 5 records"

**Returns:**

```
FILE: /home/ki7mt/logs/field-day-2025.adi
TOTAL RECORDS: 1247
DISPLAYING: 1 to 5

--- RECORD 1 ---
<CALL:5>KI7MT <BAND:3>20m <MODE:3>FT8 <QSO_DATE:8>20250315 <EOR>

--- RECORD 2 ---
<CALL:4>W1AW <BAND:3>40m <MODE:2>CW <QSO_DATE:8>20250316 <EOR>
...
```

**Paging through a large file:**

> "Show me records 100 through 110 from that log"

The agent calls `parse_adif` with `start_at=100, limit=11`.

---

### read_specification_resource

Loads a named ADIF 3.1.6 specification module as raw JSON. The server bundles 30 JSON files covering fields, data types, and all enumerations. A smart router tries enumeration files first, then general files, then falls back to the `all.json` catalog.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resource_name` | `str` | Yes | Spec module name (e.g., `band`, `mode`, `fields`, `dxcc_entity_code`) |

**Ask your agent:**

> "What are the valid ADIF bands and their frequency ranges?"

**Returns:** (truncated)

```json
{
  "Adif": {
    "Enumerations": {
      "Band": {
        "Records": {
          "2190m": {"Lower Freq (MHz)": 0.1357, "Upper Freq (MHz)": 0.1378},
          "630m": {"Lower Freq (MHz)": 0.472, "Upper Freq (MHz)": 0.479},
          "160m": {"Lower Freq (MHz)": 1.8, "Upper Freq (MHz)": 2.0},
          "..."
        }
      }
    }
  }
}
```

**Other useful queries:**

> "What data type is the FREQ field in the ADIF spec?"

> "Show me the ADIF mode enumeration -- is FT8 a mode or a submode?"

> "What are the valid QSL_RCVD values?"

---

### search_enumerations

Searches the `Primary_Administrative_Subdivision` enumeration records. Matches on subdivision code or name. Resolves international code collisions where the same code belongs to different DXCC entities.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search_term` | `str` | Yes | Code or name to search (case-insensitive) |

**Ask your agent:**

> "Search the ADIF subdivision enumerations for 'MA' -- is that Massachusetts or Moscow?"

**Returns:**

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

**Other examples:**

> "Find all subdivisions matching 'Alaska'"

> "What DXCC entity does subdivision code 'QC' belong to?"

---

### calculate_distance

Calculates the Great Circle distance in kilometers between two Maidenhead grid locators using the Haversine formula. Supports 4-character (grid square) and 6-character (sub-square) locators.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start` | `str` | Yes | Maidenhead grid locator (e.g., `DN13`, `FN31pr`) |
| `end` | `str` | Yes | Maidenhead grid locator |

**Ask your agent:**

> "How far is it from DN13 in Idaho to JN48 in central Europe?"

**Returns:**

```json
8455.2
```

> "What's the distance between my grid FN31 and VK3 in Melbourne (QF22)?"

---

### calculate_heading

Calculates the initial beam heading (azimuth in degrees) from one Maidenhead grid locator to another. Use this to determine antenna pointing direction.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start` | `str` | Yes | Maidenhead grid locator (your QTH) |
| `end` | `str` | Yes | Maidenhead grid locator (target station) |

**Ask your agent:**

> "What heading should I point my antenna from DN13 to work JN48?"

**Returns:**

```json
42.7
```

> "I'm in DN13 and want to work Japan. What beam heading to PM95?"

---

### get_version_info

Returns the ADIF-MCP service version and the ADIF specification version it implements.

**Parameters:** None

**Ask your agent:**

> "What version of adif-mcp am I running?"

**Returns:**

```json
{
  "service_version": "0.6.2",
  "adif_spec_version": "3.1.6"
}
```

---

### Resource: adif://system/version

In addition to the 7 tools, ADIF-MCP exposes one MCP resource at `adif://system/version`. This provides the same version information as `get_version_info` but via the MCP resource protocol (read-only, agent-discoverable).

**URI:** `adif://system/version`

```json
{
  "service_version": "0.6.2",
  "adif_spec_version": "3.1.6",
  "status": "online"
}
```
