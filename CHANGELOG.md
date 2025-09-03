# Changelog

All notable changes to this project will be documented in this file.

## [0.3.3] - 2025-09-02
### Fixed
- Ensure manifest.json is included in dist aand wheel.

---

## [0.3.2] - 2025-09-02
### Fixed
- Ensured `manifest-validate` works reliably in both local and packaged installs by updating `cli.py` to prefer the packaged `src/adif_mcp/mcp/manifest.json` and gracefully fallback to repo manifests.
- Cleaned up CI configuration:
  - Updated `.github/workflows/ci.yml` to run manifest validation inline with other gates.
  - Corrected paths and logic in `manifest-validate.yml` workflow.

### Changed
- Removed redundant manifest validation logic; consolidated to `adif-mcp manifest-validate` for consistency across local, CI, and release builds.
- Minor cleanup of CLI docstrings and UX messages.

---

## [0.3.1] - 2025-09-03
### Fixed
- Restored and migrated `PersonaManager` into the new `adif_mcp.identity` namespace.
- Resolved missing import errors caused by the removal of `persona_manager.py`.
- Cleaned up packaging to ensure identity components ship correctly in wheel and sdist.

---

## [0.3.0] - 2025-09-03

### Added
- New `adif_mcp.identity` namespace with clear separation of:
  - `models` (Persona, ProviderRef types)
  - `store` (JSON persistence)
  - `secrets` (keyring integration)
  - `manager` (high-level PersonaManager with typed errors)
  - `errors` (granular exception classes for credential handling)

- `src/adif_mcp/resources/` module introduced:
  - `providers/*.json` for per-provider field definitions
  - `schemas/manifest.v1.json` for manifest validation
  - `spec/adif_catalog.json` and `spec/adif_meta.json` for ADIF catalog/spec metadata

### Changed
- Migrated old `personas.py` and `persona_manager.py` into `identity/` namespace.
- Moved provider manifests, schemas, and ADIF spec data into `resources/`.
- Updated all probes and adapters to import from `identity` instead of legacy modules.
- CI and pre-commit updated to enforce `ruff`, `mypy --strict`, and `interrogate` across the new layout.

### Removed
- Legacy `scripts/` helpers (`http_probe.py`, `provider_index_probe.py`, etc.) now fully replaced by `adif_mcp.probes.*`.
- Old `mcp/` provider/spec folders replaced by `resources/`.
- Deprecated direct imports from `adif_mcp.personas` / `persona_manager`.

### Notes
- This release introduces **breaking changes** for anyone importing directly from `adif_mcp.personas` or `persona_manager`.
- Downstream users should migrate to the `adif_mcp.identity` namespace.

---

## [0.2.1] - 2025-09-03

### Fixed
- Updated and refactored all test files under `test/` to match the new package layout.
- Restored full test coverage (17/17 passing).
- Fixed CLI `manifest-validate` command to use the in-package validator and packaged/repo manifests.
- Corrected workflow issues in CI:
  - Ensured `uv` is installed and available in pre-commit hooks.
  - Synced dev dependencies for `uv run` hooks in CI.
- Resolved pre-commit “uv not found” failures by updating GitHub Actions workflow.

### Changed
- CI/CD pipelines (lint, type-check, test, manifest validation, pre-commit) now green across all jobs.
- Pre-commit configuration aligned with `uv run` workflows.

### Notes
- This is primarily a **stability/maintenance release** to lock in a clean baseline after the v0.2.0 refactor.

---

## [0.2.0] - 2025-09-03

### Added
- Provider probe framework under `adif_mcp/probes/`:
  - `http_probe` (GET-only probe engine with redaction).
  - `inbox_probe` (persona+provider → safe GET execution).
  - `index_probe` (no-network credential presence check).
- New CLI commands:
  - `adif-mcp provider probe --provider … --persona …`
  - `adif-mcp provider index-check --provider … --persona …`
- Makefile targets `probe-index`, `probe-get`, `probe-all`.
- Centralized credential validation via `PersonaManager.require()` with typed errors.
- One-pager documentation: `docs/probes.md`.

### Changed
- Refactored all scripts into proper package modules (`adif_mcp/probes`, `adif_mcp/tools`, `adif_mcp/dev`).
- CLI now uses in-package probe logic (no more `scripts/` imports).
- Ruff line length standardized to 90 chars.

### Fixed
- Redaction for sensitive parameters (`password`, `token`, `api`, etc.) in probe output.
- Interrogate coverage: added missing docstrings to new modules and helpers.

---

## [0.1.21] - 2025-08-31
### Added
- Introduced **PersonaManager** as the single point of truth for personas, providers, and secrets.
- New script: `provider_index_probe.py` consolidates the old `eqsl_inbox_probe.py` and `provider_inbox_probe.py`.
- `make keychain-test` target now exercises persona add/set/remove flows against macOS Keychain safely.
- Extended pyproject.toml:
  - Defined `[project.optional-dependencies]` groups for dev tooling (ruff, mypy, pytest, interrogate, mkdocs, etc.).
  - Added provider URLs (LoTW, eQSL, Club Log, QRZ) under `[project.urls]`.
  - Config section `[tool.adif]` now OS-agnostic (`config_dir_name`, `personas_index`).
- Makefile:
  - Added consistent `gate` and `smoke-all` targets with `uv run` for lint, type, test, interrogate.
  - Added `docs-check` and `docs-dev` helpers for MkDocs/Mermaid workflows.

### Changed
- All persona/provider/secret resolution now routed through **PersonaManager**.
- Refactored smoke and probe scripts to depend on PersonaManager (no direct PersonaStore lookups).
- Type safety improvements:
  - Removed redundant `cast()` calls, eliminated `Any` return paths.
  - Added full docstrings and typing to PersonaManager and helpers.
- Consolidated/de-duplicated Makefile `smoke-all` target (removed `scripts/smoke.sh`).
- UI (`persona_ui.py`) removed from repo and stashed for later revisit.

### Fixed
- `make gate` and `make smoke-all` now fully green (ruff, mypy strict, interrogate, pytest).
- MacOS keychain test: fixed handling of `security(1)` return codes when no items remain.
- Pre-commit and CI config aligned with strict typing and lint rules.

### Notes
- This version is **tagged only** (v0.1.21) and not intended for release packaging.
- Breaking change: the following scripts were removed in favor of consolidation:
  - `eqsl_inbox_probe.py`
  - `provider_inbox_probe.py`

---

## [0.1.20] - 2025-08-30
### Added
- Persona CLI enhancements:
  - `persona add`, `persona list`, `persona show`, `persona remove`, and `persona remove-all`.
  - Support for managing provider credentials via system keyring.
  - Validation: reject end date earlier than start date.
  - Automatic normalization of callsigns to uppercase.
  - Improved `persona list` output with optional `--verbose` mode (masks usernames).
  - Keyring backend is echoed when saving credentials.
- New `make keychain-test` target to manually validate persona/credential round-trips (safe for local testing).

### Fixed
- Consistent error handling in CLI commands (`remove`, `remove-all`, etc.).
- Mypy and Ruff compliance across `adif-mcp/{src,scripts,test} `.
- Gate and smoke tests now pass cleanly with real macOS Keychain integration.

### Notes
- This release marks the first complete integration of **Personas** with secure credential storage.
- CI tests avoid touching the real keychain; use `make keychain-test` locally if you want to validate secrets end-to-end.

---

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

---

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
