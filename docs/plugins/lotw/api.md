# LoTW API (MCP Tools)

- Purpose: confirmations, awards tracking, uploads/queries
- Auth: LoTW credential handling (never exposed to the agent)
- Safety: tool-scoped permissions + audit

- `lotw.upload(adif_batch)`
- `lotw.status(callsign, since)`
- `lotw.confirmations(query)`
