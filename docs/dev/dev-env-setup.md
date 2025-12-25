# Developer Environment Setup (Linux & macOS)

This document describes how to set up a full development environment for `adif-mcp` on Linux and macOS.
The project uses **uv**, **pre-commit**, and **modern Python packaging**. These instructions assume you are comfortable with the terminal.

---

## 1. System Requirements

- **Python**: 3.11 or newer (3.13 recommended)
- **uv**: fast Python package manager and build tool
- **git**: version control
- **make**: for running project tasks
- **pre-commit**: for local checks before commit (installed via uv tools)

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git make
```

### macOS
- Install **Xcode Command Line Tools** (for `make`, `git`, compilers):
```bash
xcode-select --install
```
- Install **Homebrew** (if not installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
- Ensure Python 3.11+ is installed (Homebrew or Python.org).

---

## 2. Install uv

The project standardizes on `uv` for dependency management.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify:
```bash
uv --version
```

---

## 3. Clone the Repository

```bash
git clone https://github.com/<your-org>/adif-mcp.git
cd adif-mcp
```

---

## 4. Sync Dependencies

Create and sync the virtual environment:

```bash
uv sync --frozen
```

This will:
- Create `.venv/`
- Install runtime + dev dependencies from `uv.lock`

---

## 5. Install pre-commit Hooks

Install **pre-commit** globally with uv:

```bash
uv tool install pre-commit
```

Register the hooks in this repo:

```bash
pre-commit install
```

You can test them manually:

```bash
pre-commit run --all-files
```

---

## 6. Verify Development Setup

Run all quality gates:

```bash
make gate
```

Expected: all checks (`ruff`, `mypy`, `interrogate`, manifests) should pass.

Run smoke tests:

```bash
make smoke-all
```

Expected: probes and CLI run without errors (Clublog probe may return HTTP 403 by design).

### Final Step: The MCP Handshake

Verify the AI Agent interface is responsive (requires a seeded persona):

```bash
# 1. Seed a test persona
uv run adif-mcp persona add --name TestUser --callsign N0CALL --start 2025-01-01

# 2. Run the audit agent
uv run python test_mcp.py
```

*For the full "Unknown State" testing protocol, see the [Testing Playbook](testing.md).*

---

## 7. Useful Commands

- Format & lint:
```bash
uv run ruff check src --fix
uv run ruff format src
```

- Type checking:
```bash
uv run mypy src test
```

- Docstring coverage:
```bash
uv run interrogate -v -c pyproject.toml
```

- Run tests:
```bash
uv run pytest -q
```

- Validate manifests:
```bash
make manifest
```

---

## 8. macOS Notes

- If using Python from **python.org** installer, you may need:
```bash
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools wheel
```
- If keyring prompts do not appear, install `keyring` backend:
```bash
brew install keyring
```

---

## 9. Linux Notes

- Some Linux distros require a keyring daemon for secrets. If unavailable, credentials will store non-secret refs only.
- Install recommended packages:
```bash
sudo apt install gnome-keyring libsecret-1-0
```

---

## 10. Confirm CLI Works

```bash
uv run adif-mcp --help
```

Should display the CLI help with subcommands.

---
