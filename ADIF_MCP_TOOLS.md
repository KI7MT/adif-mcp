# ADIF-MCP Tool Catalog

This document outlines the Model Context Protocol (MCP) tools provided by this service.

## Core Tools (Implemented)
These tools form the "Technical Bedrock" and are currently active in `server.py`.

- **`get_service_metadata`**
  - **Purpose:** Service discovery. Returns the active ADIF specification version (3.1.5) and supported features.
  - **Guardrail:** Ensures the AI agent knows exactly what schema version to use.

- **`validate_qso`**
  - **Purpose:** Data integrity. Accepts a QSO object and validates it against the strict Pydantic ADIF model.
  - **Guardrail:** "No Hallucinations" — prevents the AI from inventing non-existent ADIF fields.

- **`calculate_distance`**
  - **Purpose:** Analysis. Computes the great-circle distance (km) between two Maidenhead grid locators.
  - **Guardrail:** "Sovereign" — performed locally using the Haversine formula, no external API calls.

- **`lookup_country`**
  - **Purpose:** Enrichment. Resolves a callsign to its DXCC Entity, Continent, and CQ/ITU Zones.
  - **Guardrail:** "Sovereign" — uses a local prefix map (cty.dat logic) instead of cloud lookups.

## Utility Tools (Implemented)
These tools provide essential data manipulation for the "Average" ham operator.

- **`calculate_heading`**: Computes the beam heading (azimuth) between two locators to assist with antenna pointing.
- **`parse_adif`**: Parses raw `.adi` text blocks into structured, validated JSON records.
- **`normalize_band`**: Canonicalizes frequency or band strings (e.g., "14.074" or "20M") into standard ADIF enumerations ("20m").

## Integration Tools (Implemented)
These tools connect the local "Sovereign" node to the wider amateur radio ecosystem to draw insights from queried data. **Note:** This service is read-only and does not perform uploads.

- **`lotw_query`**: Queries ARRL's Logbook of The World for QSL confirmations and award credits.
- **`eqsl_query`**: Queries eQSL.cc for card status and inbox analysis.
- **`clublog_query`**: Queries ClubLog for DXCC status and propagation trends.
- **`qrz_query`**: Fetches extended operator bio and station data from QRZ.com (requires API key).
