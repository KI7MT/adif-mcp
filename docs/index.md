# ADIF MCP

**ADIF MCP** is a set of Model Context Protocol tools that give AI agents safe, typed access to Amateur Radio logging data using the ADIF standard.

## Core Project Health
[![ADIF 3.1.5](https://img.shields.io/badge/ADIF-3.1.5-blue?label=Spec)](#-compliance--provenance)
[![GitHub release](https://img.shields.io/github/v/release/KI7MT/adif-mcp)](https://github.com/KI7MT/adif-mcp/releases)
[![GitHub tag](https://img.shields.io/github/v/tag/KI7MT/adif-mcp?sort=semver)](https://github.com/KI7MT/adif-mcp/tags)
[![Docs](https://img.shields.io/badge/docs-github_pages-blue)](https://adif-mcp.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


## Why ADIF MCP?

- Safe, schema-validated access to log data
- Full ADIF 3.1.5 compatibility (upward-compatible with future ADIF)
- Extensible plugin system (LoTW, eQSL, …)
- Designed for AI agents and modern developer workflows

## What This Project Provides

- **Core:** ADIF parsing, validation, canonical types, and tool contracts
- **Plugins:** LoTW and eQSL integrations as separate MCPs
- **Goals:** portability, safety, testability, and vendor-neutral interfaces

👉 Start with the [User Guide](userguide/getting-started.md) or browse through the [LoTW](plugins/lotw/api.md) and [eQSL](plugins/eqsl/api.md) plugins.
