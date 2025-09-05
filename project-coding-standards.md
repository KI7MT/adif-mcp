# Project Coding Standards

This document defines the required style and quality rules for all code in this repository.

## Docstrings
- **Always include docstrings** for:
  - Modules
  - Classes
  - Functions
- Docstrings must explain purpose, inputs, outputs, and side-effects.
- Keep them concise but clear.

## Style & Linting
- **Ruff** is enforced with:
  - Maximum line length of **90 characters**.
- Avoid unnecessary blank lines or noisy comments.
- Keep diffs focused; don’t flood reviews with unrelated changes.

## Type Checking
- **Mypy** must pass cleanly:
  - Always provide correct, explicit type annotations.
  - No `# type: ignore` unless absolutely required, and never leave unused ignores.
  - Remove unused imports or type hints.

## Module Layout
- All Python files under `src/adif_mcp/` must be **inside a proper module** (package).
- No loose scripts directly in `src/adif_mcp/`; each should belong to a submodule.
- Public APIs should be exposed via `__init__.py` where appropriate.

## General Guidance
- Favor clarity over cleverness.
- Keep CLI wiring minimal in `root.py` — delegate functionality to submodules.
- Validate changes against:
  - `make gate`
  - `mypy`, `ruff`, and `interrogate`

## Channel Behaviour
- Do not flood the channel with alternative solutions and excess comments
- If ther is more that one options, mark the first with Recommendes, or preferred.
- If more details is needed, or additional dialog about a topic, we will ask for recomendations or further explination
