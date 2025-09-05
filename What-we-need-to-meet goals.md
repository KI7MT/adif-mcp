🚀 What we need to meet goals
1.	Packaging & CLI ( COMPLETE )
[  ] Move convert-adi.py into src/adif_mcp/cli/convert_adi.py.
[  ] Add CLI entry point (uv run adif-mcp convert …).
[  ]	Ensure it works as both library + CLI (SSOT for logic).

2.	Single Source of Truth (SSOT) filesystem layout ( COMPLETE )
[  ] Configurable root (~/.adif-mcp on Linux/macOS; %APPDATA%\adif-mcp on Windows).
[  ] Sub-dirs for conf/, logs/, data/, state/.
[  ] Update persona config to honor this path convention.

3.	Tests ( COMPLETE )
[ X ] Keep tiny smoke tests (already have).
[ X ] Add 1–2 fixture-based tests with real .adi samples (like your 500-QSO eqsl file).
[ X ]Add validation tests against schema in manifest.json.

4.	Sync logic skeleton
	•	Define state file JSON: what’s the last fetch, record count, provider.
	•	Draft sync planner: “fetch new since last X days,” merge, update state.
	•	Provide manual trigger (sync all my QSO’s) plus scheduled/auto refresh.

5.	Docs/User Guide
	•	Document provider limits (e.g. eQSL 50k cap).
	•	Show flows: baseline import → state file → ongoing sync.
	•	Include CLI usage examples + “Type or Talk” chat use cases.

⸻

🪜 Next steps (short-term, actionable)
	1.	Smoke test for convert-adi.py (done).
	2.	Relocate script into package (src/adif_mcp/cli/).
	3.	Add __main__ entry point for CLI.
	4.	Add one more pytest that runs CLI → parses NDJSON and validates schema.
	5.	Commit + merge branch into main.
