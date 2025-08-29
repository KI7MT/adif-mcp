# -------------------------------
# Project meta
# -------------------------------
PROJECT ?= adif-mcp
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
# C_C  ?= \033[1;36m
# C_Y  ?= \033[1;33m
# C_NC ?= \033[0m

# Foreground colors
C_R='\033[01;31m'		# red
C_G='\033[01;32m'		# green
C_Y='\033[01;33m'		# yellow
C_C='\033[01;36m'		# cyan
C_NC='\033[0m'		  # no color

# -------------------------------
# Environment / deps
# -------------------------------
setup-dev: ## Create venv, sync deps (incl. dev), install pre-commit hooks
	uv sync --group dev
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
lint: ## Ruff lint
	uv run ruff check .

format: ## Ruff format (in-place)
	uv run ruff format .

type: ## mypy (src only)
	uv run mypy src

test: ## pytest
	uv run pytest -q

smoke: lint type manifest ## quick local gate (lint+type+manifest)
	@echo "[smoke] OK"

gate: ## CI parity gate: lint + type + tests + manifest + docstrings
	$(MAKE) lint
	$(MAKE) type
	$(MAKE) test
	$(MAKE) manifest
	uv run interrogate -c pyproject.toml

# -------------------------------
# Manifest validation
# -------------------------------
.PHONY: manifest
manifest: ## Validate MCP manifest(s)
	@set -e; \
	files=$$(git ls-files | grep -E '(^|/)manifest\.json$$' || true); \
	if [ -z "$$files" ]; then \
	  echo "No manifest.json found"; \
	else \
	  for f in $$files; do \
	    echo "Validating $$f"; \
	    uv run python scripts/validate_manifest.py "$$f"; \
	  done; \
	fi

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
# full smoke test via bash script
# -------------------------------
.PHONY: smoke-all
smoke-all: lint type manifest docs-check ## Run full smoke (lint, type, docstrings, tests, build, install-check, docs)
	./scripts/smoke.sh

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
	@if [ -n "$(SPEC)" ]; then echo $(C_G)"✔ ADIF spec matches ($(SPEC))" ; echo $(N_CN) echo ; fi
	@echo


# -------------------------------
# Docstring coverage (verbose)
# -------------------------------
.PHONY: providers-coverage
providers-coverage: # Prodiver property converage against out ADIF catalog
	uv run python scripts/provider_coverage.py

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
