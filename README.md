# ADIF-MCP

⚠️ Status: Deprecated – Python implementation is frozen
The Python codebase (≤ v0.3.6) is no longer maintained.
Future development is moving to Java 21 + JavaFX.

## Documentation
- User & Developer Docs: https://adif-mcp.com
- Release notes & tags: GitHub Releases

## Python Legacy
- The last working Python release: v0.3.6
- A tombstone branch preserves the Python sources for reference.
- All new development is happening in Java.

## Migration Plan
- Existing CLI concepts (personas, providers, creds, sync) will re-emerge in Java.
- MkDocs remains the user-facing documentation system.
- Developer API docs will move to Javadoc.

## Core Project Health
![ADIF](https://img.shields.io/badge/ADIF-3.1.5-blue)
[![Docs](https://img.shields.io/badge/docs-github_pages-blue)](https://adif-mcp.com/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![SSL Certificate Expiry Check](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml)
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


License

MIT © KI7MT
