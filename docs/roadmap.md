# Roadmap

## 1. Recently Completed (v0.3.0 → v0.3.1)
- Identity migration
- Split into identity/models.py, identity/store.py, identity/secrets.py, identity/manager.py, identity/errors.py.
- Removed old persona_manager.py and personas.py.
- Moved personas.json index and secret handling into cleanly separated layers.
- Resources re-org
- Moved provider JSONs, schemas, and ADIF spec metadata under src/adif_mcp/resources/.
- Verified adif_mcp.resources APIs load correctly in both sdist and wheel.
- CI & QA
- Ruff, Mypy, Interrogate all green at 100%.
- Pre-commit integrated with uv across workflows.
- make gate and make smoke-all fully green.
- Packaging
- Wheel + sdist validated: resources bundled, CLI functional.
- Fixed pyproject entry points (no stale persona manager entry).

⸻

## 2. Next Release: v0.3.2 (Stability & Docs polish)
- Improve docs coverage:
- Publish Persona Management guide in docs/userguide/ and docs/dev/.
- Update developer guide with pre-commit + uv workflows.
- Consolidate old checklists into Roadmap + Dev Plans.
- Add smoke tests for provider probe CLI (adif-mcp provider probe ...) to CI.
- Harden manifest validation (ensure schemas load from resources, not repo paths).
- Add typed tests for identity errors (MissingPersonaError, etc.).

⸻

## 3. Planned: v0.4.0 (Demo Tools + Normalization)
- Demo integrations
- eQSL demo tools:
- eqsl.fetch_inbox (with MOCK mode, sample ADIF in tests/data).
- eqsl.filter_summary (aggregate by band/mode/date).
- LoTW read-only probe (extension of inbox_probe).
- Normalization helpers
- Add normalize/ module:
- Callsign uppercasing, gridsquare validation, ADIF date/time normalization.
- Enumerations for band/mode/submode/qsl flags from JSON resources.
- Pydantic-based QsoRecord validation pipeline with strict vs lenient modes.
- CLI polish
- Add adif-mcp validate for batch ADIF JSON validation.
- Add adif-mcp enums for listing supported bands/modes.
- CI/QA
- Golden ADIF fixtures (good + bad) under test/data/.
- Conformance tests for validation and enum resolution.

⸻

## 4. Longer-Term Goals
- Standalone identity library (persona manager generalized for ham radio and beyond).
- MCP server façade (FastAPI) for agent integration.
- Plugin repos (adif-mcp-eqsl, adif-mcp-lotw) once core stabilizes.
- Expanded ADIF 3.2.x support as spec evolves.
