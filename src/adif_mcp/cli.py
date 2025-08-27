"""CLI entry points for the ADIF MCP core package."""

from __future__ import annotations
import json
import pathlib
import click


@click.group()
def cli() -> None:
    """Top-level command group for adif-mcp utilities."""
    pass


@cli.command()
def version() -> None:
    """Print the installed package version."""
    from adif_mcp import __version__

    click.echo(f"adif-mcp {__version__}")


@cli.command("manifest-validate")
@click.option(
    "--path",
    "path",
    default="mcp/manifest.json",
    show_default=True,
    help="Path to an MCP manifest to validate.",
)
def manifest_validate(path: str) -> None:
    """Validate a manifest’s basic shape (presence/shape of tools array)."""
    p = pathlib.Path(path)
    data = json.loads(p.read_text())
    assert "tools" in data and isinstance(data["tools"], list), "manifest.tools missing"
    click.echo("manifest: OK")
