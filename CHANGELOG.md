# Changelog

## [0.1.17] - 2025-08-29
### Added
- **ADIF parser (`adif_reader`)**: minimal implementation to parse `.adi` text into typed QSO records.
- **eQSL stub (`eqsl_stub`)**: synthetic inbox + band/mode summaries for testing integration concepts.
- **CLI commands**:
  - `adif-mcp version` → shows MCP + ADIF spec version.
  - `adif-mcp manifest-validate` → validates MCP manifest against schema.
  - `adif-mcp eqsl inbox` and `adif-mcp eqsl summary` → exercise the stub integration.
- **Build hook (`build_hooks.py`)**: automatically injects `adif_meta.json` into the wheel with version + spec metadata.
- **Full test suite** with 100% coverage across parsers, stub tools, CLI, and manifest validation.
- **CI/CD docs workflow**: MkDocs + Material + Mermaid v10, GitHub Pages with custom domain.

### Changed
- Normalized ADIF keys (snake_case).
- Callsigns automatically uppercased in parser.
- Strict type checking: `mypy`, `ruff`, `interrogate` integrated and enforced at 100% docstring coverage.

### Fixed
- CI/CD issues with `commitizen` hooks removed, replaced with manual version bump + tagging.
- Mermaid diagram rendering on GitHub Pages (switch to `mkdocs-mermaid2-plugin`).

---

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

## [v0.1.1] to [0.1.13] - 2025-08-27
- No formal package release was made during pipline development.
