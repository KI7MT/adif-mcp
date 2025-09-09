# ===============================
# ADIF-MCP (Java) – Makefile
# Wraps Gradle build/test + MkDocs docs via UV
# ===============================
# -------- Project meta --------
PROJECT ?= adif-mcp
JDK_VER ?= 21
# Colors
COLOR_GREEN = \033[01;32m
COLOR_CYAN  = \033[01;36m
COLOR_YELLOW= \033[01;33m
COLOR_RESET = \033[0m
# -------- Helpers --------
GRADLEW = ./gradlew
GRADLE_ARGS = --no-daemon
GRADLE_NOCACHE = --no-configuration-cache
PY_VER ?= 3.11
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show help with targets and descriptions
	@echo "Developer Commands (Java + Gradle + MkDocs)"
	@echo "-------------------------------------------"
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# -------- Gradle tasks --------
.PHONY: build test check javadoc run clean clean-all
build: ## Gradle: compile + package
	$(GRADLEW) $(GRADLE_ARGS) clean build

test: ## Gradle: run unit tests
	$(GRADLEW) $(GRADLE_ARGS) test

check: ## Gradle: code style / static checks (Spotless/Checkstyle/PMD if configured)
	$(GRADLEW) $(GRADLE_ARGS) check

javadoc: ## Gradle: generate Javadocs
	$(GRADLEW) $(GRADLE_ARGS) javadoc

run: ## Gradle: run app with args="--help" (override with ARGS=...)
	$(GRADLEW) $(GRADLE_ARGS) run --args="$(ARGS)"

clean: ## Remove Gradle artifacts
	$(GRADLEW) $(GRADLE_ARGS) clean

clean-local: ## Remove local caches, virtualenvs, and built sites
	@echo "[clean-local] - Python and Docs/Dist artifacts"
	rm -rf .venv .docs-venv .ruff_cache .mypy_cache .pytest_cache site dist build docs/javadoc app/
	@echo "Done"
	@echo ""

clean-all: clean clean-local ## Deep clean (Gradle + docs caches)
	@true

# Sanity Check
sanity-check: ## Gradle: clean, build, cli, ui, javadoc
	$(GRADLEW) clean build
	$(GRADLEW) $(GRADLE_NOCACHE) :cli:run --args="--help"
	$(GRADLEW) $(GRADLE_NOCACHE) :cli:run --args="providers"
	$(GRADLEW) $(GRADLE_NOCACHE) :ui:run
	uv run mkdocs build --strict
	$(GRADLEW) javadocAll
	uv run mkdocs serve


# -------- Gate / Smoke --------
.PHONY: gate smoke-all quick
gate: ## CI-like gate: build, test, check, javadoc
	@echo "$(COLOR_CYAN)[gate] build$(COLOR_RESET)"
	$(GRADLEW) $(GRADLE_ARGS) build
	@echo
	@echo "$(COLOR_CYAN)[gate] test$(COLOR_RESET)"
	$(GRADLEW) $(GRADLE_ARGS) test
	@echo
	@echo "$(COLOR_CYAN)[gate] check$(COLOR_RESET)"
	$(GRADLEW) $(GRADLE_ARGS) check
	@echo
	@echo "$(COLOR_CYAN)[gate] javadoc$(COLOR_RESET)"
	$(GRADLEW) $(GRADLE_ARGS) javadoc
	@echo
	@echo "$(COLOR_GREEN)[gate] OK$(COLOR_RESET)"

smoke-all: ## Full local smoke: clean, gate, docs build
	@echo "$(COLOR_CYAN)[smoke] clean-all$(COLOR_RESET)"; $(MAKE) clean-all
	@echo
	@echo "$(COLOR_CYAN)[smoke] gate$(COLOR_RESET)";      $(MAKE) gate
	@echo
	@echo "$(COLOR_CYAN)[smoke] docs-build$(COLOR_RESET)"; $(MAKE) docs-build
	@echo
	@echo "$(COLOR_GREEN)[smoke-all] OK$(COLOR_RESET)"

quick: ## Fast compile + single run (override ARGS=...)
	$(GRADLEW) $(GRADLE_ARGS) classes
	$(GRADLEW) $(GRADLE_ARGS) run --args="$(ARGS)"


# -------- Docs (MkDocs via uv) --------
.PHONY: docs-venv docs-install docs-build docs-serve
docs-venv: ## Ensure a Python $(PY_VER) uv venv for docs
	uv venv --python $(PY_VER)

docs-install: docs-venv ## Install MkDocs deps into the uv venv
	uv pip install -r requirements.docs

docs-build: docs-install ## Build docs to ./site
	uv run mkdocs build --strict
	@echo "site/ built"

docs-serve: docs-install ## Serve docs locally
	uv run mkdocs serve -a 127.0.0.1:8000

docs-javadoc: ## Build javadocs docs/javadoc/
	$(GRADLEW) $(GRADLE_NOCACHE) javadoc
	rm -rf docs/javadoc && mkdir -p docs/javadoc
	cp -R build/docs/javadoc/* docs/javadoc/


# -------- Release helpers (optional) --------
.PHONY: dist installDist shadow
dist: ## Gradle: assemble distributable archives
	$(GRADLEW) $(GRADLE_ARGS) assemble

installDist: ## Gradle: install runnable distribution under build/install
	$(GRADLEW) $(GRADLE_ARGS) installDist

shadow: ## Gradle: build fat/uber JAR (requires shadow plugin)
	$(GRADLEW) $(GRADLE_ARGS) shadowJar
