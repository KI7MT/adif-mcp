# eQSL API (MCP Tools)

- Purpose: confirmations, awards tracking, uploads/queries
- Auth: eQSL credential handling (never exposed to the agent)
- Safety: tool-scoped permissions + audit

- `eqsl.upload(adif_batch)`
- `eqsl.status(callsign, since)`
- `eqsl.confirmations(query)`
