# ADIF MCP

**ADIF MCP** is a set of Model Context Protocol tools that give AI agents safe, typed access to Amateur Radio logging data using the ADIF standard.

## Core Project Health
[![GitHub release](https://img.shields.io/github/v/release/KI7MT/adif-mcp)](https://github.com/KI7MT/adif-mcp/releases)
[![GitHub tag](https://img.shields.io/github/v/tag/KI7MT/adif-mcp?sort=semver)](https://github.com/KI7MT/adif-mcp/tags)
[![CI](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-github_pages-blue)](https://adif-mcp.com/)
[![SSL Certificate Expiry Check](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml)


## Why ADIF MCP?

- Safe, schema-validated access to log data
- Full ADIF 3.1.5 compatibility (upward-compatible with future ADIF)
- Extensible plugin system (LoTW, eQSL, …)
- Designed for AI agents and modern developer workflows

## What This Project Provides

- **Core:** ADIF parsing, validation, canonical types, and tool contracts
- **Plugins:** LoTW and eQSL integrations as separate MCPs
- **Goals:** portability, safety, testability, and vendor-neutral interfaces

👉 Start with the [User Guide](userguide/getting-started.md) or browse through the [LoTW](plugins/lotw/index.md) and [eQSL](plugins/eqsl/api.md) plugins.
