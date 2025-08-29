"""
Command-line entry points for adif-mcp.

Commands:
    - version           -> prints package version + ADIF spec version
    - manifest-validate -> quick shape/sanity validation for MCP manifest
"""

from __future__ import annotations

import json
import pathlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional

import click

from adif_mcp import __adif_spec__, __version__
from adif_mcp.parsers.adif_reader import QSORecord
from adif_mcp.tools.eqsl_stub import fetch_inbox as _eqsl_fetch_inbox
from adif_mcp.tools.eqsl_stub import filter_summary as _eqsl_filter_summary


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


@cli.group("eqsl")
def eqsl() -> None:
    """Commands for the (stub) eQSL integration.

    These commands exercise the manifest-defined tools without calling the
    real eQSL service. Useful for wiring, demos, and end-to-end tests.
    """


@eqsl.command("inbox")
@click.option(
    "-u",
    "--user",
    "username",
    required=True,
    help="eQSL username for the demo data (e.g., KI7MT).",
)
@click.option(
    "--pretty/--no-pretty",
    default=True,
    show_default=True,
    help="Pretty-print JSON output.",
)
@click.option(
    "-o",
    "--out",
    "out_path",
    type=click.Path(dir_okay=False, writable=True),
    help="Optional path to write JSON instead of stdout.",
)
def eqsl_inbox(username: str, pretty: bool, out_path: Optional[Path]) -> None:
    """Return a deterministic stubbed 'inbox' for the given user.

    The payload matches the MCP tool output schema:
    {"records": [QsoRecord, ...]}.
    """
    payload: Dict[str, List[QSORecord]] = _eqsl_fetch_inbox(username)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=pretty)
    if out_path:
        out_path.write_text(text + ("\n" if pretty else ""), encoding="utf-8")
        click.echo(f"Wrote {len(payload['records'])} record(s) → {out_path}")
    else:
        click.echo(text)


@eqsl.command("summary")
@click.option(
    "-u",
    "--user",
    "username",
    help="If provided, summarize the stub inbox for this user.",
)
@click.option(
    "--by",
    type=click.Choice(["band", "mode"], case_sensitive=False),
    default="band",
    show_default=True,
    help="Field to summarize.",
)
@click.option(
    "-i",
    "--in",
    "in_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Optional JSON file produced by 'eqsl inbox -o ...' to summarize.",
)
@click.option(
    "--pretty/--no-pretty",
    default=True,
    show_default=True,
    help="Pretty-print JSON output.",
)
def eqsl_summary(
    username: Optional[str],
    by: Literal["band", "mode"],
    in_path: Optional[Path],
    pretty: bool,
) -> None:
    """Summarize QSO records by band or mode.

    Records come from either:
      * a prior JSON file (`--in`), or
      * a fresh stub fetch (`--user`).

    Output schema: {"summary": {"<key>": <count>, ...}}
    """
    records: Iterable[QSORecord]

    if in_path:
        data: Dict[str, Any] = json.loads(in_path.read_text(encoding="utf-8"))
        recs = data.get("records", [])
        if not isinstance(recs, list):
            raise click.ClickException("Input JSON must contain a 'records' array.")
        records = recs
    elif username:
        records = _eqsl_fetch_inbox(username)["records"]
    else:
        raise click.ClickException("Provide either --in <file> or --user <callsign>.")

    out = _eqsl_filter_summary(records, by=by)  # {"summary": {...}}
    click.echo(json.dumps(out, indent=2 if pretty else None, sort_keys=pretty))
