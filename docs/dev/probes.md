# Provider Probes

Provider probes are **sanity checks** only.
They confirm that credentials for a persona can be transported to the provider and accepted, without ingesting any real log data.

## What They Do

- **Index probes** (`provider index-check`):
  - No network calls.
  - Verify that the persona has a username + secret for a provider.
  - Exit code `0` if present, `5` otherwise.

- **GET probes** (`provider probe`):
  - Safe HTTP GET requests to provider endpoints.
  - Endpoints chosen to return small bodies or explicit auth errors.
  - Never POST, never upload logs, never fetch large data.

## Credential Resolution

All credentials are resolved via:

- `PersonaManager` → reads non-secret refs from the persona index (`personas.json`).
- `keyring` → retrieves the associated secret for the persona/provider.

If either is missing, `PersonaManager.require()` raises a typed error.

## Usage Examples

```bash
# Index probes (no network)
uv run adif-mcp provider index-check --provider eqsl    --persona MyEQSL
uv run adif-mcp provider index-check --provider lotw    --persona MyLOTW
uv run adif-mcp provider index-check --provider qrz     --persona MyQRZ
uv run adif-mcp provider index-check --provider clublog --persona MyCLUBLOG

# GET probes (network)
uv run adif-mcp provider probe --provider eqsl    --persona MyEQSL    --timeout 30
uv run adif-mcp provider probe --provider lotw    --persona MyLOTW    --timeout 30
uv run adif-mcp provider probe --provider qrz     --persona MyQRZ     --timeout 30
uv run adif-mcp provider probe --provider clublog --persona MyCLUBLOG --timeout 30
```

Sample Output
```bash
[OK] lotw GET /lotwuser/lotwreport.adi?login=k***t&password=<redacted>&qso_qslsince=2025-09-03 http=200 bytes=6284
[error] clublog GET /logsearchjson.php?call=G7VJR&log=G3TXF&year=2099&api=<redacted> net=HTTPError: HTTP Error 403: Forbidden
```

|Code|Meaning
| ----- | ----- |
|0      | Success / credentials valid.
|3      |Non-200 HTTP status.
|4      |Network error (timeout, SSL, DNS, etc.).
|5      |Persona/provider credential missing.
|2      |Usage error (bad args, JSON parse, etc.).

## Safety
- Redaction: all query parameters like password, api, token are replaced with <redacted> in output.
- Logging: only minimal endpoint path + query (with redactions) is printed.
- No secrets: usernames masked (k***t), secrets never printed.
- Verbose mode (--verbose): prints response body if <512 bytes, with inline redaction.
