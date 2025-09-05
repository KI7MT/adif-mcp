# -------------------------------
# Project meta
# -------------------------------
PROJECT	?= "adif-mcp"
PYTHON	?= python3

# Pull versions from pyproject.toml (Python 3.11+ for tomllib)
PY_PROJ_VERSION := $(shell $(PYTHON) -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])" 2>/dev/null)
ADIF_SPEC_VERSION := $(shell $(PYTHON) -c "import tomllib;d=tomllib.load(open('pyproject.toml','rb'));print(d.get('tool',{}).get('adif',{}).get('spec_version','unknown'))" 2>/dev/null)

# Optional defaults printed in the help header (leave blank if N/A)
FROM    ?=
TO      ?=
DB      ?=
PORT    ?=

# -------------------------------
# Color Helpers
# -------------------------------
# Foreground colors
C_R='\033[01;31m'		# red
C_G='\033[01;32m'		# green
C_Y='\033[01;33m'		# yellow
C_C='\033[01;36m'		# cyan
C_NC='\033[0m'		  # no color

# -------------------------------
# Environment / deps
# -------------------------------
.PHONY: bootstrap setup-dev sync add add-dev init
bootstrap: ## Ensure dev tools (ruff/mypy/pytest/interrogate) are installed
	uv sync --group dev || uv sync

setup-dev: ## Create venv, sync deps (incl. dev), install pre-commit hooks
	uv sync --group dev || uv sync
	pre-commit install -t pre-commit -t commit-msg
	@echo "Dev environment ready."

sync: ## uv sync dependencies
	uv sync

add: ## Add a runtime dep (usage: make add DEP=requests)
	@test -n "$(DEP)" || (echo "Usage: make add DEP=<package>[==version]"; exit 1)
	uv add "$(DEP)"

add-dev: ## Add a dev dep (usage: make add-dev DEP=pytest)
	@test -n "$(DEP)" || (echo "Usage: make add-dev DEP=<package>[==version]"; exit 1)
	uv add --group dev "$(DEP)"

init: ## One-time bootstrap: sync deps, install hooks, run smoke-all
	$(MAKE) setup-dev
	$(MAKE) smoke-all
	@echo
	@echo $(C_G)"init complete"$(C_NC)
	@echo

# -------------------------------
# Quality gates
# -------------------------------
.PHONY: lint format type test smoke gate
lint: bootstrap ## Ruff lint
	uv run ruff check .

format: bootstrap ## Ruff format (in-place)
	uv run ruff format .

type: bootstrap ## mypy (src only)
	uv run mypy src

test: bootstrap ## pytest
	uv run pytest -q

smoke: lint type manifest ## quick local gate (lint+type+manifest)
	@echo "[smoke] OK"

.PHONY: gate lint type test validate-manifest keychain-test
gate: ## CI parity gate: lint + type + tests + manifest + docstrings, keychain test
	$(MAKE) lint
	$(MAKE) type
	uv run interrogate -c pyproject.toml
	$(MAKE) validate-manifest
	$(MAKE) keychain-test

# -------------------------------
# Manifest validation
# -------------------------------

.PHONY: validate-manifest
validate-manifest: ## Validate MCP manifest(s)
	uv run adif-mcp validate-manifest

# -------------------------------
# Docs: export dev commands page
# -------------------------------
.PHONY: docs-dev
docs-dev: ## Generate docs/dev.md from make help
	@mkdir -p docs
	@echo "# Developer Commands" > docs/dev.md
	@echo >> docs/dev.md
	@echo "This page is generated from \`make help\` for quick reference." >> docs/dev.md
	@echo >> docs/dev.md
	@echo '```' >> docs/dev.md
	@$(MAKE) -s help >> docs/dev.md
	@echo '```' >> docs/dev.md
	@echo "Wrote docs/dev.md"

# -------------------------------
# pre-commit
# -------------------------------
.PHONY: pre-commit-install pre-commit-run
pre-commit-install: ## Install pre-commit hooks (pre-commit & commit-msg)
	pre-commit install -t pre-commit -t commit-msg
	@echo "Hooks installed."

pre-commit-run: ## Run hooks on all files
	pre-commit run --all-files

