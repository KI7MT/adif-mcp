# src/adif_mcp/cli/persona.py
from __future__ import annotations

import getpass
import importlib
from datetime import date
from typing import Any, Optional

import click

from adif_mcp import __adif_spec__, __version__
from adif_mcp.identity import Persona, PersonaStore
from adif_mcp.util.paths import personas_index_path


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


def _parse_date(s: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD or return None."""
    return None if not s else date.fromisoformat(s)


def _format_persona_line(p: Persona) -> str:
    """One-line summary used by list/show/find."""
    span = p.active_span()
    providers = ", ".join(sorted(p.providers)) or "—"
    return f"- {p.name}: {p.callsign}  [{span}]  providers: {providers}"


def register_persona(root: click.Group) -> None:
    """Attach the `persona` command group to the root CLI."""

    @root.group(help="Manage personas & credentials (experimental).")
    @click.version_option(version=__version__, prog_name="adif-mcp persona")
    def persona() -> None:
        """Persona subcommands."""
        return

    @persona.command("version")
    def persona_version() -> None:
        """Show package version and ADIF spec compatibility."""
        click.echo(f"adif-mcp persona {__version__} (ADIF {__adif_spec__} compatible)")

    @persona.command("list", help="List configured personas.")
    @click.option("--verbose", is_flag=True, help="Show provider usernames (masked).")
    def persona_list(verbose: bool) -> None:
        store = PersonaStore(personas_index_path())
        items = store.list()
        if not items:
            click.echo("No personas configured.")
            return
        for p in items:
            click.echo(_format_persona_line(p))
            if verbose and p.providers:
                for prov, ref in sorted(p.providers.items()):
                    user = ref.get("username", "")
                    click.echo(f"    • {prov}: {_mask_username(user)}")

    @persona.command("add", help="Add or update a persona.")
    @click.option("--name", required=True, help="Persona name (e.g., 'primary').")
    @click.option("--callsign", required=True, help="Callsign for this persona.")
    @click.option("--start", help="Start date (YYYY-MM-DD).", default=None)
    @click.option("--end", help="End date (YYYY-MM-DD).", default=None)
    def persona_add(
        name: str, callsign: str, start: Optional[str], end: Optional[str]
    ) -> None:
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
        store = PersonaStore(personas_index_path())
        ok = store.remove(name)
        if ok:
            click.echo(f"Removed persona '{name}'.")
        else:
            click.echo(f"No such persona: {name}", err=True)
            raise SystemExit(1)

    @persona.command("remove-all", help="Delete ALL personas and purge saved secrets.")
    @click.option("--yes", is_flag=True, help="Confirm deletion without prompt.")
    def persona_remove_all(yes: bool) -> None:
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
        store = PersonaStore(personas_index_path())

        def _by_name() -> Optional[Persona]:
            return store.get(ident)

        def _by_callsign() -> Optional[Persona]:
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
        store = PersonaStore(personas_index_path())

        try:
            store.set_provider_ref(
                persona=persona_name,
                provider=provider.lower(),
                username=username,
            )
        except KeyError:
            click.echo(f"No such persona: {persona_name}", err=True)
            raise SystemExit(1)

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
                f"       Secret was NOT stored. You can set it later when keyring works.",
                err=True,
            )
