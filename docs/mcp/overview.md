# MCP Overview

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) is an open standard that lets AI agents discover and call tools exposed by external servers. Instead of hardcoding API integrations, agents connect to MCP servers that advertise typed tool contracts -- inputs, outputs, and descriptions -- so the agent can invoke them safely.

## How adif-mcp Uses MCP

adif-mcp is an MCP server that exposes Amateur Radio logging operations as tools. When an AI agent (Claude, ChatGPT, Copilot, Gemini, etc.) connects to adif-mcp, it automatically discovers 11 tools for:

- **Validating and parsing** ADIF records against the 3.1.6 specification
- **Searching** the full ADIF spec -- fields, enumerations, data types
- **Computing** Great Circle distance and beam headings between Maidenhead grids
- **Querying** service metadata and version information

## Architecture

```
AI Agent  <-->  MCP Protocol (stdio)  <-->  adif-mcp server
                                              |
                                              +-- ADIF 3.1.6 spec (bundled JSON)
                                              +-- Plugin system (LoTW, eQSL, QRZ, Club Log)
                                              +-- Persona & credential management
```

The server runs locally via `stdio` transport (default) or `streamable-http` for debugging with MCP Inspector. All ADIF specification data is bundled -- no network calls required for core operations.

## Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| Validation | 2 | Parse and validate ADIF records |
| Spec Intelligence | 5 | Search fields, enumerations, data types |
| Geospatial | 2 | Distance and heading between grids |
| System | 2 | Version and metadata |

See the [Tools](tools.md) page for the complete tool reference.
