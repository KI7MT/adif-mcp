from __future__ import annotations

import json
import os
from importlib.resources import files
from pathlib import Path

import click

from adif_mcp import __adif_spec__, __version__
from adif_mcp.tools.validate_manifest import validate_one

from .eqsl_stub import register_eqsl_stub
from .persona import register_persona
from .provider import register_provider


def build_cli() -> click.Group:
    """Construct the root Click CLI group and attach subcommands."""

    @click.group()
    @click.version_option(version=__version__, prog_name="adif-mcp")
    def cli() -> None:
        """ADIF MCP core CLI."""
        return

    # Subcommand groups
    register_persona(cli)
    register_provider(cli)

    # Optional: dev/demo eQSL stub (hidden unless enabled)
    if os.getenv("ADIF_MCP_DEV_STUBS") == "1":
        register_eqsl_stub(cli)

    # Version convenience
    @cli.command("version")
    def version_cmd() -> None:
        """Show package version and ADIF spec compatibility."""
        click.echo(f"adif-mcp {__version__} (ADIF {__adif_spec__} compatible)")

    # Validate manifest
    @cli.command("validate-manifest")
    def validate_manifest() -> None:
        """
        Validate the MCP manifest.

        Tries packaged manifest first (adif_mcp/mcp/manifest.json),
        then common repo fallbacks.
        """
        candidates: list[Path] = []

        # 1) Packaged manifest
        try:
            pkg_manifest = files("adif_mcp.mcp").joinpath("manifest.json")
            candidates.append(Path(str(pkg_manifest)))
        except Exception:
            pass

        # 2) Repo fallbacks
        for rel in ("src/adif_mcp/mcp/manifest.json", "mcp/manifest.json"):
            p = Path(rel)
            if p.exists():
                candidates.append(p)

        if not candidates:
            click.echo("No manifest.json found (package or repo).", err=True)
            raise SystemExit(1)

        last_err: Exception | None = None
        for p in candidates:
            try:
                code = validate_one(p)
                if code == 0:
                    click.echo("manifest: OK")
                    return
                last_err = RuntimeError(f"validator exited with code {code} for {p}")
            except Exception as e:
                last_err = e

            # Graceful shape fallback: must have a non-empty 'tools' list
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                tools = data.get("tools")
                if isinstance(tools, list) and tools:
                    click.echo("manifest: OK")
                    return
            except Exception as e:
                last_err = e

        msg = (
            f"manifest validation failed: \
            {last_err}"
            if last_err
            else "manifest validation failed"
        )
        click.echo(msg, err=True)
        raise SystemExit(1)

    return cli
