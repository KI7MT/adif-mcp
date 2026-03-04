# eQSL Integration

## About eQSL

[eQSL.cc](https://www.eqsl.cc/) is an electronic QSL card exchange service. Operators upload logs and receive graphical eQSL cards from confirmed contacts. eQSL maintains its own award program (eDX100, eWAS, ePFX300, etc.) separate from ARRL awards.

## Plugin: adif-mcp-eqsl

The eQSL plugin provides MCP tools for querying your eQSL account:

| Tool | Description |
|------|-------------|
| `eqsl.upload(adif_batch)` | Upload ADIF records to eQSL |
| `eqsl.status(callsign, since)` | Check inbox and confirmation status |
| `eqsl.confirmations(query)` | Query confirmed QSOs with filters (band, mode, date range) |

## Authentication

eQSL credentials are managed through the adif-mcp persona system. Credentials are stored in your operating system's keyring and are never exposed to AI agents.

```bash
# Set up eQSL credentials for your persona
uv run adif-mcp persona set-credential --persona MyEQSL --provider eqsl \
    --username "${EQSL_USER}" --password "${EQSL_PASS}"
```

## Safety

- All operations are read-only by default
- Upload operations require explicit agent permission
- Credentials are managed by the persona layer -- agents never see passwords
- All actions are logged with `APP_ADIF-MCP-EQSL_TIME` provenance fields

## Program ID

Exports from this plugin are tagged with Program ID `ADIF-MCP-EQSL`, registered with the [ADIF Program ID Registry](https://adif.org.uk/programids.html).
