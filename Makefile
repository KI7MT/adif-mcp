# -------------------------------
# Project meta
# -------------------------------
PROJECT ?= adif-mcp

# Optional defaults printed in the help header (leave blank if N/A)
FROM    ?=
TO      ?=
DB      ?=
PORT    ?=
VERSION ?=

# Default target
.PHONY: help
help: ## Show this help
	@printf "\n$(C_C)%s$(C_NC)\n" "$(PROJECT)  — Developer Commands"
	@printf "%s\n" "-------------------------------------------------------------------------------"
	@printf "$(C_Y)Defaults:$(C_NC) "; \
	printf "FROM=%s " "$(FROM)"; \
	printf "TO=%s " "$(TO)"; \
	printf "DB=%s " "$(DB)"; \
	printf "PORT=%s " "$(PORT)"; \
	printf "VERSION=%s\n\n" "$(VERSION)";
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@printf "\n"


# -------------------------------
# Environment / deps
# -------------------------------
.PHONY: setup-dev sync add add-dev
setup-dev: sync pre-commit-install ## Create venv, sync deps, install pre-commit hooks
	@echo "Dev environment ready."

sync:
	uv sync

add: ## make add DEP=requests
	@test -n "$(DEP)" || (echo "Usage: make add DEP=<package>[==version]"; exit 1)
	uv add "$(DEP)"

add-dev: ## make add-dev DEP=pytest
	@test -n "$(DEP)" || (echo "Usage: make add-dev DEP=<package>[==version]"; exit 1)
	uv add --group dev "$(DEP)"

# -------------------------------
# Quality gates
# -------------------------------
.PHONY: lint format type test smoke
lint: ## run linter to improve code quality
	uv run ruff check .

format: ## run ruff to check and format python files
	uv run ruff format .

type: ## run mypy to catch type-related errors
	uv run mypy src

test: ## run pytest suite for defined tests
	uv run pytest -q

smoke: lint type manifest ## run lint type and manifest checks
	@echo "[smoke] OK"

# -------------------------------
# Manifest validation
# -------------------------------
.PHONY: manifest
manifest: ## validate mcp manifest file
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
# pre-commit
# -------------------------------
.PHONY: pre-commit-install
pre-commit-install: ## install pre-commit hooks
	pre-commit install -t pre-commit -t commit-msg
	@echo "Hooks installed."

# -------------------------------
# full smke test via bash script
# -------------------------------
.PHONY: smoke-all
smoke-all: ## Run full smoke (lint, type, docstrings, tests, build, install-check)
	./scripts/smoke.sh

# -------------------------------
#  Clean everything
# -------------------------------
.PHONY: clean clean-pyc clean-all
clean:  ## Remove build artifacts (dist/build/egg-info)
	rm -rf dist build *.egg-info

clean-pyc:  ## Remove Python bytecode (__pycache__, *.pyc)
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.py[co]' -delete 2>/dev/null || true
	@find . -name '*$py.class' -delete 2>/dev/null || true

clean-all: clean clean-pyc  ## Deep clean (incl. smoke venv)
	rm -rf .smoke-venv
