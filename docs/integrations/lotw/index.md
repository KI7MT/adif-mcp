# LoTW Integration

## About LoTW

[Logbook of The World](https://lotw.arrl.org/) (LoTW) is the ARRL's online QSO confirmation system. It uses digital signatures (TQ6/TQ8 certificates) to cryptographically verify contacts, making it the gold standard for award credit (DXCC, WAS, VUCC, Triple Play, etc.).

## Plugin: adif-mcp-lotw

The LoTW plugin provides MCP tools for querying your LoTW account:

| Tool | Description |
|------|-------------|
| `lotw.upload(adif_batch)` | Upload signed ADIF records to LoTW |
| `lotw.status(callsign, since)` | Check upload/processing status |
| `lotw.confirmations(query)` | Query confirmed QSOs with filters (band, mode, date range, entity) |

## Authentication

LoTW credentials are managed through the adif-mcp persona system. Credentials are stored in your operating system's keyring (macOS Keychain, Windows Credential Manager, or Linux Secret Service) and are never exposed to AI agents.

```bash
# Set up LoTW credentials for your persona
uv run adif-mcp persona set-credential --persona MyLOTW --provider lotw \
    --username "${LOTW_USER}" --password "${LOTW_PASS}"
```

## Safety

- All operations are read-only by default (queries and status checks)
- Upload operations require explicit tool-scoped permission from the agent framework
- Credentials pass through the persona layer -- agents see only query results, never tokens or passwords
- All actions are logged with `APP_ADIF-MCP-LOTW_ACTION` provenance fields

## Program ID

Exports from this plugin are tagged with Program ID `ADIF-MCP-LOTW`, registered with the [ADIF Program ID Registry](https://adif.org.uk/programids.html).
