# Troubleshooting

Common issues and solutions when running ADIF-MCP.

---

## `adif-mcp` command not found

**Symptom:** Running `adif-mcp` returns "command not found."

**Causes and fixes:**

1. **Not installed:** Install with `pip install adif-mcp` or `uv tool install adif-mcp`.
2. **Not on PATH:** If installed with `pip install --user`, ensure `~/.local/bin` is in your `PATH`.
3. **Wrong venv:** If using a virtual environment, make sure it's activated: `source .venv/bin/activate`.
4. **uv tool:** If installed via `uv tool install`, the binary is at `~/.local/bin/adif-mcp`. Ensure `~/.local/bin` is on `PATH`.

Verify:

```bash
which adif-mcp
adif-mcp --help
```

---

## MCP client can't connect

**Symptom:** Your AI agent doesn't see any ADIF tools after configuration.

**Fixes:**

1. **Restart the client.** Claude Desktop, Cursor, and VS Code all require a restart after editing MCP config.
2. **Check the command path.** The `"command"` in your MCP config must resolve to the actual binary. Test by running the command in your terminal first.
3. **Check JSON syntax.** A trailing comma or missing brace in your MCP config will silently fail.
4. **stdio transport.** ADIF-MCP uses `stdio` transport by default. No port or URL configuration is needed.

Test the server directly:

```bash
echo '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}' | adif-mcp
```

You should see a JSON response with the server's capabilities.

---

## Keyring backend not found (Linux)

**Symptom:** Errors like `No recommended backend was available` when using persona/credential features.

**Cause:** The `keyring` library needs a system secret service. Headless Linux servers often lack one.

**Fixes:**

=== "GNOME / Desktop Linux"

    ```bash
    sudo apt install gnome-keyring      # Debian/Ubuntu
    sudo dnf install gnome-keyring      # Fedora/RHEL
    ```

=== "Headless Linux"

    Install the `keyrings.alt` backend for file-based storage:

    ```bash
    pip install keyrings.alt
    ```

    Or set the plaintext backend explicitly:

    ```bash
    export PYTHON_KEYRING_BACKEND=keyrings.alt.file.PlaintextKeyring
    ```

    !!! warning
        The plaintext backend stores credentials unencrypted. Use it only on single-user machines.

---

## `parse_adif` file not found

**Symptom:** `parse_adif` returns a file-not-found error even though the file exists.

**Cause:** The `file_path` parameter requires an **absolute path**.

**Fix:** Use the full path:

```
/home/user/logs/mylog.adi      (correct)
~/logs/mylog.adi               (may not work -- depends on agent)
mylog.adi                      (will not work)
```

---

## Pre-commit hook failures

**Symptom:** `git commit` is rejected by pre-commit hooks (ruff, mypy, interrogate).

**Fix workflow:**

```bash
# 1. Fix the issues reported by the hook
# 2. Stage the fixes
git add -u

# 3. Commit again (do NOT use --no-verify)
git commit -m "fix: resolve lint issues"
```

Common hook issues:

| Hook | Fix |
|------|-----|
| `ruff` | Run `ruff check --fix .` then `ruff format .` |
| `mypy` | Add type annotations to new/changed code |
| `interrogate` | Add docstrings to new public functions/classes |

---

## MCP Inspector debugging

For interactive debugging, run the server with streamable-http transport:

```bash
adif-mcp --transport streamable-http
```

Then connect with [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to test tools interactively.
