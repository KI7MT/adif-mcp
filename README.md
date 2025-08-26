# ADIF MCP

__AI is Here, Don't Fight it, Embrase It !!__

## Big picture
	•	MCP = contract + guardrails. The manifest describes exactly what tools exist (e.g., import/export ADIF, validate, normalize, reconcile, upload/download, award progress). The server enforces types, schemas, and side-effects.
	•	Agents = workflows on top. Different agent roles orchestrate sequences of safe tool calls: “Validator”, “Normalizer”, “Uploader”, “Reconciler”, “Awards Analyst”, etc. They add reasoning, but the MCP enforces policy.

---

## Core objectives
	1.	Single canonical model for QSOs that maps 1:1 to ADIF 3.1.5 (plus a few normalized fields), decoupling loggers from service quirks.
	2.	Deterministic normalization & validation so a QSO means the same thing everywhere (UTC handling, callsign casing, DXCC entity, grids, band/mode/submode).
	3.	Idempotent syncing to LoTW/eQSL with robust duplicate detection and reconciliation.
	4.	Awards engine substrate that computes progress for ARRL/eQSL awards from the canonical store.

---

## Data & validation layer (inside the MCP)
	•	Canonical schema aligned with ADIF 3.1.5:
	•	Required: CALL, QSO_DATE, TIME_ON, BAND/FREQ, MODE (with SUBMODE), RST_SENT/RCVD, MY_* (station), GRIDSQUARE, DXCC, etc.
	•	Normalized helpers: datetime_utc (from QSO_DATE + TIME_ON), band_code, normalized callsign (uppercase, slash handling), entity_id, lat/lon (if grids present).
	•	Strict validators:
	•	Temporal: UTC only, TIME_ON ≤ TIME_OFF, timezone contamination detection, future dates.
	•	Referential: BAND ↔ FREQ consistency (per ADIF tables), MODE ↔ SUBMODE, DXCC/entity validity at QSO time (prefixes can change with time).
	•	Identity: callsign forms (/P, /QRP, maritime, satellites), portable suffix policies.
	•	Duplicates: define a deterministic “duplicate key” (e.g., CALL + datetime_utc (rounded?) + BAND + MODE + MY_CALL/MY_GRIDSQUARE).
	•	Compatibility cushions:
	•	Tolerate partial ADIF; report correctable vs fatal defects.
	•	Versioning: record the ADIF version that produced the record, keep a lossless raw blob for audit.

---

## Tool surface (examples to include in the manifest)
	•	adif.validate(records) → per-record errors/warnings with ADIF clause references.
	•	adif.normalize(records) → canonicalized fields (UTC time, band/mode mapping, casing, entity resolution).
	•	adif.import(source) / adif.export(filters) → in/out of ADIF 3.1.5 (preserve unknown fields via a passthrough bag).
	•	sync.lotw.upload(records), sync.lotw.fetch(status_since)

## Credentials handled via MCP secrets; results are structured (accepted, duplicates, rejected w/ reasons).
	•	sync.eqsl.upload(records), sync.eqsl.fetch(…)
	•	qsl.match(strategy, scope) → reconcile confirmations from LoTW/eQSL to local canonical store. Strategies: strict (exact match) vs relaxed (small time delta, mode family).
	•	awards.progress(program, filters) → returns rules applied + current progress (e.g., DXCC Mixed, WAS, eQSL eDX). Uses normalized entity/band/mode.
	•	lookup.callsign(callsign, when) (optional) → QRZ/ClubLog/CTY fallback for prefix & entity at date.
	•	audit.log(query) → every mutation has an audit trail (who/when/what), critical for trust.

All tools return structured results (no HTML), with explicit error codes and ADIF spec citations where applicable.

---

## Agent roles (how you’d orchestrate)
	•	Validator Agent: takes an ADIF file, runs validate then normalize, produces a human-readable report + a clean payload.
	•	Uploader Agent: batches by service, honors rate limits, retries, and idempotency tokens; records the remote IDs.
	•	Reconciler Agent: periodically pulls LoTW/eQSL status, runs qsl.match, updates local QSL states, flags conflicts for human review.
	•	Awards Analyst Agent: computes progress deltas, explains what’s missing (e.g., “need 17m in NA for WAS Digital”).
	•	Migration Agent: ingests from legacy logs, maps custom fields to ADIF or stores as APP_ fields, surfaces anomalies


## Design choices that pay off
	•	State machines for QSL status
Per-QSO finite states (e.g., NEW → SENT(LoTW/eQSL) → CONFIRMED → ERROR/RETRY) with timestamps and source. Prevents flip-flopping.
	•	Idempotency keys
Deterministic per-QSO keys so re-uploads don’t create dupes on services that are… creative.
	•	Award rules as data
Don’t hardcode. Express rules in a small declarative DSL (band families, mode groups, entity sets, time-bounded exceptions), so updating for new awards is a data change, not code.
	•	Versioning & replay
Keep original ADIF blobs and normalization “diffs”. Makes audits and reprocessing (when specs change) safe.
	•	PII & credentials
Callsign data is public-ish, but treat passwords/tokens and operator notes as sensitive: encrypted at rest, least-privileged access, and explicit scopes in the manifest.


## Tricky areas to plan for
	•	Entity changes over time (DXCC, special calls): need date-aware prefix tables.
	•	Portable & special suffixes (CALL/XYZ): sometimes imply region; sometimes don’t. Provide a tunable policy.
	•	Time ambiguity: ADIF without seconds; clock drift; overnight QSOs (ON/OFF crossing midnight). Define rules clearly and document them.
	•	Mode/submode families: award logic often groups (e.g., FT8 ∈ DATA); be consistent.
	•	LoTW vs eQSL matching quirks: each has its own tolerance for time/mode/band; encapsulate them in qsl.match(strategy=servic

## Phased plan
	1.	MCP Core (read-only): validate, normalize, import/export, local canonical store. Golden test corpus of ADIF snippets + expected outcomes.
	2.	Sync (LoTW/eQSL): credentials vault, upload/download, robust reconciliation, audit logs.
	3.	Awards: DSL + rule packs (ARRL DXCC/WAS, eQSL awards). Agent that explains gaps.
	4.	Ecosystem adapters: thin shims for popular loggers (N1MM/WSJT-X exports, Cloud loggers) that just call the MCP.
	5.	Governance & conformance: publish a small “ADIF MCP” conformance suite so logger authors can self-test against your contract.

## Why MCP is a great fit here
	•	It insulates every caller from the gnarly corners of ADIF, LoTW, and eQSL, while giving a precise, typed interface.
	•	You get safety (schema validation, idempotency, RBAC/secrets) and extensibility (new tools, new awards) without breaking consumers.
	•	Agents can be simple and focused; the heavy lifting is centralized and trustworthy.
# adif-mcp
