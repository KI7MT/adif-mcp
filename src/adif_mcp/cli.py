"""
Command-line entry points for adif-mcp.

Commands:
    - version           -> prints package version + ADIF spec version
    - manifest-validate -> quick shape/sanity validation for MCP manifest
"""

from __future__ import annotations

import getpass
import json
import pathlib
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional

import click

from adif_mcp import __adif_spec__, __version__
from adif_mcp.parsers.adif_reader import QSORecord
from adif_mcp.personas import Persona, PersonaStore
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


# -------- Persona Group --------


def _parse_date(s: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD or return None."""
    return None if not s else date.fromisoformat(s)


def _format_persona_line(p: Persona) -> str:
    """One-line summary used by list/show/find."""
    span = p.active_span()
    providers = ", ".join(sorted(p.providers)) or "—"
    return f"- {p.name}: {p.callsign}  [{span}]  providers: {providers}"


@cli.group(help="Manage personas & credentials (experimental).")
def persona() -> None:
    """Clickgroup for persona not fully implemented yet."""
    pass


@persona.command("list", help="List configured personas.")
def persona_list() -> None:
    """List configured personas with optional active date span and providers."""
    store = PersonaStore(_personas_index_path())
    items = store.list()
    if not items:
        click.echo("No personas configured.")
        return
    for p in items:
        span = p.active_span()  # e.g., "2024-01-01–…" or "…–2024-12-31" or "—"
        providers = ", ".join(sorted(p.providers)) or "—"
        click.echo(f"- {p.name}: {p.callsign}  [{span}]  providers: {providers}")


def _personas_index_path() -> Path:
    """Resolve personas index path from pyproject (if present) or default."""
    default = Path.home() / ".config" / "adif-mcp" / "personas.json"
    try:
        from . import _find_pyproject  # local helper in __init__.py

        pj: Optional[Path] = _find_pyproject(Path.cwd())
        if pj:
            import tomllib

            data = tomllib.loads(pj.read_text(encoding="utf-8"))
            tool = data.get("tool", {})
            adif = tool.get("adif", {})
            custom = adif.get("personas_index")
            if isinstance(custom, str) and custom.strip():
                return (pj.parent / custom).resolve()
    except Exception:
        # Any parsing/import errors → fall back to default
        pass
    return default


@persona.command("add", help="Add or update a persona.")
@click.option(
    "--name", required=True, help="Persona name (e.g., 'primary', 'w7a-2025')."
)
@click.option("--callsign", required=True, help="Callsign for this persona.")
@click.option("--start", help="Start date (YYYY-MM-DD).", default=None)
@click.option("--end", help="End date (YYYY-MM-DD).", default=None)
def persona_add(
    name: str,
    callsign: str,
    start: Optional[str],
    end: Optional[str],
) -> None:
    """Add a new Persona."""
    """Add a new Persona

    Args:
        name (str): name of the persona
        callsign (str): callsign the persona is associated with
        start (Optional[str]): start date of the persona
        end (Optional[str]): end date of the persona
    """
    store = PersonaStore(_personas_index_path())
    p = store.upsert(
        name=name,
        callsign=callsign.upper(),
        start=_parse_date(start),
        end=_parse_date(end),
    )
    click.echo(f"Saved persona: {p.name}  ({p.callsign})  span={p.active_span()}")


@persona.command("remove", help="Remove a persona.")
@click.argument("name")
def persona_remove(name: str) -> None:
    """Remove a persona.

    Args:
        name (str): Persona name to remove

    Raises:
        SystemExit: If no such persona exists.
    """
    store = PersonaStore(_personas_index_path())
    ok = store.remove(name)
    if ok:
        click.echo(f"Removed persona '{name}'.")
    else:
        click.echo(f"No such persona: {name}", err=True)
        raise SystemExit(1)


@persona.command("remove-all", help="Remove all personas.")
@click.confirmation_option(prompt="Are you sure you want to delete ALL personas?")
def persona_remove_all() -> None:
    """Delete all personas from the index."""
    store = PersonaStore(_personas_index_path())
    items = store.list()
    if not items:
        click.echo("No personas to remove.")
        return
    for p in list(items):
        store.remove(p.name)
    click.echo(f"Removed {len(items)} persona(s).")


@persona.command("show", help="Show details for one persona.")
@click.argument("ident", required=False)
@click.option(
    "--name",
    "name_opt",
    help="Show by exact persona NAME (bypasses callsign matching).",
)
@click.option(
    "--by",
    type=click.Choice(["auto", "callsign", "name"], case_sensitive=False),
    default="auto",
    show_default=True,
    help="Lookup mode: auto tries callsign first, then name.",
)
def persona_show(ident: str | None, name_opt: str | None, by: str) -> None:
    """
    Show a persona by callsign (default) or by name.

    Examples:
        adif-mcp persona show KI7MT             # callsign first
        adif-mcp persona show --by name Primary # force name lookup
        adif-mcp persona show --name Primary    # direct by name
    """
    store = PersonaStore(_personas_index_path())

    # Direct by-name short-circuit
    if name_opt:
        p = store.get(name_opt)
        if not p:
            click.echo(f"No such persona (name): {name_opt}", err=True)
            raise SystemExit(1)
        click.echo(_format_persona_line(p))
        return

    if not ident:
        # No ident and no --name; show help-ish guidance.
        click.echo(
            "Usage: adif-mcp persona show [IDENT] "
            "or --name <persona-name>. Try 'persona list' or 'persona find'.",
            err=True,
        )
        raise SystemExit(2)

    ident_l = ident.lower()

    def _by_callsign() -> list[Persona]:
        """Enaby by callsign searching"""
        return [p for p in store.list() if p.callsign.lower() == ident_l]

    def _by_name_exact() -> Persona | None:
        """Enable exact name matching"""
        return store.get(ident)  # exact name match only

    if by.lower() == "name":
        p = _by_name_exact()
        if not p:
            click.echo(f"No such persona (name): {ident}", err=True)
            raise SystemExit(1)
        click.echo(_format_persona_line(p))
        return

    # callsign first (auto/callsign)
    cs_hits = _by_callsign()
    if len(cs_hits) == 1:
        click.echo(_format_persona_line(cs_hits[0]))
        return
    if len(cs_hits) > 1:
        click.echo(f"Multiple personas use callsign {ident}:")
        for p in cs_hits:
            click.echo(_format_persona_line(p))
        click.echo(
            "Re-run with '--name <persona>' to select the one you want.",
            err=True,
        )
        raise SystemExit(1)

    if by.lower() == "auto":
        # Fall back to exact name match if callsign didn’t hit
        p = _by_name_exact()
        if p:
            click.echo(_format_persona_line(p))
            return

    click.echo(f"No persona found for '{ident}'.", err=True)
    raise SystemExit(1)


@persona.command(
    "set-credential",
    help="Attach provider credential (non-secret ref + secret in keyring).",
)
@click.option("--persona", "persona_name", required=True, help="Persona name.")
@click.option(
    "--provider",
    required=True,
    type=click.Choice(["lotw", "eqsl", "qrz", "clublog"], case_sensitive=False),
)
@click.option("--username", required=True, help="Account username for the provider.")
@click.option(
    "--password",
    help="Password/secret. If omitted, will prompt securely.",
    default=None,
)
def persona_set_credential(
    persona_name: str, provider: str, username: str, password: Optional[str]
) -> None:
    """Attach provider credential (non-secret ref + secret in keyring

    Args:
        persona_name (str): name of the persona
        provider (str): name of the provider ( LoTW, eQSL, etc )
        username (str): username associated with the provider account
        password (Optional[str]): password associated with the provider account

    Raises:
        SystemExit: No such persona
    """
    store = PersonaStore(_personas_index_path())

    # Save non-secret ref
    try:
        store.set_provider_ref(
            persona=persona_name,
            provider=provider.lower(),
            username=username,
        )
    except KeyError:
        click.echo(f"No such persona: {persona_name}", err=True)
        raise SystemExit(1)

    # Secret handling via keyring (optional)
    secret = password or getpass.getpass(f"{provider} password for {username}: ")

    saved = False
    try:
        import keyring  # optional dep

        keyring.set_password(
            "adif-mcp",
            f"{persona_name}:{provider}:{username}",
            secret,
        )
        saved = True
    except Exception as e:  # nosec - surfaced as UX note
        click.echo(
            f"[warn] keyring unavailable or failed: {e}\n"
            f"       Secret was NOT stored. You can set it "
            f"later when keyring works.",
            err=True,
        )

    click.echo(
        f"Credential ref saved for {persona_name}/{provider} "
        f"(username={username})."
        f"{' Secret stored in keyring.' if saved else ''}"
    )


@persona.command("find", help="List personas matching name or callsign.")
@click.argument("query")
def persona_find(query: str) -> None:
    """Case-insensitive substring search over persona *name* and *callsign*."""
    store = PersonaStore(_personas_index_path())
    q = query.lower()
    hits = [p for p in store.list() if q in p.name.lower() or q in p.callsign.lower()]
    if not hits:
        click.echo(f"No personas match '{query}'.")
        raise SystemExit(1)
    for p in hits:
        click.echo(_format_persona_line(p))
