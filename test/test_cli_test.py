"""CLI smoke tests for `adif-mcp`."""

from __future__ import annotations

from click.testing import CliRunner

from adif_mcp.cli.root import build_cli

CLI = build_cli()


def test_cli_validate_manifest() -> None:
    """`adif-mcp validate-manifest` prints OK for packaged/repo manifest."""
    r = CliRunner().invoke(CLI, ["validate-manifest"])
    assert r.exit_code == 0
    assert "manifest: OK" in (r.output or "")


def test_cli_version() -> None:
    """`adif-mcp version` prints package + ADIF spec."""
    r = CliRunner().invoke(CLI, ["version"])
    assert r.exit_code == 0
    assert "adif-mcp" in r.output
    assert "ADIF" in r.output
