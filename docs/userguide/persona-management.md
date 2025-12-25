# Personas & Credentials

A persona is a **date-bounded identity** used by the MCP server to fetch authenticated logs. While most operators have a primary callsign, many also manage contest calls, special-event stations, or historical vanity calls.

By defining a persona with a specific `start` date (and optional `end` date), you ensure that log queries and confirmations are routed to the correct credentials for that specific time period.

## Architecture

The system separates **Identity** (Persona) from **Access** (Credentials).

### 1. Persona Index (Metadata)
Stored in `~/.config/adif-mcp/personas.json`. This file contains **non-secret** configuration:
- Persona Name (e.g., "Primary", "FieldDay2025")
- Callsign
- Date Range (Start/End)
- Provider Usernames (References)

### 2. Secure Keyring (Secrets)
Passwords and API tokens are **never** stored in plain text. They are injected into your operating system's native keyring (macOS Keychain, Linux Secret Service, Windows Credential Locker).

- **Service**: `adif-mcp`
- **Key**: `{persona}:{provider}:{username}`

## Persona Quick Start

Initialize your environment by creating a primary persona and injecting its credentials.

> **Note**: The `--start` date is mandatory to establish the authoritative timeline for the logbook.

```
# 1. Create Primary Persona (Start date required)
uv run adif-mcp persona add \
  --name Primary \
  --callsign KI7MT \
  --start 2020-01-01

# 2. Inject Credentials (Prompts for password securely)
uv run adif-mcp creds set \
  --persona Primary \
  --provider lotw \
  --username ki7mt

# 3. Verify
uv run adif-mcp persona list
```

## Commands

List - Shows each persona, callsign, date span, and which providers have credentials references.
```
uv run adif-mcp persona list
```

Add / Update - Re-using the same --name updates the persona (callsign/dates).
```
uv run adif-mcp persona add \
  --name <PersonaName> \
 --callsign <CALL> \
 [--start YYYY-MM-DD] \
 [--end   YYYY-MM-DD]
```

Show
```
# By persona name (default)
uv run adif-mcp persona show <PersonaName>

# By callsign (disambiguates multiple personas that share a call)
uv run adif-mcp persona show --by callsign <CALL>
```

Set credential (non-secret ref + secret in keyring)
```
uv run adif-mcp persona set-credential \
  --persona <PersonaName> \
  --provider {lotw|eqsl|qrz|clublog} \
  --username <account_username>
# Prompts for password/token securely
```

Remove
```
# Remove a single persona
uv run adif-mcp persona remove <PersonaName>

# Remove ALL personas (destructive; index only—does not purge keyring)
uv run adif-mcp persona remove-all
```

JSON on disk (reference)

Your personas.json
- Passwords/tokens **are not** stored here—only usernames/refs.

```json
{
  "personas": {
    "Primary": {
      "name": "Primary",
      "callsign": "KI7MT",
      "start": null,
      "end": null,
      "providers": {
        "lotw": { "username": "ki7mt" }
      }
    },
    "ContestW7A": {
      "name": "ContestW7A",
      "callsign": "W7A",
      "start": "2025-03-01",
      "end": "2025-03-31",
      "providers": {
        "lotw": { "username": "w7a_lotw" }
      }
    }
  }
}
```

## How MCP will pick a persona (design intent)

When you or an agent asks a log question, the eventual selection logic can:
1. Filter personas by callsign (if specified), otherwise consider all.
2. Prefer personas whose date range covers the QSO dates being queried.
3. Use the provider that’s requested (or the best available for the query).
4. Fall back sensibly (e.g., no date filters → show all matching personas).

This keeps special-event accounts separate until you intentionally merge them at the provider (e.g., LoTW/eQSL), while still letting you query broadly when you want.

Troubleshooting
- “No personas configured.”

Create one:

```bash
uv run adif-mcp persona add --name Primary --callsign <CALL>
```

- “Secret was NOT stored.”
Your environment likely lacks a keyring backend. Install one (e.g., keyring + OS backend) and re-run persona set-credential. Non-secrets were saved; only the secret failed.

- Wrong date format
Use ISO dates: YYYY-MM-DD.

- Multiple personas share a callsign
Use persona show --by callsign <CALL> to inspect each; the UI will show their date spans.


## Security notes
- Credentials are stored via the OS keyring whenever possible.
- You can safely commit personas.json if you wish (it contains no secrets), though it usually lives in your home config directory.
- If you rotate provider passwords, simply re-run persona set-credential for the affected persona/provider.
