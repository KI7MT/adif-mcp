from __future__ import annotations

import json
import pathlib
import click


@click.group()
def cli() -> None:
    """ADIF MCP core CLI."""
    pass


@cli.command()
def version() -> None:
    """Print the package version."""
    from adif_mcp import __version__
    click.echo(f"adif-mcp {__version__}")


@cli.command("manifest-validate")
def manifest_validate() -> None:
    """Validate the MCP manifest structure."""
    p: pathlib.Path = pathlib.Path("mcp/manifest.json")
    data = json.loads(p.read_text())
    assert "tools" in data and isinstance(data["tools"], list), "manifest.tools missing"
    click.echo("manifest: OK")
