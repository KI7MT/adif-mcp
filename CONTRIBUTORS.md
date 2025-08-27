# Contributors

This project exists thanks to its contributors.

## Contributors

- Gregory Beam (@KI7MT) — Project lead, architecture, packaging, documentation

## Contribution Checklist

When contributing new code, documentation, or other resources, please ensure:

1. **Coding Standards**
   - Add **docstrings** for all functions, classes, and modules.
   - Run `make test` and ensure all unit tests pass.
   - Run `pre-commit run --all-files` before committing.

2. **Documentation Standards**
   - Use **lowercase filenames** in `docs/` (e.g., `troubleshooting.md`).
   - Update `mkdocs.yml` to include new docs under the correct `nav` section.
   - Verify that all internal links in Markdown files resolve correctly.
   - Copy root-level files (`CHANGELOG.md`, `LICENSE.md`) into `docs/` if you want them visible on GitHub Pages.

3. **Releases**
   - Update `CHANGELOG.md` with changes.
   - Bump `__version__` in `src/wspr_ai_lite/__init__.py`.
   - Tag the release (`git tag vX.Y.Z && git push --tags`).
   - Smoke test with `make smoke-test` or `make smoke-test-pypi`.

4. **General**
   - Keep commits atomic and meaningful.
   - Prefer PRs from feature branches.
   - Be respectful and collaborative.

Thank you for helping improve **WSPR AI Lite** 🚀
