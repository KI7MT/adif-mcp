# TODO / Ideas Backlog

This file tracks design ideas and potential refactors.
Not all items will be implemented — it’s a scratchpad for future work.

---

## Centralized Utilities (`utils.py` or `adif_mcp/utils/cli.py`)

- [ ] **`clear()`** → single clear-screen function for all CLI scripts
  ```python
  def clear() -> None:
      """Clear the terminal for readability."""
      os.system("cls" if os.name == "nt" else "clear")
  ```

- [ ] **`print_header(title, description)`** → standardized CLI header output
  ```python
  def print_header(title: str, description: str) -> None:
      """Standardized header block for CLI tools."""
      print(f"{title} - {description}")
      print()
  ```

- [ ] Replace per-script copies with imports from `adif_mcp.utils.cli`.

---

## Single Source of Truth (SSOT) for Paths

- [ ] Store critical paths (`manifest`, `schemas`, `spec`, `providers`) in **`pyproject.toml`**
- [ ] All scripts should **read paths from SSOT** (via `importlib.metadata` or a helper).

---

## Boilerplate / Consistency

- [ ] Add `DEFAULT_TITLE` and `DEFAULT_DESCRIPTION` to each script.
- [ ] Optionally centralize common defaults in `utils.cli`.

---

## Docs & Dev Workflow

- [ ] Expand **Contributing** guide with consistent style tips (headers, `~~~` fences).
- [ ] Move Git Flow notes to **Developer Guide**.
- [ ] Add section for "Why MCP Matters" (philosophy + operator impact).

---

## Testing / CI

- [ ] Add provider coverage check to CI, with configurable threshold.
- [ ] Smoke tests: validate manifest, run coverage script, confirm CLI basics.

---
