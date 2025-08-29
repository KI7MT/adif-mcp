# adif-mcp

Core [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) service for **Amateur Radio Logging**, per [ADIF 3.1.5 specification](https://adif.org.uk/315/ADIF_315.htm)

> **Pretty Code • Pretty Output • Iterative Docs**
> A simple mantra: keep the code clean, the output clear, and the docs evolving.

---

## Resources

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Core Project Health
![ADIF](https://img.shields.io/badge/ADIF-3.1.5-blue)
[![GitHub release](https://img.shields.io/github/v/release/KI7MT/adif-mcp?display_name=tag)](https://github.com/KI7MT/adif-mcp/releases)
[![GitHub tag](https://img.shields.io/github/v/tag/KI7MT/adif-mcp?sort=semver)](https://github.com/KI7MT/adif-mcp/tags)
[![CI](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-github_pages-blue)](https://adif-mcp.com/)
[![pre-commit](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/pre-commit.yml)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![SSL Certificate Expiry Check](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml)


## MCP / API Readiness
[![MCP](https://img.shields.io/badge/AI--Agent--Ready-MCP-green)](https://modelcontextprotocol.io/)
[![API Docs](https://img.shields.io/badge/API-Schema-blue)](https://adif-mcp.com/mcp/manifest.html)
[![JSON Schema](https://img.shields.io/badge/Schema-JSON--Schema-lightgrey)](#)
[![Manifest Validate](https://github.com/KI7MT/adif-mcp/actions/workflows/manifest-validate.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/manifest-validate.yml)


## Compliance and Program Registry
[![ADIF 3.1.5](https://img.shields.io/badge/ADIF-3.1.5-blue?label=Spec)](#-compliance--provenance)
[![Program ID](https://img.shields.io/badge/Program%20ID-Registered-success)](https://adif.org.uk/programids.html)

---



## Overview

This package defines the ADIF MCP core engine, with plugins for:
- LoTW (`adif-mcp-lotw`)
- eQSL (`adif-mcp-eqsl`)

Performs these tasks
- Validation & normalization of ADIF records
- Unified schema for consistent QSO storage and exchange
- MCP-ready tools for safe AI-agent access
- Foundation for service adapters (e.g., LoTW, eQSL)

🔑 Takeaway: MCP doesn’t replace LoTW, eQSL, or award programs. Instead, it gives operators visibility and accessibility into their award progress, across sponsors, without them needing to export, filter, or code.

---

## Why ADIF-MCP Matters

Unlike existing ADIF editors and one-off utilities, ADIF-MCP is a shared protocol engine for the Amateur Radio community:
- Spec-compliant & typed — ADIF fields are validated against the official standard.
- Extensible — integrations (LoTW, eQSL, QRZ, logging apps) plug into a common base.
- AI-ready — exposes safe, typed tools to AI agents via the Model Context Protocol.
- Foundation, not silo — one engine many apps can trust, instead of everyone re-implementing ADIF parsing.

👉 ADIF-MCP turns ADIF from a static file format into a living protocol interface.

---

## Next Steps
- Build `adif-mcp-lotw` and `adif-mcp-eqsl` adapters
- Expose MCP tools for validation, award tracking, and service sync
- Support cross-logger interoperability with AI-driven agents

## Compliance & Provenance

ADIF-MCP and its plugins follow the [ADIF Specification](https://adif.org.uk) (currently 3.1.5) and use **registered Program IDs** to identify all exports:

- `ADIF-MCP` — Core engine
- `ADIF-MCP-LOTW` — Plugin for ARRL Logbook of The World
- `ADIF-MCP-EQSL` — Plugin for eQSL.cc

To ensure transparency and auditability, the project also uses **APP_ fields** for provenance when augmenting records.
Examples include:

- `APP_ADIF-MCP_OP` → operation performed (`normalize`, `validate`, `merge`)
- `APP_ADIF-MCP-LOTW_ACTION` → LoTW plugin operation
- `APP_ADIF-MCP-EQSL_TIME` → timestamp of eQSL merge

See the [Program ID & APP_ Field Policy](docs/program-id-policy.md) for full details.

## License
MIT — open and free for amateur radio use.
