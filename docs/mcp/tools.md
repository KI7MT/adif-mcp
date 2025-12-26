# Tools (API Surface)

The ADIF-MCP server exposes **11 verified tools** categorized by function. These tools operate strictly against the embedded ADIF 3.1.6 (2025-09-15) specification.

### 1. Core Validation & Parsing
* **`validate_adif_record(adif_string)`**
* **Input**: Raw ADIF text (e.g., `<CALL:5>KI7MT...`).
* **Output**: JSON report containing the parsed record, a status (`success`/`invalid`), and specific error messages if data types (like 'Number') are violated.
* **`parse_adif(adif_text)`**
* **Input**: A string containing one or multiple ADIF records.
* **Output**: A list of parsed dictionaries with normalized uppercase keys (e.g., `{"CALL": "KI7MT"}`).

### 2. Specification Intelligence
* **`search_enumerations(search_term)`**
* **Description**: Surgically searches deep within the ADIF 3.1.6 `Records` structure.
* **Capability**: Resolves code collisions (e.g., distinguishing `MA.54` Moscow from `MA.291` Massachusetts).
* **`read_specification_resource(resource_name)`**
* **Description**: Retrieves the raw JSON for any specification module (e.g., `band`, `mode`, `fields`).
* **Capability**: Uses a "Smart Router" to handle modular file loading without hitting 1MB limits.
* **`search_adif_spec(search_term)`**
* **Description**: Performs a global search across `fields`, `datatypes`, and `enumerations`.
* **`list_enumeration_groups()`**
* **Description**: Lists all available enumeration categories (e.g., `DXCC_Entity_Code`, `Submode`).
* **`get_enumeration_values(group_name)`**
* **Description**: Returns the valid values for a specific enumeration group.

### 3. Geospatial Utilities
* **`calculate_distance(start, end)`**
* **Description**: Calculates the Great Circle distance (km) between two Maidenhead locators.
* **`calculate_heading(start, end)`**
* **Description**: Calculates the initial beam heading (azimuth) between two locators.

### 4. System Metadata
* **`get_version_info()`**
* **Description**: Returns the active Service Version (v0.4.3) and ADIF Spec Version (3.1.6).
* **`get_service_metadata()`**
* **Description**: Provides build timestamps and maintainer details.
