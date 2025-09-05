# src/adif_mcp/cli/eqsl_stub.py
from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

import click

from adif_mcp.parsers.adif_reader import QSORecord
from adif_mcp.tools.eqsl_stub import fetch_inbox as _eqsl_fetch_inbox
from adif_mcp.tools.eqsl_stub import filter_summary as _eqsl_filter_summary


def register_eqsl_stub(root: click.Group) -> None:
    """Attach the optional 'eqsl' stub group (only in dev)."""

    @root.group("eqsl")
    @click.version_option(prog_name="adif-mcp eqsl (stub)")
    def eqsl() -> None:
        """Commands for the (stub) eQSL integration."""
        return

    @eqsl.command("inbox")
    @click.option(
        "-u",
        "--user",
        "username",
        required=True,
        help="eQSL username for demo data (e.g., KI7MT).",
    )
    @click.option("--pretty/--no-pretty", default=True, show_default=True)
    @click.option("-o", "--out", "out_path", type=click.Path(dir_okay=False, writable=True))
    def eqsl_inbox(username: str, pretty: bool, out_path: Path | None) -> None:
        """Return a deterministic stubbed 'inbox' for the given user."""
        payload: dict[str, list[QSORecord]] = _eqsl_fetch_inbox(username)
        text = json.dumps(payload, indent=2 if pretty else None, sort_keys=pretty)
        if out_path:
            Path(out_path).write_text(text + ("\n" if pretty else ""), encoding="utf-8")
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
    )
    @click.option(
        "-i",
        "--in",
        "in_path",
        type=click.Path(exists=True, dir_okay=False, readable=True),
    )
    @click.option("--pretty/--no-pretty", default=True, show_default=True)
    def eqsl_summary(
        username: str | None,
        by: Literal["band", "mode"],
        in_path: Path | None,
        pretty: bool,
    ) -> None:
        """Summarize QSO records by band or mode (stub data)."""
        records: Iterable[QSORecord]
        if in_path:
            data: dict[str, Any] = json.loads(Path(in_path).read_text(encoding="utf-8"))
            recs = data.get("records", [])
            if not isinstance(recs, list):
                raise click.ClickException("Input JSON must contain a 'records' array.")
            records = recs
        elif username:
            records = _eqsl_fetch_inbox(username)["records"]
        else:
            raise click.ClickException("Provide either --in <file> or --user <callsign>.")

        out = _eqsl_filter_summary(records, by=by)
        click.echo(json.dumps(out, indent=2 if pretty else None, sort_keys=pretty))


def main_inbox_count(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    # TODO: placeholder for future `eqsl count`/fetchers
    print("eQSL inbox count: (stub) unknown")
    return 0


def register_cli(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """_summary_

    Args:
        subparsers (argparse._SubParsersAction[argparse.ArgumentParser]): _description_
    """
    p = subparsers.add_parser(
        "eqsl",
        help="eQSL utilities (stub)",
        description="eQSL utilities (stub)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sp = p.add_subparsers(dest="eqsl_cmd", required=True)

    p_cnt = sp.add_parser("count", help="Show eQSL inbox/outbox counts (stub)")
    p_cnt.set_defaults(func=main_inbox_count)
