# ADIF MCP

**ADIF MCP** is a set of Model Context Protocol tools that give AI agents safe, typed access to Amateur Radio logging data using the ADIF standard.

## Core Project Health
[![ADIF 3.1.5](https://img.shields.io/badge/ADIF-3.1.5-blue?label=Spec)](https://github.com/KI7MT/adif-mcp/spec)
[![GitHub release](https://img.shields.io/github/v/release/KI7MT/adif-mcp)](https://github.com/KI7MT/adif-mcp/releases)
[![GitHub tag](https://img.shields.io/github/v/tag/KI7MT/adif-mcp?sort=semver)](https://github.com/KI7MT/adif-mcp/tags)
[![Docs](https://img.shields.io/badge/docs-github_pages-blue)](https://adif-mcp.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/KI7MT/adif-mcp/blob/main/LICENSE)


## Project Ethos

ADIF-MCP is a community-driven effort.
It is not intended to replace or compete with existing ADIF libraries, utilities, or logging applications. Instead, it provides a common foundation that others can build upon.

- Interoperability — a schema-driven, spec-compliant core that makes it easier for tools, logs, and services to talk to each other.
- Extensibility — a plugin and integration framework for services like LoTW, eQSL, QRZ, and future platforms.
- Collaboration — designed to complement, not fragment, the ecosystem of ADIF tools already enjoyed by the ham community.
- Future-facing — introduces safe, typed access to ADIF data in contexts such as AI agents and MCP integrations, opening doors for innovation while preserving compatibility.

Our goal is simple: support and enhance the Amateur Radio logging ecosystem while keeping the project open, transparent, and aligned with the spirit of the hobby.

## Why ADIF MCP?

- Safe, schema-validated access to log data
- Full ADIF 3.1.5 compatibility (upward-compatible with future ADIF)
- Extensible plugin system (LoTW, eQSL, …)
- Designed for AI agents and modern developer workflows

## What This Project Provides

- **Core:** ADIF parsing, validation, canonical types, and tool contracts
- **Plugins:** LoTW and eQSL integrations as separate MCPs
- **Goals:** portability, safety, testability, and vendor-neutral interfaces

👉 Start with the [User Guide](userguide/getting-started.md) or browse through the [LoTW](integrations/lotw/index.md) and [eQSL](integrations/eqsl/index.md) integrations.
