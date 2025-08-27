v0.1.1 — Green Baseline Release

This is the first fully green baseline for adif-mcp: docs are published, CI/CD workflows pass end-to-end, and the development toolchain (uv, ruff, mypy, interrogate, commitizen, pre-commit) is in place.

Added
- Published documentation to adif-mcp.com
- Placeholder test suite (test/test_placeholder.py) for CI stability
- scripts/validate_manifest.py for MCP manifest schema validation
- Pre-commit hooks & commitizen integration for consistent workflow
- Full docstring coverage across all source files

Fixed
- Type annotation + mypy strictness issues with Click decorators
- Ruff/formatting issues in scripts/validate_manifest.py

Changed
- CI/CD pipelines: renamed all workflows to .yml for consistency
- Adopted uv toolchain for dependency management

⸻

📦 Tag: v0.1.1
🌐 Docs: adif-mcp.com
