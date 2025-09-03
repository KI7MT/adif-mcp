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


def test_cli_validate_manifest() -> None:
    """`adif-mcp validate-manifest` prints OK for repo manifest."""
    r = CliRunner().invoke(cli, ["validate-manifest"])
    assert r.exit_code == 0
    assert "manifest validation: OK" in r.output
