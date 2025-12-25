# Release Process

This document outlines the "Gold Standard" protocol for releasing new versions of `adif-mcp`. We use a strict gating process to ensure that every release is stable, documented, and compliant with the ADIF specification.

## 1. Pre-Flight Validation (The Gate)

Before attempting a release, the codebase must pass the full quality gate in a clean environment.

```bash
# 1. Clean everything
make clean-all

# 2. Bootstrap
make init

# 3. Run the Quality Gate
make gate
```

**Stop if:**
- Any linting or type errors occur.
- Unit tests fail.
- Manifest validation fails.
- Docstring coverage drops below 100%.

## 2. The Release Command

We use a unified Makefile target to handle version bumping, tagging, and pushing. This ensures consistency between `pyproject.toml` and git tags.

### Syntax
```bash
make release VERSION=<x.y.z> SPEC=<spec_version>
```

- **VERSION**: The new semantic version for the package (e.g., `0.3.12`).
- **SPEC**: The ADIF specification version supported (e.g., `3.1.5`).

### Example
To release version `0.4.0` targeting ADIF spec `3.1.5`:

```bash
make release VERSION=0.4.0 SPEC=3.1.5
```

### What Happens Automatically
1.  **Validation**: Runs `make gate` one last time.
2.  **Bump**: Updates `version` in `pyproject.toml` and `CHANGELOG.md`.
3.  **Spec Update**: Updates `tool.adif.spec_version` in `pyproject.toml`.
4.  **Commit**: Creates a release commit (`bump: version 0.4.0`).
5.  **Tag**: Creates a git tag (`v0.4.0`).
6.  **Push**: Pushes the commit and tag to `origin`.

## 3. Post-Release Verification

Once the tag is pushed, the CI/CD pipeline (GitHub Actions) takes over to build and publish the package.

### Manual Smoke Test
After the package is published, verify it in a fresh environment:

```bash
# 1. Install from PyPI (or test index)
uv tool install adif-mcp --force

# 2. Verify Version
adif-mcp --version

# 3. Verify Spec Compliance
uv run adif-mcp mcp
# (Check that get_service_metadata returns the correct spec version)
```