# -------------------------------
# Full smoke (inline; single definition)
# -------------------------------
.PHONY: smoke-all
smoke-all: ## Run smoke checks in a fresh, reproducible env
	@echo "[smoke] lint (ruff)"
	uv run ruff check .
	@echo "[smoke] format check (ruff)"
	uv run ruff format .
		@echo "[smoke] type check (mypy)"
	uv run mypy src
	@echo "[smoke] docstrings (interrogate)"
	uv run interrogate -c pyproject.toml
	@echo "[smoke] manifest validation]"
	$(MAKE) validate-manifest
	@echo "[smoke-all] OK"

# -------------------------------
# Release helper (tags & push)
# -------------------------------
.PHONY: release
release: check-version ## Tag & push release [usage: make release VERSION=x.y.z SPEC=3.1.5]
	@git fetch --tags --quiet
	@if [ -z "$(VERSION)" ]; then echo "ERROR: set VERSION=x.y.z"; exit 1; fi
	@if git rev-parse "v$(VERSION)" >/dev/null 2>&1; then \
	  echo "Tag v$(VERSION) already exists"; exit 1; \
	fi
	git tag -a "v$(VERSION)" -m "chore(release): v$(VERSION)"
	git push origin "v$(VERSION)"
	@echo "🚀 Pushed tag v$(VERSION). GitHub Actions will build & publish."

# -------------------------------
# Docs (MkDocs)
# -------------------------------
.PHONY: docs-build docs-serve
docs-build: ## Build docs to ./site
	@test -f mkdocs.yml || { echo "mkdocs.yml not found; skipping"; exit 0; }
	uv run mkdocs build --strict
	@echo "site/ built"

docs-serve: ## Serve MkDocs locally on http://127.0.0.1:8000/
	@test -f mkdocs.yml || { echo "mkdocs.yml not found"; exit 1; }
	uv run mkdocs serve -a 127.0.0.1:8000

.PHONY: docs-check
docs-check: docs-build ## Verify Mermaid rendered (div.mermaid present; no code.language-mermaid left)
	@set -e; \
	ok_div=$$(grep -R '<div class="mermaid"' -c site/ || true); \
	bad_code=$$(grep -R '<code class="language-mermaid"' -c site/ || true); \
	echo "mermaid divs: $$ok_div; leftover code blocks: $$bad_code"; \
	if [ "$$ok_div" -eq 0 ]; then \
	  echo "❌ No rendered <div class=\"mermaid\"> found in site/"; exit 1; \
	fi; \
	if [ "$$bad_code" -gt 0 ]; then \
	  echo "❌ Found unrendered <code class=\"language-mermaid\"> blocks in site/"; exit 1; \
	fi; \
	echo "✅ Mermaid diagrams look good."

# -------------------------------
# Version checks
# -------------------------------
.PHONY: print-versions check-version
print-versions: ## Show versions from pyproject.toml
	@clear
	@echo $(C_C)"Project Information"$(C_NC)
	@echo "--------------------------------------------"
	@echo "  Project Name .......: $(PROJECT) "
	@echo "  Project Version ....: $(PY_PROJ_VERSION)"
	@echo "  ADIF Spec Version ..: $(ADIF_SPEC_VERSION)"
	@echo

# Usage:
#   make check-version
#   make check-version VERSION=0.1.23
#   make check-version SPEC=3.1.5
#   make check-version VERSION=0.1.23 SPEC=3.1.5
check-version: ## Ensure VERSION and/or SPEC match pyproject.toml (use VERSION=... SPEC=...)
	@clear
	@echo $(C_C)"Project Information"$(C_NC)
	@echo "--------------------------------------------"
	@echo "  Project Name .......: $(PROJECT) "
	@echo "  Project Version ....: $(PY_PROJ_VERSION)"
	@echo "  ADIF Spec Version ..: $(ADIF_SPEC_VERSION)"

	@if [ -n "$(VERSION)" ] && [ "$(PY_PROJ_VERSION)" != "$(VERSION)" ]; then \
	  echo ; echo $(C_Y)"ERROR: pyproject version ($(PY_PROJ_VERSION)) != VERSION ($(VERSION))"; echo $(C_NC) ;echo ; exit 1; \
	fi
	@if [ -n "$(VERSION)" ]; then echo "✔ version matches ($(VERSION))"; fi

	@if [ -n "$(SPEC)" ] && [ "$(ADIF_SPEC_VERSION)" != "$(SPEC)" ]; then \
	  echo ; echo $(C_Y)"ERROR: ADIF spec version ($(ADIF_SPEC_VERSION)) != SPEC ($(SPEC))";  echo $(C_NC) ;echo ; echo ; exit 1; \
	fi
	@if [ -n "$(SPEC)" ]; then echo $(C_G)"✔ ADIF spec matches ($(SPEC))"$(C_NC); fi
	@echo

