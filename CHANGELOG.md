# Changelog

All notable changes to this project will be documented in this file.

## [0.1.19] - 2025-08-30

### Added
- Persona management (CLI): `persona add|list|show|remove|set-credential`.
- Date-bounded personas to model vanity/contest/event calls (start/end).
- Secure secret storage via system keyring; non-secrets stored in JSON index.
- `PersonaStore` for CRUD over `~/.config/adif-mcp/personas.json` (overrideable via `pyproject.toml`).
- Docs: brief guidance on personas & keyring (operator-facing).

### Changed
- CLI polish and consistent output for persona flows.
- `_personas_index_path()` resolves path from `tool.adif.personas_index` if provided.

### Fixed
- Type-check issues across `personas.py` and CLI; strict mypy now clean.
- Ruff E501 and assorted nitpicks; interrogate coverage at 100%.

### Internal
- `make gate` and `smoke-all` are green (ruff, mypy, interrogate, pytest, manifest).

---

## [0.1.18] - 2025-08-29

### Added
- New script: `scripts/provider_coverage.py`
  - Computes per-provider ADIF field coverage against the canonical catalog.
  - Pretty-printed report with coverage %, missing fields, and status column.
  - Consistent header/title conventions (`DEFAULT_TITLE`, `DEFAULT_DESCRIPTION`).
- Added `TODO.md` for developer notes and future improvements.
- Added `utils.clear()` helper idea for terminal readability (tracked in TODO).

### Changed
- Updated `CONTRIBUTING.md` to require smoke tests before PRs:
  - `ruff`, `mypy`, `interrogate`, `pytest`, and manifest validation.
- Centralized JSON spec & provider files under `mcp/` directory for clarity.
- Improved test coverage to 100% across `src/`, `scripts/`, and `test/`.

### Fixed
- Build hook script (`scripts/build_hooks.py`) cleaned up for Python ≥3.11 only.
- Normalization in ADIF parser (`record_as_qso`) now uppercases callsigns.
- eQSL stub `filter_summary` properly raises `ValueError` for invalid selectors.
- RST validation rejects invalid values (`rst_sent`, `rst_rcvd`).

---

## [0.1.17] - 2025-08-28
### Added
- First pass at `eqsl_stub.py` demo tool.
- ADIF parser and models with validation.
- CLI entrypoints (`adif-mcp version`, `manifest-validate`, `eqsl`).
- Docs: Concepts overview with working Mermaid diagram.
- CI pipeline integration for linting, typing, and manifest validation.

---

[0.1.18]: https://github.com/KI7MT/adif-mcp/releases/tag/v0.1.18
[0.1.17]: https://github.com/KI7MT/adif-mcp/releases/tag/v0.1.17

## [0.1.16] - 2025-08-28

### Added
- MkDocs configuration and CI/CD workflow for documentation publishing
- Mermaid2 diagrams support in docs (flowcharts render correctly)
- Redirects for subdomains (`eqsl.adif-mcp.com`, `lotw.adif-mcp.com`)
- Developer convenience Makefile targets (`docs-serve`, `check-version`, `init`)

### Fixed
- Smoke test isolation issues with `.smoke-venv`
- Pre-commit hook installation steps in `setup-dev`
- Release workflow tag/version mismatch edge cases
- Removed broken sitemap plugin reference

### Changed
- Documentation structure: clearer navigation (`Integrations` vs `Plugins`)
- MkDocs index/overview pages reorganized for clarity
- Adopted consistent `.yml` extension for workflows and mkdocs config


## [0.1.15] - 2025-08-27
### Added
  - Added target for publishing to github-release

## [0.1.14] - 2025-08-27

### Added
- Initial documentation publishing to [adif-mcp.com](https://adif-mcp.com)
- Placeholder test suite (`test/test_placeholder.py`) to satisfy CI pytest checks
- Pre-commit hooks and `commitizen` validation for consistent workflow
- Manifest validation script with JSON Schema checks
- Full docstring coverage across all source files

### Fixed
- Type annotation and `mypy` strictness issues with Click decorators
- Ruff/formatting issues in `scripts/validate_manifest.py`

### Changed
- CI/CD pipelines: renamed workflows to `.yml` for consistency
- Adopted `uv` toolchain for dependency management

## Removed
- All previous development tags

## v0.1.18 (2025-08-29)

## [v0.1.1] to [0.1.13] - 2025-08-27
- No formal package release was made during pipline development.
