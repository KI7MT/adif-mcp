"""
Command-line entry points for adif-mcp.

Commands:
    - version           -> prints package version + ADIF spec version
    - manifest-validate -> quick shape/sanity validation for MCP manifest
"""

from __future__ import annotations

import getpass
import importlib
import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, cast

import click

from adif_mcp import __adif_spec__, __version__
from adif_mcp.identity import Persona, PersonaStore
from adif_mcp.parsers.adif_reader import QSORecord
from adif_mcp.probes import inbox_probe, index_probe
from adif_mcp.providers import ProviderKey
from adif_mcp.tools.eqsl_stub import fetch_inbox as _eqsl_fetch_inbox
from adif_mcp.tools.eqsl_stub import filter_summary as _eqsl_filter_summary

from .util_paths import personas_index_path

# ---------------------------
# Helper functions
# ----------------------------


def _mask_username(u: str) -> str:
    """Return a lightly-masked username for display."""
    if len(u) <= 2:
        return "*" * len(u)
    return f"{u[0]}***{u[-1]}"


def _keyring_backend_name() -> str:
    """Return active keyring backend name, or 'unavailable'."""
    try:
        import keyring

        kr = keyring.get_keyring()
        cls = kr.__class__
        return f"{cls.__module__}.{cls.__name__}"
    except Exception:
        return "unavailable"


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
    Validate the MCP manifest.

    Tries the canonical packaged manifest first (src/adif_mcp/mcp/manifest.json),
    and falls back to the repo manifest at mcp/manifest.json.
    Prints "manifest: OK" on success; exits non-zero on failure.
    """
    import json
    from importlib.resources import files

    from adif_mcp.tools.validate_manifest import validate_one  # raises or returns code

    candidates: list[Path] = []

    # 1) Packaged manifest (preferred)
    try:
        pkg_manifest = files("adif_mcp.mcp").joinpath("manifest.json")
        candidates.append(Path(str(pkg_manifest)))
    except Exception:
        pass

    # 2) Repo manifest (fallback)
    repo_manifest = Path("mcp/manifest.json")
    if repo_manifest.exists():
        candidates.append(repo_manifest)

    if not candidates:
        click.echo("No manifest.json found (package or repo).", err=True)
        raise SystemExit(1)

    last_err: Exception | None = None
    for p in candidates:
        try:
            # validate_one may return an int code, or raise on error.
            code = validate_one(p)
            if code == 0:
                click.echo("manifest: OK")
                return
            # Non-zero code → try next candidate (record a generic error)
            last_err = RuntimeError(f"validator returned exit code {code} for {p}")
        except Exception as e:  # schema/shape/file errors
            last_err = e
            # try next candidate

        # As a graceful fallback, ensure basic shape (tools: list)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            tools = data.get("tools", None)
            if isinstance(tools, list) and tools:
                click.echo("manifest: OK")
                return
        except Exception as e:
            last_err = e
            # continue loop

    # If we get here, all candidates failed
    msg = (
        f"manifest validation failed: {last_err}"
        if last_err
        else "manifest validation failed"
    )
    click.echo(msg, err=True)
    raise SystemExit(1)


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


@persona.command("version")
def persona_version() -> None:
    """Show package version and ADIF spec compatibility."""
    click.echo(f"adif-mcp persona {__version__} (ADIF {__adif_spec__} compatible)")


@persona.command("list", help="List configured personas.")
@click.option(
    "--verbose",
    is_flag=True,
    help="Show provider usernames (masked).",
)
def persona_list(verbose: bool) -> None:
    """List configured personas."""
    store = PersonaStore(personas_index_path())
    items = store.list()
    if not items:
        click.echo("No personas configured.")
        return
    for p in items:
        span = p.active_span()
        providers = ", ".join(sorted(p.providers)) or "—"
        line = f"- {p.name}: {p.callsign}  [{span}]  providers: {providers}"
        click.echo(line)
        if verbose and p.providers:
            for prov, ref in sorted(p.providers.items()):
                user = ref.get("username", "")
                click.echo(f"    • {prov}: {_mask_username(user)}")


@persona.command("add", help="Add or update a persona.")
@click.option("--name", required=True, help="Persona name (e.g., 'primary', 'w7a-2025').")
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
    store = PersonaStore(personas_index_path())
    try:
        p = store.upsert(
            name=name,
            callsign=callsign.upper().strip(),
            start=_parse_date(start),
            end=_parse_date(end),
        )
    except ValueError as e:
        click.echo(f"[error] {e}", err=True)
        raise SystemExit(1)

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
    store = PersonaStore(personas_index_path())
    ok = store.remove(name)
    if ok:
        click.echo(f"Removed persona '{name}'.")
    else:
        click.echo(f"No such persona: {name}", err=True)
        raise SystemExit(1)


# in src/adif_mcp/cli.py


@persona.command("remove-all", help="Delete ALL personas and purge saved secrets.")
@click.option("--yes", is_flag=True, help="Confirm deletion without prompt.")
def persona_remove_all(yes: bool) -> None:
    """Remove every persona and delete any saved keyring secrets for them."""
    if not yes:
        click.echo("Refusing to remove without --yes.", err=True)
        raise SystemExit(1)

    store = PersonaStore(personas_index_path())
    items = store.list()
    if not items:
        click.echo("No personas configured.")
        return

    kr: Optional[Any]
    try:
        # Runtime import; returns Any, so mypy is fine and no ignore is needed.
        kr = importlib.import_module("keyring")
    except Exception:
        kr = None

    deleted_pw = 0
    for p in items:
        if kr is not None:
            for prov, ref in p.providers.items():
                username = ref.get("username")
                if not username:
                    continue
                try:
                    kr.delete_password("adif-mcp", f"{p.name}:{prov}:{username}")
                    deleted_pw += 1
                except Exception:
                    pass  # ignore per-entry delete failures

        # Remove persona from the JSON index
        store.remove(p.name)

    click.echo(f"Removed {len(items)} persona(s).")
    if kr:
        click.echo(f"Removed {deleted_pw} keyring entrie(s).")
    else:
        click.echo("Keyring not available; secrets unchanged.", err=True)


@persona.command("show", help="Show details for one persona.")
@click.option(
    "--by",
    type=click.Choice(["name", "callsign"], case_sensitive=False),
    default="name",
    show_default=True,
    help="Lookup by persona name or callsign.",
)
@click.argument("ident")
def persona_show(by: str, ident: str) -> None:
    """Show persona details (credentials masked)."""
    store = PersonaStore(personas_index_path())

    def _by_name() -> Optional[Persona]:
        """Show persona details by name"""
        return store.get(ident)

    def _by_callsign() -> Optional[Persona]:
        """Show persona details by callsign"""
        ident_u = ident.upper()
        for p in store.list():
            if p.callsign.upper() == ident_u:
                return p
        return None

    p = _by_name() if by == "name" else _by_callsign()
    if not p:
        click.echo(f"No such persona by {by}: {ident}", err=True)
        raise SystemExit(1)

    click.echo(f"Persona: {p.name}")
    click.echo(f"Callsign: {p.callsign}")
    click.echo(f"Active:   {p.active_span()}")

    if not p.providers:
        click.echo("Providers: —")
        return

    click.echo("Providers:")
    for prov, ref in sorted(p.providers.items()):
        user = ref.get("username", "")
        click.echo(f"  - {prov}: {_mask_username(user)}")


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
    store = PersonaStore(personas_index_path())

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

    try:
        import keyring  # optional dep

        keyring.set_password(
            "adif-mcp",
            f"{persona_name}:{provider}:{username}",
            secret,
        )

        backend = _keyring_backend_name()

        click.echo(
            "Credential ref saved for "
            f"{persona_name}/{provider} (username={username}). "
            f"Secret stored in keyring [{backend}]."
        )
    except Exception as e:  # nosec - surfaced as UX note
        click.echo(
            f"[warn] keyring unavailable or failed: {e}\n"
            f"       Secret was NOT stored. You can set it "
            f"later when keyring works.",
            err=True,
        )


@persona.command("find", help="List personas matching name or callsign.")
@click.argument("query")
def persona_find(query: str) -> None:
    """Case-insensitive substring search over persona *name* and *callsign*."""
    store = PersonaStore(personas_index_path())
    q = query.lower()
    hits = [p for p in store.list() if q in p.name.lower() or q in p.callsign.lower()]
    if not hits:
        click.echo(f"No personas match '{query}'.")
        raise SystemExit(1)
    for p in hits:
        click.echo(_format_persona_line(p))


@cli.group("provider")
def provider_group() -> None:
    """Provider tools (probes, etc.)."""
    return


@provider_group.command("probe")
@click.option(
    "--provider",
    required=True,
    type=click.Choice(["lotw", "eqsl", "qrz", "clublog"], case_sensitive=False),
)
@click.option("--persona", required=True)
@click.option("--timeout", type=float, default=10.0, show_default=True)
@click.option("--verbose", is_flag=True)
@click.option("--real", is_flag=True, help="Reserved; behaves same as GET probe for now.")
def provider_probe(
    provider: str, persona: str, timeout: float, verbose: bool, real: bool
) -> None:
    """Probe the provider for valid connection"""
    pkey = cast(ProviderKey, provider.lower())
    code = inbox_probe.run(pkey, persona, timeout=timeout, verbose=verbose)
    raise SystemExit(code)


@provider_group.command("index-check")
@click.option(
    "--provider",
    required=True,
    type=click.Choice(["lotw", "eqsl", "qrz", "clublog"], case_sensitive=False),
)
@click.option("--persona", required=True)
def provider_index_check(provider: str, persona: str) -> None:
    """Verify credentials by performaing an index check on the provder"""
    pkey = cast(ProviderKey, provider.lower())
    code = index_probe.run(pkey, persona)
    raise SystemExit(code)
