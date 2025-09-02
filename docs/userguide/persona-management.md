# Personas & Credentials

A persona is simply a way to represent an operator’s on-air identity. Most hams use one primary callsign, but many also have contest calls, special-event calls, or past vanity calls that are still linked to their logging accounts. A persona lets you keep these identities separate, with optional start and end dates, so your log queries and confirmations always line up with the right callsign history.

A keyring is your operating system’s built-in secure storage for secrets like passwords or tokens. Instead of saving provider passwords in plain text, ADIF-MCP only saves the non-sensitive reference in its config file, while the actual secret is handed off to the system keyring. That means credentials are encrypted and protected the same way your browser or email client secures saved logins.

Personas let you manage multiple operator identities (callsigns and their date ranges) and connect each one to provider credentials (LoTW, eQSL, QRZ, Club Log). This solves real-world cases like:
- Primary call (no dates)
- Temporary/special-event/contest calls (date-bounded)
- Old calls merged into LoTW/eQSL
- Multiple accounts per provider

Personas JSON files store `non-secret` metadata on disk; secrets (passwords/tokens) are saved in your OS keyring.

## Where Data Lives
Index JSON (non-secret):

```
~/.config/adif-mcp/personas.json (default)

# This psth is configrable via the project’s pyproject.toml

[tool.adif]
personas_index = "path/to/personas.json"
```

Provider Access Credentials ( secrets ) for LoTW, eQSL, Clublog, etc

- Secrets (passwords/tokens) are stored in the system keyring under:
	- service: adif-mcp
	- key: {persona}:{provider}:{username}

If keyring isn’t available, the CLI will still save the non-secret reference and tell you the secret was not stored.


## Persona Quick Start

Create a primary persona and a date-bounded special-event persona, then attach credentials:

```
# 1) Fresh list (may show "No personas configured." on first run)
uv run adif-mcp persona list

# 2) Primary persona (no dates)
uv run adif-mcp persona add --name Primary --callsign KI7MT

# 3) Special-event / contest persona (date-bounded)
uv run adif-mcp persona add \
  --name ContestW7A \
  --callsign W7A \
  --start 2025-03-01 \
  --end   2025-03-31

# 4) Attach provider credentials (prompts for password; stores in keyring)
uv run adif-mcp persona set-credential \
  --persona Primary \
  --provider lotw \
  --username ki7mt

uv run adif-mcp persona set-credential \
  --persona ContestW7A \
  --provider lotw \
  --username w7a_lotw

# 5) Inspect
uv run adif-mcp persona list
uv run adif-mcp persona show Primary
uv run adif-mcp persona show --by callsign W7A
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
