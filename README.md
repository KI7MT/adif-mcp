# adif-mcp

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Core Project Health
[![GitHub release](https://img.shields.io/github/v/release/KI7MT/adif-mcp)](https://github.com/KI7MT/adif-mcp/releases)
[![GitHub tag](https://img.shields.io/github/v/tag/KI7MT/adif-mcp?sort=semver)](https://github.com/KI7MT/adif-mcp/tags)
[![CI](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-github_pages-blue)](https://adif-mcp.com/)
[![pre-commit](https://github.com/KI7MT/adif-mcp/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/pre-commit.yml)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![SSL Certificate Expiry Check](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/ssl-expiry.yml)

## MCP / API Readiness
[![MCP](https://img.shields.io/badge/AI--Agent--Ready-MCP-green)](https://modelcontextprotocol.io/)
[![API Docs](https://img.shields.io/badge/API-Schema-blue)](https://adif-mcp.com/mcp/manifest.html)
[![JSON Schema](https://img.shields.io/badge/Schema-JSON--Schema-lightgrey)](#)
[![Manifest Validate](https://github.com/KI7MT/adif-mcp/actions/workflows/manifest-validate.yml/badge.svg)](https://github.com/KI7MT/adif-mcp/actions/workflows/manifest-validate.yml)

---

This project implements the [ADIF 3.1.5 specification](https://adif.org.uk/315/ADIF_315.htm) as a **core library** for amateur radio logging systems.
It provides:

- Validation & normalization of ADIF records
- Unified schema for consistent QSO storage and exchange
- MCP-ready tools for safe AI-agent access
- Foundation for service adapters (e.g., LoTW, eQSL)

## Why?
Every amateur radio logger supports ADIF, but implementations are fragmented.
`adif-mcp` offers a **single, standards-based interface** to make QSO data portable, auditable, and agent-friendly.

## Next Steps
- Build `adif-mcp-lotw` and `adif-mcp-eqsl` adapters
- Expose MCP tools for validation, award tracking, and service sync
- Support cross-logger interoperability with AI-driven agents

## License
MIT — open and free for amateur radio use.
