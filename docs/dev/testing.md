# Testing Playbook

This document outlines the rigorous testing protocols used to validate `adif-mcp` releases. Our "Gold Standard" is the **Unknown State** test, typically performed on a clean Mac Mini or Linux CI runner, ensuring that no hidden state (cached credentials, virtualenvs, or config files) masks deployment issues.

## 1. The "Unknown State" Protocol

Before any release, we simulate a fresh user installation. This process guarantees that the application bootstraps correctly from zero.

### Step 1: Deep Clean
Remove all build artifacts, virtual environments, and cached bytecode.

```bash
make clean-all
```

### Step 2: Bootstrap
Initialize the environment. This mimics the first-run experience of a developer or CI system.

```bash
make init
```
*Verifies: `uv sync`, dependency resolution, and pre-commit hook installation.*

### Step 3: The Quality Gate
Run the full suite of static analysis and unit tests.

```bash
make gate
```
*Verifies: Linting (Ruff), Types (Mypy), Unit Tests (Pytest), Manifest Validity, and Docstring Coverage.*

---

## 2. Keychain Integration Testing

Because `adif-mcp` relies on the operating system's native keyring (macOS Keychain, Linux Secret Service, Windows Credential Locker), we must verify that secrets can be stored and retrieved outside of the Python process memory.

To verify the keyring backend specifically:

```bash
make keychain-test
```

**Success Criteria:**
- The test script successfully detects a viable backend (e.g., `keyring.backends.macOS.Keyring`).
- It can write a dummy secret.
- It can read that secret back.
- It cleans up after itself.

> **Note:** If this fails on Linux, ensure `gnome-keyring` or `libsecret` is installed and a session daemon is running.

---

## 3. The "Sovereign" Handshake (End-to-End)

Once the build passes `make gate`, we perform a live functional test using the MCP server entry point. This ensures the AI agent interface is responsive.

### Step 1: Seed a Persona
Create a temporary identity to test configuration loading.

```bash
uv run adif-mcp persona add --name TestUser --callsign N0CALL --start 2025-01-01
```

### Step 2: Run the Audit Agent
We use a dedicated script (`test_mcp.py`) to simulate an MCP client (like Claude Desktop) connecting over Stdio.

```bash
uv run python test_mcp.py
```

**Checklist:**
- [ ] **Connection**: "ADIF Audit Agent: Connecting to Sovereign Node..."
- [ ] **Capabilities**: Lists tools like `get_service_metadata`, `lookup_country`, etc.
- [ ] **Execution**: Tools return valid JSON results (not stack traces).
- [ ] **Exit**: The script completes without hanging.
