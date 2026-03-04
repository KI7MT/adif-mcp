# Roadmap

## Completed (v0.1.0 -- v0.5.x)

### Core Engine
- `src/adif_mcp/` canonical layout with identity namespace
- 7 MCP tools: validation, parsing, spec search, geospatial, metadata
- FastMCP integration for multi-client MCP support
- ADIF 3.1.6 specification bundled as structured JSON
- Persona and credential management (system keyring)
- Plugin framework for service integrations

### Quality & CI
- ruff, mypy --strict, interrogate (100% docstring coverage)
- Pre-commit hooks, manifest validation
- Tag-driven PyPI publishing via trusted publisher (OIDC)
- CI workflow (lint, type check, test)

### Documentation
- MkDocs Material site at [adif-mcp.com](https://adif-mcp.com/)
- Developer setup, command reference, code snippets
- Persona management and award query guides
- MCP tools reference, manifest docs

### Packaging
- PyPI: `pip install adif-mcp`
- CLI entry point: `adif-mcp`
- Registered ADIF Program IDs (ADIF-MCP, ADIF-MCP-LOTW, ADIF-MCP-EQSL, ADIF-MCP-QRZ, ADIF-MCP-CLUBLOG)

## Current Focus

### Integration Plugins
- LoTW adapter: confirmation queries, award tracking
- eQSL adapter: inbox queries, confirmation status
- QRZ adapter: callsign lookup, logbook queries
- Club Log adapter: DXCC matching, OQRS status

### ADIF Models
- Pydantic models for typed QSO records
- Normalization helpers (callsign, grid, dates, RST, frequency)
- Enumeration loaders from bundled JSON

## Future

### Expanded Tool Surface
- Award progress queries (DXCC, WAS, VUCC by band/mode)
- Cross-provider log comparison and merge
- Batch validation for ADIF file imports

### Community
- Contribution guide and plugin development docs
- Example notebooks for common award tracking workflows
