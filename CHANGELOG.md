# Changelog

All notable changes to this project will be documented in this file.

**[ unreleased & untagged ]**

## Current Status (v0.4.0-SNAPSHOT)
- Multi-module Gradle build is stable (:core, :cli, :ui, :providers:provider-eqsl)
- CLI: root + ui, serve, providers subcommands
- Providers: eQSL stub visible via ServiceLoader
- UI: JavaFX HelloApp runs
- Docs: Javadocs aggregated via `javadocAll` into docs/javadoc, served by MkDocs
- Sanity check via `make sanity-check` is green

**[ unreleased & untagged ]**

### Changed
- **Project migration notice:** `adif-mcp` (Python) is deprecated.
  Future development continues in **Java 21 + JavaFX**, with MkDocs retained for user guides and Javadocs for developer reference.

### Removed
- Python-specific tooling (mypy, ruff configs, etc.) no longer maintained.
- Python codebase is frozen and preserved only in the `v0.3.7-python` branch.
