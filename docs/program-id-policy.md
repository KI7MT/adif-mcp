# Program ID & APP_ Field Policy

The ADIF-MCP project uses **registered ADIF Program IDs** to clearly identify log exports and transformations. This ensures transparency, auditability, and compatibility with other ADIF-compliant applications.

## 1. Registered Program IDs

- `ADIF-MCP` — the core engine (https://github.com/KI7MT/adif-mcp)
- `ADIF-MCP-LOTW` — plugin for ARRL Logbook of The World (LoTW) (https://github.com/KI7MT/adif-mcp-lotw)
- `ADIF-MCP-EQSL` — plugin for eQSL.cc (https://github.com/KI7MT/adif-mcp-eqsl)

Each plugin or engine component reports `PROGRAMVERSION` equal to its package release version.

## 2. APP_ Vendor Extensions

To avoid overwriting a user’s original `PROGRAMID`, ADIF-MCP components may add **APP_ fields** with namespaced provenance. Examples:

- `APP_ADIF-MCP_OP` — operation performed (e.g., `normalize`, `validate`, `merge`)
- `APP_ADIF-MCP-LOTW_ACTION` — LoTW operation (`upload`, `fetch`, `merge`)
- `APP_ADIF-MCP-EQSL_TIME` — UTC timestamp of eQSL confirmation merge
- `APP_ADIF-MCP_SESSION` — batch/session UUID for audit trail
- `APP_ADIF-MCP_MANIFEST` — MCP manifest/tool version that executed the action

These fields are optional but recommended when the engine or plugins modify or confirm records.

## 3. Policy Summary

- **Exports from core**: set `PROGRAMID=ADIF-MCP`
- **Exports from plugins**: set `PROGRAMID=ADIF-MCP-LOTW` or `ADIF-MCP-EQSL`
- **Augmenting existing logs**: preserve original `PROGRAMID` and add `APP_` provenance fields

All ADIF files produced are upward-compatible with the ADIF 3.1.5 specification and future revisions.