# -------------------------------
# Test Persona
# -------------------------------
.PHONY: test-persona
test-persona: # Run test using for persona
	uv run pytest -q test/test_personas_cli.py

# -------------------------------
# Keychain test (macOS only)
# -------------------------------
.PHONY: keychain-test
keychain-test: # Test keychain for accepting credentials
ifneq ($(shell uname),Darwin)
	@echo "[keychain-test] skipping Keychain check (not macOS)"
else
	@set -euo pipefail; \
	echo "[keychain-test] starting..."; \
	uv run adif-mcp persona remove-all --yes; \
	# add a persona (must include --start now)
	uv run adif-mcp persona add --name Primary --callsign W7X --start 2000-01-01; \
	# set creds via the new creds subcommand
	uv run adif-mcp creds set Primary lotw --username W7X --password testpw; \
	uv run adif-mcp persona list --verbose; \
	# bad span must be rejected (end before start)
	if uv run adif-mcp persona add --name BadSpan --callsign TEST --start 2025-04-01 --end 2025-03-01; then \
	  echo "ERROR: Bad span accepted"; exit 1; \
	else \
	  echo "OK: rejected (bad date span)"; \
	fi; \
	# cleanup: remove persona and delete its creds
	uv run adif-mcp persona remove-all --yes; \
	uv run adif-mcp creds delete Primary lotw || true; \
	# 'security' returns 44 when no items; neutralize it so pipefail doesn't trip
	if command -v security >/dev/null 2>&1; then \
	  cnt=$$( (security find-generic-password -s adif-mcp 2>/dev/null || true) | wc -l | tr -d ' ' ); \
	  echo "[keychain-test] remaining keychain rows: $$cnt"; \
	fi; \
	echo "[keychain-test] done."
endif

# Probes
probe-index: ## Run index (no network) probes for all providers
	@echo "== Index probes (no network) =="
	uv run adif-mcp provider index-check --provider eqsl    --persona MyEQSL
	uv run adif-mcp provider index-check --provider lotw    --persona MyLOTW
	uv run adif-mcp provider index-check --provider qrz     --persona MyQRZ
	uv run adif-mcp provider index-check --provider clublog --persona MyCLUBLOG

probe-get: ## Run GET (network) probes for all providers
	@echo "== GET probes (network) =="
	uv run adif-mcp provider probe --provider eqsl    --persona MyEQSL    --timeout 30 || true
	uv run adif-mcp provider probe --provider lotw    --persona MyLOTW    --timeout 30 || true
	uv run adif-mcp provider probe --provider qrz     --persona MyQRZ     --timeout 30 || true
	uv run adif-mcp provider probe --provider clublog --persona MyCLUBLOG --timeout 30 || true

probe-all: ## Run both index and GET probes
	$(MAKE) probe-index
	@echo
	$(MAKE) probe-get

# -------------------------------
# Docstring coverage (verbose)
# -------------------------------
.PHONY: docstrings
docstrings: ## Show per-object docstring coverage with file/function lines
	uv run interrogate -vv -c pyproject.toml --fail-under=100 src scripts test

# -------------------------------
# Full local gate
# -------------------------------
.PHONY: check-all
check-all: ## Ruff + mypy + verbose docstrings + manifest validation
	uv run ruff check src scripts test
	uv run mypy src scripts test
	uv run interrogate -vv -c pyproject.toml --fail-under=100 src scripts test
	$(MAKE) manifest

# -------------------------------
# Clean
# -------------------------------
.PHONY: clean clean-pyc clean-all
clean:  ## Remove build artifacts (dist/build/egg-info)
	rm -rf dist build *.egg-info
	rm -rf site/
	rm -rf .venv
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache

clean-pyc:  ## Remove Python bytecode (__pycache__, *.pyc)
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.py[co]' -delete 2>/dev/null || true
	@find . -name '*$$py.class' -delete 2>/dev/null || true

clean-all: clean clean-pyc  ## Deep clean (incl. smoke venv)
	rm -rf .smoke-venv

# -------------------------------
# Help
# -------------------------------
.PHONY: help
help: ## Show this help
	@clear
	@echo "Developer Commands"
	@echo "--------------------------------------------------------------------------------------------------------"
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@printf "\n"
