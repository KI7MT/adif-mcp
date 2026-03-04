# Quick Start

Get ADIF-MCP running with your AI agent in under 5 minutes.

## Install

=== "pip"

    ```bash
    pip install adif-mcp
    ```

=== "uv"

    ```bash
    uv tool install adif-mcp
    ```

=== "pipx"

    ```bash
    pipx install adif-mcp
    ```

Verify the install:

```bash
adif-mcp --help
```

## Configure Your MCP Client

Add `adif-mcp` to your AI agent's MCP server configuration.

=== "Claude Desktop"

    Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

    ```json
    {
      "mcpServers": {
        "adif-mcp": {
          "command": "adif-mcp"
        }
      }
    }
    ```

=== "Claude Code"

    ```bash
    claude mcp add adif-mcp -- adif-mcp
    ```

=== "VS Code (Copilot)"

    Add to `.vscode/mcp.json`:

    ```json
    {
      "servers": {
        "adif-mcp": {
          "command": "adif-mcp"
        }
      }
    }
    ```

=== "Cursor"

    Add to `.cursor/mcp.json`:

    ```json
    {
      "mcpServers": {
        "adif-mcp": {
          "command": "adif-mcp"
        }
      }
    }
    ```

Restart your MCP client after saving the configuration.

## Verify

Ask your agent:

> "What ADIF tools are available?"

The agent should discover all 7 tools and describe them. If not, see the [Troubleshooting](dev/troubleshooting.md) page.

## Try It Out

Here are some conversation starters to try with your agent:

- **Validate a record:** "Validate this ADIF record: `<CALL:5>KI7MT <BAND:3>20m <MODE:3>FT8 <QSO_DATE:8>20250315 <EOR>`"
- **Check distance:** "What is the great circle distance between grid DN13 and JN48?"
- **Look up a spec field:** "Search the ADIF spec for the DXCC entity code enumeration"
- **Parse a log file:** "Parse the ADIF file at `/home/user/logs/mylog.adi`"
- **Beam heading:** "What heading should I point my antenna from DN13 to work JA1?"

## What's Next

- [Tools Reference](mcp/tools.md) -- full details on all 7 tools with input/output examples
- [MCP Architecture](mcp/overview.md) -- how the server works under the hood
- [ADIF 3.1.6 Spec](spec/spec.md) -- specification coverage and details
