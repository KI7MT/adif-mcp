# Developer Commands

This page is generated from `make help` for quick reference.

```
| Target                 | Purpose                                                      | Core Commands / Flow |
|------------------------|--------------------------------------------------------------|----------------------|
| **bootstrap**          | Ensure dev deps are installed                                | `uv sync --group dev \|\| uv sync` |
| **setup-dev**          | Full dev env (deps + pre-commit hooks)                       | `uv sync …`; `pre-commit install …` |
| **sync**               | Sync runtime deps                                            | `uv sync` |
| **add**                | Add runtime dep (`DEP=...`)                                  | `uv add "$(DEP)"` |
| **add-dev**            | Add dev dep (`DEP=...`)                                      | `uv add --group dev "$(DEP)"` |
| **init**               | One-time bootstrap + smoke                                   | `make setup-dev`; `make smoke-all` |
| **lint**               | Ruff lint                                                    | `uv run ruff check .` |
| **format**             | Ruff format (in-place)                                       | `uv run ruff format .` |
| **type**               | mypy type check (src only)                                   | `uv run mypy src` |
| **test**               | pytest quick run                                             | `uv run pytest -q` |
| **smoke**              | Quick gate: lint + type + manifest                           | `make lint`; `make type`; `make manifest` |
| **gate**               | CI parity: lint + type + test + manifest + docs + keychain   | Lint → Type → Test → Manifest → `interrogate` → `keychain-test` |
| **manifest**           | Validate all tracked `manifest.json`                         | `uv run python scripts/validate_manifest.py <file>` |
| **docs-dev**           | Generate `docs/dev.md` from `make help`                      | Build from `help` output |
| **pre-commit-install** | Install pre-commit + commit-msg hooks                        | `pre-commit install -t pre-commit -t commit-msg` |
| **pre-commit-run**     | Run all hooks on repo                                        | `pre-commit run --all-files` |
| **smoke-all**          | Full smoke (reproducible)                                    | Ruff lint + format check + mypy + interrogate + pytest + manifest |
| **release**            | Tag & push release                                           | `git tag -a v$(VERSION)`; `git push origin v$(VERSION)` |
| **docs-build**         | Build MkDocs site                                            | `uv run mkdocs build --strict` |
| **docs-serve**         | Serve docs locally                                           | `uv run mkdocs serve -a 127.0.0.1:8000` |
| **docs-check**         | Verify Mermaid diagrams rendered                             | Grep `site/` for `<div class="mermaid">` |
| **print-versions**     | Show project + spec versions                                 | Echo values from `pyproject.toml` |
| **check-version**      | Ensure `VERSION`/`SPEC` match `pyproject.toml`               | Validates `VERSION`/`SPEC` args |
| **test-persona**       | Run persona test suite                                       | `uv run pytest -q test/test_personas_cli.py` |
| **keychain-test**      | macOS only: test keychain integration                        | Persona add/set/list/remove; keychain rows check |
| **providers-coverage** | Report provider property coverage                            | `uv run python scripts/provider_coverage.py` |
| **docstrings**         | Verbose docstring coverage                                   | `uv run interrogate -vv … --fail-under=100` |
| **check-all**          | Full local gate (ruff + mypy + interrogate + manifest)       | Explicit runs on `src scripts test` |
| **clean**              | Remove build artifacts + venv/site                           | `rm -rf dist build *.egg-info site/ .venv` |
| **clean-pyc**          | Remove `__pycache__` + pyc/pyclass files                     | `find … -delete` |
| **clean-all**          | Deep clean (incl. smoke venv)                                | `make clean clean-pyc; rm -rf .smoke-venv` |
| **help**               | Print this help map                                          | Greps `##` docstrings |

---

**Note:** All commands use `uv` consistently, respect strict lint/type/docstring/test gates, and follow the OS-agnostic/secret-safe practices defined in this project.
