## Completed (up through v0.3.4)

### Core packaging & structure
- src/adif_mcp/ canonical layout
- identity/ namespace (models, store, secrets, manager, errors)
- Resources bundled under resources/ (spec, schemas, providers, mapping/usage)
- Manifests moved into src/adif_mcp/mcp/manifest.json

### Provider probes
- provider index-check (no network)
- provider probe (GET-only, safe, redacting secrets)
- CI/make targets: probe-index, probe-get, probe-all

### Quality gates
- ruff, mypy --strict, interrogate integrated with pre-commit
- CI workflows fixed for uv + pre-commit + manifest validation
- All checks green in CI/CD

### Docs
- Developer setup for Linux/macOS ✅
- Command reference (incl. make help merged) ✅
- Persona management documented (stub + keyring) ✅
- Roadmap and dev plan unified ✅

### Releases
- v0.3.0 → v0.3.4, all tagged, CHANGELOG updated

⸻

## In Progress / Next Milestone (v0.3.5 → v0.4.0)

### Demo tools (eQSL)
- eqsl.fetch_inbox → mock + real mode (still stubbed)
- eqsl.filter_summary → analytics (band/mode/date/confirmed)

### Validation / normalization
- Expand models.py into proper ADIF Pydantic models
- Add normalize.py helpers (callsign, grid, dates, times, rst, freq, power)
- Add enums/ JSON + loader (bands, modes, qsl flags)

### CLI
- Align naming: validate-manifest pattern
- Move dev/test stubs under adif-mcp dev … group

### Docs
- Integrations pages: start with eQSL quickstart
- Add “useful code snippets” section (bash helpers, persona reset, etc.)
- CI smoke doc (how probes run in CI without network)

### CI
- Add make probe-index smoke to CI (non-network)
- Ensure manifest validation runs once (not duplicated across jobs)

⸻

## Near-Term Roadmap (what’s left before calling 0.4.0)
1. Finish eQSL demo tools (real + mock).
2. Normalize ADIF models (basic fields).
3. Expose enums + validation tools (list_enums, validate_adif).
4. Docs polish (CLI help dumps, quickstarts, troubleshooting).
5. Refactor stubs into dev/ CLI group.
