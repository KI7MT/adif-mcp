# ===============================
# ADIF-MCP (Java) – Makefile
# Gradle build/test + MkDocs (via uv)
# ===============================

# -------- Project meta --------
PROJECT           ?= adif-mcp
JDK_VER           ?= 21
PY_VER            ?= 3.11

# -------- Colors --------
COLOR_GREEN  = \033[01;32m
COLOR_CYAN   = \033[01;36m
COLOR_YELLOW = \033[01;33m
COLOR_RESET  = \033[0m

# -------- Helpers --------
GRADLEW         = ./gradlew
GRADLE_ARGS     = --no-daemon
GRADLE_NOCACHE  = --no-configuration-cache

.DEFAULT_GOAL := help

# --------------------------------
# Help
# --------------------------------
.PHONY: help
help: ## Show help with targets and descriptions
	@echo "Developer Commands (Java + Gradle + MkDocs)"
	@echo "-------------------------------------------"
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# --------------------------------
# Gradle basics
# --------------------------------
.PHONY: build test check run clean clean-all clean-local
build: ## Gradle: clean + build all modules
	$(GRADLEW) $(GRADLE_ARGS) clean build

test: ## Gradle: run unit tests
	$(GRADLEW) $(GRADLE_ARGS) test

check: ## Gradle: aggregated checks (if configured)
	$(GRADLEW) $(GRADLE_ARGS) check

run: ## Gradle: run CLI with ARGS (e.g. make run ARGS="--help")
	$(GRADLEW) $(GRADLE_ARGS) $(GRADLE_NOCACHE) :cli:run --args="$(ARGS)"

clean: ## Remove Gradle build outputs
	$(GRADLEW) $(GRADLE_ARGS) clean

clean-local: ## Remove local caches / sites (keeps docs/dev/api wrappers)
	@echo "[clean-local] removing local caches and site/"
	rm -rf .venv .docs-venv .ruff_cache .mypy_cache .pytest_cache site build dist docs/javadoc
	@echo "Done."

clean-all: clean clean-local ## Deep clean
	@true

# --------------------------------
# Javadoc
# --------------------------------
.PHONY: javadoc javadoc-all stage-javadoc publishJavadoc

javadoc: ## Generate per-module Javadocs (spi, core, cli)
	$(GRADLEW) $(GRADLE_ARGS) :spi:javadoc :core:javadoc :cli:javadoc

javadoc-all: ## Aggregate all Javadocs to build/docs/javadoc-all
	$(GRADLEW) $(GRADLE_ARGS) javadocAll

stage-javadoc: javadoc-all ## Copy aggregated Javadocs to docs/javadoc (for MkDocs)
	@mkdir -p docs/javadoc
	@rsync -a --delete build/docs/javadoc-all/ docs/javadoc/
	@echo "$(COLOR_GREEN)Staged Javadoc to docs/javadoc$(COLOR_RESET)"

publishJavadoc: stage-javadoc ## Convenience alias (stage for docs)
	@true

# --------------------------------
# Docs (MkDocs via uv)
# --------------------------------
.PHONY: docs-venv docs-venv-recreate docs-install docs-build docs-serve

docs-venv: ## Ensure a Python $(PY_VER) uv venv for docs (no prompt)
	@test -d .venv || uv venv --python $(PY_VER) --force

docs-venv-recreate: ## Force-recreate the docs venv
	@rm -rf .venv
	uv venv --python $(PY_VER)

docs-install: docs-venv ## Install MkDocs deps into the uv venv
	uv pip install -r requirements.docs

docs-build: docs-install stage-javadoc ## Build docs to ./site
	uv run mkdocs build --strict
	@echo "site/ built"

docs-serve: docs-install stage-javadoc ## Serve docs locally
	uv run mkdocs serve -a 127.0.0.1:8000

# --------------------------------
# Sanity / smoke
# --------------------------------
.PHONY: sanity-check smoke-all quick
sanity-check: ## Quick sanity: build, CLI help/version, providers/serve, javadoc stage
	$(GRADLEW) $(GRADLE_NOCACHE) clean build
	$(GRADLEW) $(GRADLE_NOCACHE) :cli:run --args="--help"
	$(GRADLEW) $(GRADLE_NOCACHE) :cli:run --args="--version"
	$(GRADLEW) $(GRADLE_NOCACHE) :cli:run --args="providers"
	$(GRADLEW) $(GRADLE_NOCACHE) :cli:run --args="serve"
	$(MAKE) stage-javadoc
	@echo "$(COLOR_GREEN)[sanity-check] OK$(COLOR_RESET)"

smoke-all: ## Full local smoke: clean-all, build/test/check, stage Javadoc, mkdocs build
	@echo "$(COLOR_CYAN)[smoke] clean-all$(COLOR_RESET)"; $(MAKE) clean-all
	@echo "$(COLOR_CYAN)[smoke] build$(COLOR_RESET)";     $(MAKE) build
	@echo "$(COLOR_CYAN)[smoke] test$(COLOR_RESET)";      $(MAKE) test
	@echo "$(COLOR_CYAN)[smoke] check$(COLOR_RESET)";     $(MAKE) check
	@echo "$(COLOR_CYAN)[smoke] javadoc$(COLOR_RESET)";   $(MAKE) stage-javadoc
	@echo "$(COLOR_CYAN)[smoke] docs-build$(COLOR_RESET)";$(MAKE) docs-build
	@echo "$(COLOR_GREEN)[smoke-all] OK$(COLOR_RESET)"

quick: ## Fast compile + run CLI once (override ARGS)
	$(GRADLEW) $(GRADLE_ARGS) classes
	$(GRADLEW) $(GRADLE_ARGS) $(GRADLE_NOCACHE) :cli:run --args="$(ARGS)"
