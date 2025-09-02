# adif-mcp: Unified Plan (Demo → Production)

This document consolidates the **demo scope** with the **production-grade baseline**, and clarifies where **MCP manifests** should live as we evolve this repo into a stable MCP server. It’s the single planning page to review and iterate on.

---

## 1. TL;DR (decisions)
- **Manifests live inside the package** so they ship with the server:
  - Canonical: `src/adif_mcp/mcp/manifest.json`
  - Provider manifests (optional, only if exposing provider-scoped tools):
    `src/adif_mcp/providers/<prov>/mcp/manifest.json`
- **Keep one source of truth** for each manifest. Remove the legacy root `mcp/` folder after moving the manifest.
- Probes, CLI and quality gates are ✅. Next up: add CI smoke (no network) and tag `v0.2.0`.

---

## 2. Current Surface (working today)
- **Probes**: GET-only and safe. `lotw`/`eqsl`/`qrz` ⇒ HTTP 200; `clublog` ⇒ expected 403 with redaction.
- **CLI**:
  - `adif-mcp provider index-check …` (no network)
  - `adif-mcp provider probe …` (network)
- **Quality**: `ruff`, `mypy --strict`, `interrogate` all green. `make gate` and `make smoke-all` green.
- **DNS**:
  - `adif-mcp.com` → GitHub Pages
  - `eqsl.adif-mcp.com` / `lotw.adif-mcp.com` → `adif-mcp.com`

---

## 3. Manifests: Placement & Rules

### Canonical Placement
- **Server manifest** (single contract for the MCP server):
  ```
  src/adif_mcp/mcp/manifest.json
  ```
- **Optional per-provider manifests** (only if you expose provider-scoped tools or ship provider plugins):
  ```
  src/adif_mcp/providers/eqsl/mcp/manifest.json
  src/adif_mcp/providers/lotw/mcp/manifest.json
  ```

## 4. Validation
The `make manifest` target scans all tracked `manifest.json` files and validates them. No changes needed when you move manifests under `src/…`.

### One Source of Truth
Keep **exactly one** manifest per server or plugin. After moving the root manifest, **remove the root `mcp/`** to avoid drift.

---

## 5. Demo Scope (kept as plan; not all implemented yet)

### What the demo *will* do
- Fetch new **eQSL** entries since a date.
- Answer:
  1) “What confirmed eQSLs did I get this week?”
  2) “How many eQSL confirmations on 20m FT8 in August?”

### Minimal Data Surface (from eQSL ADIF)
- `CALL`, `QSO_DATE`, `TIME_ON`
- `BAND`, `MODE`, `FREQ` (optional)
- `EQSL_QSL_RCVD`, `EQSL_QSLRDATE`
- Optional passthrough: `RST_SENT`, `RST_RCVD`, `GRIDSQUARE`, `COMMENT`

### Tools (demo)
- **`eqsl.fetch_inbox`**
  - Input: `{ since?: "YYYY-MM-DD" }`
  - Output: `{ records: QsoRecord[] }`
  - Behavior: real GET to `DownloadInBox.cfm` or mock file if `MOCK=1`
- **`eqsl.filter_summary`**
  - Input: `{ band?, mode?, date_from?, date_to?, confirmed_only? }`
  - Output:
```json
{
  "total": 42,
  "confirmed": 19,
  "by_band": [{"band":"20m","count":...}],
  "by_mode": [{"mode":"FT8","count":...}],
  "sample": [ /* first 10 QSOs */ ]
}
```

**Why two tools?** `fetch_inbox` centralizes I/O + normalization; `filter_summary` gives the agent fast analytics without repeated downloads.

---

## 6. Production Baseline (condensed)

### Structure
```
adif-mcp/
  pyproject.toml
  src/adif_mcp/
    mcp/manifest.json           # ← canonical server manifest
    probes/…                    # safe probes (done)
    providers/…                 # adapters (done)
    tools/…                     # manifest validation, future eqsl tools
    models.py                   # ADIF models (present; to expand)
    # planned
    enums.py
    normalize.py
  docs/
  tests/
```

*(If you later split provider plugins, each plugin repo keeps its own `src/adif_mcp_<prov>/mcp/manifest.json`.)*

### Types & Validation
- Treat ADIF 3.1.x as a formal schema via Pydantic models.
- Enumerations loaded from data files, not hard-coded.
- JSON Schema exports for tool I/O.
- Normalization: uppercase CALL, YYYYMMDD date, HHMM[SS] time, MHz/frequency, watts/power.

### MCP Design
- Small, explicit tools with strict schemas and conservative defaults (limits, pagination, timeouts).
- Machine-readable errors; narrow tools over one mega-tool.

### Testing & CI
- Golden fixtures for valid/invalid ADIF.
- Contract tests for MCP tools (JSON examples & snapshots).
- CI: `uv sync --frozen`, `ruff`, `mypy --strict`, `pytest -q`, `make manifest`.

### Security & Ops
- Secrets via env/keyring; never log secrets.
- Later: API façade with OAuth2/API keys; strict request bodies (Pydantic + size caps).

---

## 7. Immediate Actions (manifests + doc consolidation)

**Move the server manifest** into the package:
```bash
mkdir -p src/adif_mcp/mcp
git mv mcp/manifest.json src/adif_mcp/mcp/manifest.json
```

**Docs**: Add a pointer in `docs/mcp/manifest.md` that the canonical manifest now lives under `src/adif_mcp/mcp/manifest.json`. The existing `make manifest` target validates all tracked manifests.

**Keep this plan** checked in as `docs/dev/plan.md` so there’s one planning page.

---

## 8. Roadmap (near-term)
**CI smoke**: run `make probe-index` (no network) in CI; skip network probes by default.
**Version & tag**: bump to `0.2.0`, update `CHANGELOG.md`, tag `v0.2.0`.
**Demo tools**: implement `eqsl.fetch_inbox` + `eqsl.filter_summary` with mock fallback; add examples in manifest.
**Docs**: `docs/integrations/eqsl/index.md` quickstart (mock + real creds).
**Models**: expand ADIF models/enums + normalization helpers.

---

## Acceptance Checks (every merge)
- `make gate` ✅
- `make smoke-all` ✅
- `make manifest` ✅
- Probes: `make probe-all` ✅
