"""
Persona management models and storage.

A *persona* represents one operator identity (callsign plus optional
active date range). Each persona may have references to provider
accounts (e.g., LoTW, eQSL, Club Log), with only non-secret metadata
(username, callsign, dates) persisted in JSON.

Secrets (passwords, API tokens) are never written to disk. Instead,
they are stored in the system keyring under a deterministic key:

    service  = "adif-mcp"
    username = "{persona}:{provider}:{account_name}"

JSON storage layout (example: ~/.config/adif-mcp/personas.json):

    {
      "personas": {
        "Primary": {
          "name": "Primary",
          "callsign": "KI7MT",
          "start": null,
          "end": null,
          "providers": {
            "lotw": {"username": "ki7mt"}
          }
        }
      }
    }

This module defines:
- `CredentialRef`: a TypedDict for non-secret provider reference.
- `Persona`: a dataclass for a single operator identity.
- `PersonaStore`: a JSON-backed manager for CRUD operations.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from adif_mcp.cli import cli


@pytest.fixture()
def tmp_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Point HOME to a temp dir so personas.json lives in ~/.config/adif-mcp/.
    """
    home = tmp_path / "home"
    (home / ".config" / "adif-mcp").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)  # keep path deterministic
    return home


def test_persona_lifecycle(tmp_home: Path, monkeypatch: pytest.MonkeyPatch):
    """_summary_

    Args:
        tmp_home (Path): _description_
        monkeypatch (pytest.MonkeyPatch): _description_

    Returns:
        _type_: _description_
    """
    runner = CliRunner()

    # Stub keyring so tests don’t depend on system keyring
    class _DummyKR:
        """Stub keyring so tests don’t depend on system keyring"""

        def set_password(self, *a, **k):  # no-op
            """Set persona password"""
            return None

    monkeypatch.setitem(os.environ, "PYTHONWARNINGS", "ignore")  # quiet optional deps
    monkeypatch.setenv("ADIF_MCP_TESTING", "1")  # (if you want test-only branches)
    monkeypatch.setenv("LC_ALL", "C")

    # Make import-time keyring patch simple
    monkeypatch.setenv("ADIF_MCP_FAKE_KEYRING", "1")
    import sys
    import types

    sys.modules.setdefault(
        "keyring", types.SimpleNamespace(set_password=_DummyKR().set_password)
    )

    # 0) list -> empty
    res = runner.invoke(cli, ["persona", "list"])
    assert res.exit_code == 0
    assert "No personas configured" in res.output

    # 1) add
    res = runner.invoke(
        cli,
        [
            "persona",
            "add",
            "--name",
            "TestP",
            "--callsign",
            "TEST1",
            "--start",
            "2025-01-01",
            "--end",
            "2025-12-31",
        ],
    )
    assert res.exit_code == 0
    assert "Saved persona: TestP  (TEST1)" in res.output

    # 2) list -> shows TestP
    res = runner.invoke(cli, ["persona", "list"])
    assert res.exit_code == 0
    assert "TestP" in res.output and "providers:" in res.output

    # 3) set credential (use --password to avoid prompt)
    res = runner.invoke(
        cli,
        [
            "persona",
            "set-credential",
            "--persona",
            "TestP",
            "--provider",
            "lotw",
            "--username",
            "test1_lotw",
            "--password",
            "secret123",
        ],
    )
    assert res.exit_code == 0
    assert "Credential ref saved for TestP/lotw" in res.output

    # 4) update persona
    res = runner.invoke(
        cli,
        [
            "persona",
            "add",
            "--name",
            "TestP",
            "--callsign",
            "TEST2",
            "--start",
            "2026-01-01",
            "--end",
            "2026-12-31",
        ],
    )
    assert res.exit_code == 0
    assert "Saved persona: TestP  (TEST2)" in res.output

    # 5) remove
    res = runner.invoke(cli, ["persona", "remove", "TestP"])
    assert res.exit_code == 0
    assert "Removed persona 'TestP'." in res.output

    # 6) list -> empty again
    res = runner.invoke(cli, ["persona", "list"])
    assert res.exit_code == 0
    assert "No personas configured" in res.output
