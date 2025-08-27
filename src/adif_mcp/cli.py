"""
Command-line entry points for adif-mcp.

Commands:
- version           -> prints package version + ADIF spec version
- manifest-validate -> quick shape/sanity validation for MCP manifest
"""

from __future__ import annotations

import json
import pathlib

import click

from adif_mcp import __adif_spec__, __version__


@click.group()
@click.version_option(version=__version__, prog_name="adif-mcp")
def cli() -> None:
    """ADIF MCP core CLI."""
    # No-op; subcommands below.
    return


@cli.command("version")
def version_cmd() -> None:
    """Show package version and ADIF spec compatibility."""
    click.echo(f"adif-mcp {__version__} (ADIF {__adif_spec__} compatible)")


@cli.command("manifest-validate")
def manifest_validate() -> None:
    """
    Validate the MCP manifest’s basic shape.

    This is a lightweight check that ensures the file exists and has a top-level
    'tools' array. For full schema validation, use the repo’s CI workflow or
    the stricter validation script.
    """
    p = pathlib.Path("mcp/manifest.json")
    if not p.exists():
        raise click.ClickException(f"manifest not found: {p}")

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise click.ClickException(f"invalid JSON in {p}: {e}") from e

    tools = data.get("tools")
    if not isinstance(tools, list):
        raise click.ClickException("manifest.tools missing or not a list")

    click.echo("manifest: OK")
