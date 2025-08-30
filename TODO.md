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

## Callsign Variants (Prefixes & Suffixes)

- **Context:** Many operators use portable or regional variants of their callsigns, such as `KI7MT/4`, `KI7MT/QRP`, or international prefixes like `ZL/KI7MT`.
- **Current State:** ADIF spec allows `/` in callsigns, and our parser already handles them as plain strings. No breakage today.
- **Need:** Users may want to associate these variants with their main persona for log matching and provider queries.
- **Proposed Approach:**
  - Extend `Persona` schema with an optional `aliases` list.
  - Example:
    ```json
    {
      "name": "Primary",
      "callsign": "KI7MT",
      "aliases": ["KI7MT/4", "KI7MT/QRP", "ZL/KI7MT"],
      ...
    }
    ```
  - Update lookup logic to check both `callsign` and any `aliases`.
- **Priority:** Low (not blocking).
- **Future Benefit:** Simplifies multi-environment ops (portable, contest, DXpeditions) without duplicating personas.
