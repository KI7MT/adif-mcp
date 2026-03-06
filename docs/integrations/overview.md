# Integration Overview

adif-mcp uses a plugin architecture to connect with Amateur Radio logging services. Each integration is a self-contained adapter that maps service-specific APIs to the common ADIF MCP schema.

## Available Integrations

| Plugin | Service | Status | Description |
|--------|---------|--------|-------------|
| `adif-mcp-lotw` | [LoTW](https://lotw.arrl.org/) | In progress | ARRL Logbook of The World -- confirmations, awards, uploads |
| `adif-mcp-eqsl` | [eQSL](https://www.eqsl.cc/) | In progress | Electronic QSL confirmations and awards |
| `adif-mcp-qrz` | [QRZ](https://www.qrz.com/) | In progress | Callsign lookup and logbook integration |

## How Integrations Work

Each plugin:

1. **Authenticates** using credentials stored in the operator's persona (via system keyring)
2. **Queries** the service API using only read-safe operations (GET requests, no modifications)
3. **Normalizes** responses to the common ADIF MCP `QsoRecord` schema
4. **Exposes** service-specific MCP tools that agents can discover and call

Credentials are never exposed to AI agents. The persona system manages authentication separately, and plugins only receive scoped access tokens at runtime.

## Plugin Architecture

```
Operator Persona
  +-- Credentials (system keyring)
  +-- Callsign history
  +-- Provider bindings
        |
        +-- LoTW adapter  --> lotw.arrl.org API
        +-- eQSL adapter  --> eqsl.cc API
        +-- QRZ adapter   --> xmldata.qrz.com API
```

## Adding a New Integration

Integration development follows the patterns established by the existing plugins. See the [Dev Guide](../dev/dev-env-setup.md) for environment setup and the [Provider Schemas](../dev/provider-schemas.md) page for the schema contracts each adapter must implement.
