# adif-mcp

Core [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server for **Amateur Radio Logging**, built on the [ADIF 3.1.6 specification](https://adif.org.uk/316/ADIF_316.htm).

## Overview

adif-mcp gives AI agents safe, typed access to Amateur Radio logging data. It validates and parses ADIF records, searches the full ADIF 3.1.6 specification (fields, enumerations, data types), and provides geospatial utilities for Maidenhead locators. A plugin system supports service integrations for LoTW, eQSL, QRZ, and Club Log.

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![ADIF 3.1.6](https://img.shields.io/badge/ADIF-3.1.6-blue)](https://adif.org.uk/316/ADIF_316.htm)
[![PyPI](https://img.shields.io/pypi/v/adif-mcp)](https://pypi.org/project/adif-mcp/)
[![CI](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-adif--mcp.com-blue)](https://adif-mcp.com/)

## Quick Start

```bash
pip install adif-mcp
```

## Configure Your MCP Client

adif-mcp works with any MCP-compatible client. Add the server config and restart -- tools appear automatically.

### Claude Desktop

Add to `claude_desktop_config.json` (`~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude\` on Windows):

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### ChatGPT Desktop

Configure via Settings > Apps & Connectors, or in your agent definition:

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### VS Code / GitHub Copilot

Add to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### Gemini CLI

Add to `~/.gemini/settings.json` (global) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

## Tools

adif-mcp exposes **11 verified tools** via the Model Context Protocol:

| Category | Tool | Description |
|----------|------|-------------|
| **Validation** | `validate_adif_record` | Validate a raw ADIF string against the 3.1.6 spec |
| **Validation** | `parse_adif` | Parse ADIF text into normalized JSON records |
| **Spec** | `search_enumerations` | Search within ADIF enumeration records |
| **Spec** | `read_specification_resource` | Retrieve raw JSON for any spec module (band, mode, fields) |
| **Spec** | `search_adif_spec` | Global search across fields, datatypes, and enumerations |
| **Spec** | `list_enumeration_groups` | List all enumeration categories (DXCC, Submode, etc.) |
| **Spec** | `get_enumeration_values` | Return valid values for a specific enumeration group |
| **Geospatial** | `calculate_distance` | Great Circle distance (km) between two Maidenhead locators |
| **Geospatial** | `calculate_heading` | Initial beam heading (azimuth) between two locators |
| **System** | `get_version_info` | Active service version and ADIF spec version |
| **System** | `get_service_metadata` | Build timestamps and maintainer details |

## ADIF-MCP Engines

This package defines the ADIF MCP core engine, with plugins for:

- **LoTW** (`adif-mcp-lotw`) -- ARRL Logbook of The World: confirmations, awards tracking, uploads
- **eQSL** (`adif-mcp-eqsl`) -- eQSL.cc: electronic QSL confirmations and awards
- **QRZ** (`adif-mcp-qrz`) -- QRZ.com: callsign lookup and logbook integration
- **Club Log** (`adif-mcp-clublog`) -- Club Log: DXCC matching, OQRS, expedition logs

MCP doesn't replace LoTW, eQSL, Club Log, QRZ, or any award/logging program. Instead, it gives operators visibility and accessibility into their award progress, across sponsors, without needing to export, filter, or code.

## Compliance & Provenance

adif-mcp follows the [ADIF Specification](https://adif.org.uk) (currently 3.1.6) and uses **registered Program IDs** to identify all exports:

- `ADIF-MCP` -- Core engine
- `ADIF-MCP-LOTW` -- LoTW plugin
- `ADIF-MCP-EQSL` -- eQSL plugin
- `ADIF-MCP-QRZ` -- QRZ plugin
- `ADIF-MCP-CLUBLOG` -- Club Log plugin

The project uses **APP_ fields** for provenance when augmenting records:

- `APP_ADIF-MCP_OP` -- operation performed (`normalize`, `validate`, `merge`)
- `APP_ADIF-MCP-LOTW_ACTION` -- LoTW plugin operation
- `APP_ADIF-MCP-EQSL_TIME` -- timestamp of eQSL merge

See the [Program ID & APP_ Field Policy](https://adif-mcp.com/program-id-policy/) for full details.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE) for details.
