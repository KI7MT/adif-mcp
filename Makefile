# ===============================
# ADIF-MCP (Java) – Makefile
# Wraps Gradle build/test + MkDocs docs via UV
# ===============================

# -------- Project meta --------
PROJECT ?= adif-mcp
JDK_VER ?= 21

# Colors
C_G = \033[01;32m
C_C = \033[01;36m
C_Y = \033[01;33m
C_NC = \033[0m

# -------- Helpers --------
GRADLEW = ./gradlew

.PHONY: help
help: ## Show help with targets and descriptions
	@echo "Developer Commands (Java + Gradle + MkDocs)"
	@echo "-------------------------------------------"
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# -------- Gradle tasks --------
.PHONY: build test check javadoc run clean clean-all
build: ## Gradle: compile + package
	$(GRADLEW) --no-daemon clean build

test: ## Gradle: run unit tests
	$(GRADLEW) --no-daemon test

check: ## Gradle: code style / static checks (Spotless/Checkstyle/PMD if configured)
	$(GRADLEW) --no-daemon check

javadoc: ## Gradle: generate Javadocs
	$(GRADLEW) --no-daemon javadoc

run: ## Gradle: run app with args="--help" (override with ARGS=...)
	$(GRADLEW) --no-daemon run --args="$(ARGS)"

clean: ## Remove Gradle artifacts
	@echo ""
	@echo "[clean] - Holding place for Gradle artifacts"
#	$(GRADLEW) --no-daemon clean
	@echo "Done"
	@echo ""

clean-all: clean ## Deep clean (Gradle + docs caches)
	@echo "[clean all] - Python and Gradle Artifacts"
	rm -rf .venv .docs-venv .ruff_cache .mypy_cache .pytest_cache site dist build
	@echo "Done"
	@echo ""

# -------- Gate / Smoke --------
.PHONY: gate smoke-all quick
gate: ## CI-like gate: build, test, check, javadoc
	@echo "$(C_C)[gate] build$(C_NC)"
	$(GRADLEW) --no-daemon build
	@echo
	@echo "$(C_C)[gate] test$(C_NC)"
	$(GRADLEW) --no-daemon test
	@echo
	@echo "$(C_C)[gate] check$(C_NC)"
	$(GRADLEW) --no-daemon check
	@echo
	@echo "$(C_C)[gate] javadoc$(C_NC)"
	$(GRADLEW) --no-daemon javadoc
	@echo
	@echo "$(C_G)[gate] OK$(C_NC)"

smoke-all: ## Full local smoke: clean, gate, docs build
	@echo "$(C_C)[smoke] clean-all$(C_NC)"; $(MAKE) clean-all
	@echo
	@echo "$(C_C)[smoke] gate$(C_NC)";      $(MAKE) gate
	@echo
	@echo "$(C_C)[smoke] docs-build$(C_NC)"; $(MAKE) docs-build
	@echo
	@echo "$(C_G)[smoke-all] OK$(C_NC)"

quick: ## Fast compile + single run (override ARGS=...)
	$(GRADLEW) --no-daemon classes
	$(GRADLEW) --no-daemon run --args="$(ARGS)"

# -------- Docs (MkDocs via uv) --------
.PHONY: docs-venv docs-install docs-build docs-serve
docs-venv: ## Ensure a Python 3.11 uv venv for docs
	uv venv --python 3.11

docs-install: docs-venv ## Install MkDocs deps into the uv venv
	uv pip install -r requirements.docs

docs-build: docs-install ## Build docs to ./site
	uv run mkdocs build --strict
	@echo "site/ built"

docs-serve: docs-install ## Serve docs locally
	uv run mkdocs serve -a 127.0.0.1:8000

# -------- Release helpers (optional) --------
.PHONY: dist installDist shadow
dist: ## Gradle: assemble distributable archives
	$(GRADLEW) --no-daemon assemble

installDist: ## Gradle: install runnable distribution under build/install
	$(GRADLEW) --no-daemon installDist

shadow: ## Gradle: build fat/uber JAR (requires shadow plugin)
	$(GRADLEW) --no-daemon shadowJar
