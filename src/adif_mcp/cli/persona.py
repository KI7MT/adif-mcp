"""Persona subcommands backed by PersonaStore (JSON index)."""

from __future__ import annotations

import argparse
from datetime import date

from adif_mcp.credentials import Credentials, set_creds
from adif_mcp.identity.store import PersonaStore
from adif_mcp.utils.paths import config_dir


def _validate_dates(
    start: str | None, end: str | None,
) -> tuple[date | None, date | None]:
    """Validate and parse start/end ISO date strings."""
    if not start:
        raise SystemExit("--start YYYY-MM-DD is required")
    s = start.strip()
    try:
        ds = date.fromisoformat(s)
    except Exception as exc:
        raise SystemExit(f"invalid --start '{start}'") from exc
    de: date | None = None
    if end:
        e = end.strip()
        try:
            de = date.fromisoformat(e)
        except Exception as exc:
            raise SystemExit(f"invalid --end '{end}'") from exc
        if de < ds:
            raise SystemExit("end date must be >= start date")
    return ds, de


def cmd_list(args: argparse.Namespace) -> int:
    """List all personas from the JSON index."""
    store = PersonaStore()
    personas = store.list()
    if not personas:
        print("(no personas) — create with: adif-mcp persona add --name NAME …")
        return 0

    verbose = bool(getattr(args, "verbose", False))
    for p in personas:
        providers = ", ".join(sorted(p.providers.keys())) or "(none)"
        if verbose:
            print(
                f"{p.name:15s}  {p.callsign:10s}  "
                f"{p.active_span():23s}  providers: {providers}"
            )
        else:
            print(f"{p.name:15s}  providers: {providers}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add a new persona to the JSON index."""
    name = args.name.strip()
    if not name:
        print("persona --name is required")
        return 1

    callsign = (args.callsign or "").strip().upper()
    if not callsign:
        raise SystemExit("callsign is required")

    ds, de = _validate_dates(args.start, args.end)

    store = PersonaStore()
    existing = store.get(name)
    if existing and not args.force:
        print(f"Persona {name} already exists. Use --force to overwrite.")
        return 1

    store.upsert(name=name, callsign=callsign, start=ds, end=de)

    # Wire up providers if given
    providers = [str(p).lower() for p in (args.providers or [])]
    for prov in providers:
        store.set_provider_ref(persona=name, provider=prov, username="")

    print(f"Created persona {name}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a persona from the JSON index."""
    store = PersonaStore()
    if not store.remove(args.name):
        print(f"No persona {args.name}")
        return 1
    print(f"Removed persona {args.name}")
    return 0


def cmd_remove_all(args: argparse.Namespace) -> int:
    """Remove all personas from the JSON index."""
    if not args.yes:
        print("Refusing to remove all personas without --yes")
        return 2
    store = PersonaStore()
    personas = store.list()
    if not personas:
        print("(no personas)")
        return 0
    count = 0
    for p in personas:
        store.remove(p.name)
        count += 1
    print(f"Removed {count} persona(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Show persona details from the JSON index."""
    store = PersonaStore()
    p = store.get(args.name)
    if not p:
        print(f"No persona {args.name} found.")
        return 1
    print(f"name:      {p.name}")
    print(f"callsign:  {p.callsign}")
    print(f"start:     {p.start.isoformat() if p.start else '—'}")
    print(f"end:       {p.end.isoformat() if p.end else '—'}")
    if p.providers:
        print(f"providers: {', '.join(sorted(p.providers.keys()))}")
    else:
        print("providers: (none)")
    return 0


def cmd_set_active(args: argparse.Namespace) -> int:
    """Mark a persona as active via current.txt marker."""
    cfg = config_dir()
    marker = cfg / "current.txt"
    marker.write_text(args.name, encoding="utf-8")
    print(f"Set active persona to {args.name}")
    return 0


def cmd_set_credential(args: argparse.Namespace) -> int:
    """Set credentials for a persona/provider (keyring-backed)."""
    name = args.persona
    provider = args.provider.lower()

    def _norm(s: str | None) -> str | None:
        if s is None:
            return None
        s = s.strip()
        return s if s else None

    creds = Credentials(
        username=_norm(args.username),
        password=_norm(args.password),
        api_key=_norm(args.api_key),
    )
    set_creds(name, provider, creds)
    print(f"Saved credentials for {name}:{provider}.")
    return 0


# ---------------- CLI wiring ----------------


def register_cli(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register persona subcommands."""
    p = subparsers.add_parser(
        "persona",
        help="Manage personas",
        description="Manage persona profiles with callsign date ranges.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sp = p.add_subparsers(dest="persona_cmd", required=True)

    # list
    s_list = sp.add_parser("list", help="List personas")
    s_list.add_argument(
        "--verbose", action="store_true", help="Show callsign and date range"
    )
    s_list.set_defaults(func=cmd_list)

    # add
    s_add = sp.add_parser("add", help="Add a new persona")
    s_add.add_argument("--name", required=True, help="Persona name")
    s_add.add_argument("--callsign", required=True, help="Primary callsign")
    s_add.add_argument(
        "--start", required=True, help="Start date YYYY-MM-DD (inclusive)"
    )
    s_add.add_argument("--end", help="End date YYYY-MM-DD (inclusive)")
    s_add.add_argument(
        "--providers",
        nargs="*",
        help="Initial providers to enable (e.g. eqsl lotw qrz)",
    )
    s_add.add_argument("--force", action="store_true", help="Overwrite if exists")
    s_add.set_defaults(func=cmd_add)

    # remove
    s_rm = sp.add_parser("remove", help="Remove a persona")
    s_rm.add_argument("name", help="Persona name")
    s_rm.set_defaults(func=cmd_remove)

    # remove-all
    s_rmall = sp.add_parser("remove-all", help="Remove ALL personas")
    s_rmall.add_argument("--yes", action="store_true", help="Confirm destructive op")
    s_rmall.set_defaults(func=cmd_remove_all)

    # show
    s_show = sp.add_parser("show", help="Show persona config")
    s_show.add_argument("name", help="Persona name")
    s_show.set_defaults(func=cmd_show)

    # set-active
    s_set = sp.add_parser("set-active", help="Mark persona as active")
    s_set.add_argument("name", help="Persona name")
    s_set.set_defaults(func=cmd_set_active)

    # set-credential (wrapper over keyring-backed creds)
    s_sc = sp.add_parser(
        "set-credential", help="Set credentials for a persona/provider"
    )
    s_sc.add_argument("--persona", required=True, help="Persona name")
    s_sc.add_argument(
        "--provider",
        required=True,
        choices=["eqsl", "lotw", "qrz", "hamqth"],
        help="Provider slug",
    )
    s_sc.add_argument("--username", help="Username/callsign", default=None)
    s_sc.add_argument("--password", help="Password", default=None)
    s_sc.add_argument("--api-key", help="API key/token", default=None)
    s_sc.set_defaults(func=cmd_set_credential)
