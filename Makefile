# -------------------------------
# Project meta
# -------------------------------
PKG := adif-mcp

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  setup-dev          Create venv, sync deps, install pre-commit hooks"
	@echo "  sync               uv sync (install dependencies from pyproject.lock/pyproject)"
	@echo "  add DEP=foo        Add a runtime dependency with uv add"
	@echo "  add-dev DEP=foo    Add a dev dependency with uv add --group dev"
	@echo "  lint               Ruff lint"
	@echo "  format             Ruff format (in-place)"
	@echo "  type               mypy (src only)"
	@echo "  docs               (reserved) build docs"
	@echo "  manifest           Validate MCP manifest(s)"
	@echo "  test               pytest (if/when tests exist)"
	@echo "  smoke              Run lint + type + manifest quickly"
	@echo "  pre-commit-install Install pre-commit hooks (pre-commit & commit-msg)"
	@echo "  clean              Remove common build caches"

# -------------------------------
# Environment / deps
# -------------------------------
.PHONY: setup-dev sync add add-dev
setup-dev: sync pre-commit-install
	@echo "Dev environment ready."

sync:
	uv sync

# Example usage:
#   make add DEP=requests
add:
	@test -n "$(DEP)" || (echo "Usage: make add DEP=<package>[==version]"; exit 1)
	uv add "$(DEP)"

# Example usage:
#   make add-dev DEP=pytest
add-dev:
	@test -n "$(DEP)" || (echo "Usage: make add-dev DEP=<package>[==version]"; exit 1)
	uv add --group dev "$(DEP)"

# -------------------------------
# Quality gates
# -------------------------------
.PHONY: lint format type test smoke
lint:
	uv run ruff check .

format:
	uv run ruff format .

type:
	uv run mypy src

test:
	uv run pytest -q

smoke: lint type manifest
	@echo "[smoke] OK"

# -------------------------------
# Manifest validation
# -------------------------------
.PHONY: manifest
manifest:
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
pre-commit-install:
	pre-commit install -t pre-commit -t commit-msg
	@echo "Hooks installed."

# -------------------------------
# Clean
# -------------------------------
.PHONY: clean
clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build *.egg-info
	@echo "Cleaned."
