# Release Process

adif-mcp uses a tag-driven release workflow. Push a semver tag and GitHub Actions handles the rest.

## 1. Pre-Flight Validation

Before releasing, the codebase must pass the full quality gate:

```bash
# Clean and run all checks
make clean-all
make gate
```

**Stop if** any linting, type, test, manifest, or docstring coverage errors occur.

## 2. Bump the Version

Update the version in `pyproject.toml`:

```toml
version = "0.5.2"
```

Commit the version bump:

```bash
git add pyproject.toml
git commit -m "bump: version 0.5.2"
```

## 3. Tag and Push

Create a semver tag and push:

```bash
git tag v0.5.2
git push origin main --tags
```

## 4. Automated Publishing

The `.github/workflows/publish.yml` workflow triggers on any `v*` tag push:

1. Checks out the tagged commit
2. Builds the package with `uv build`
3. Publishes to PyPI via trusted publisher (OIDC -- no API tokens)

The `pypi` environment in GitHub repo settings provides the OIDC trust relationship.

## 5. Post-Release Verification

After the workflow completes, verify the release:

```bash
# Install from PyPI
pip install adif-mcp --upgrade

# Verify version
adif-mcp --version
```

Check the [PyPI project page](https://pypi.org/project/adif-mcp/) to confirm the new version is live.
