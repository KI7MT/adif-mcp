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
