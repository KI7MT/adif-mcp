"""CLI smoke tests for `adif-mcp`."""

from __future__ import annotations

from click.testing import CliRunner

from adif_mcp.cli import cli


def test_cli_version() -> None:
    """`adif-mcp version` prints package + ADIF spec."""
    r = CliRunner().invoke(cli, ["version"])
    assert r.exit_code == 0
    assert "adif-mcp" in r.output
    assert "ADIF" in r.output


def test_cli_manifest_validate() -> None:
    """`adif-mcp manifest-validate` prints OK for repo manifest."""
    r = CliRunner().invoke(cli, ["manifest-validate"])
    assert r.exit_code == 0
    assert "manifest: OK" in r.output
