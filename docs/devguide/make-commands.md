# Developer Commands

This page is generated from `make help` for quick reference.

```
Developer Commands
--------------------------------------------------------------------------------------------------------
add-dev                Add a dev dep (usage: make add-dev DEP=pytest)
add                    Add a runtime dep (usage: make add DEP=requests)
check-version          Ensure VERSION and/or SPEC match pyproject.toml (use VERSION=... SPEC=...)
clean-all              Deep clean (incl. smoke venv)
clean-pyc              Remove Python bytecode (__pycache__, *.pyc)
clean                  Remove build artifacts (dist/build/egg-info)
docs-build             Build docs to ./site
docs-dev               Generate docs/dev.md from make help
docs-serve             Serve MkDocs locally on http://127.0.0.1:8000/
format                 Ruff format (in-place)
gate                   CI parity gate: lint + type + tests + manifest + docstrings
help                   Show this help
init                   One-time bootstrap: sync deps, install hooks, run smoke-all
lint                   Ruff lint
manifest               Validate MCP manifest(s)
pre-commit-install     Install pre-commit hooks (pre-commit & commit-msg)
pre-commit-run         Run hooks on all files
print-versions         Show versions from pyproject.toml
release                Tag & push release [usage: make release VERSION=x.y.z SPEC=3.1.5]
setup-dev              Create venv, sync deps (incl. dev), install pre-commit hooks
smoke-all              Full smoke (lint, type, docstrings, tests, build, install-check)
smoke                  quick local gate (lint+type+manifest)
sync                   uv sync dependencies
test                   pytest
type                   mypy (src only)
```
