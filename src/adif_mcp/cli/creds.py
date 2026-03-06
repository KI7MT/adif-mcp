"""Credentials subcommands (OS keyring)."""

from __future__ import annotations

import argparse
import getpass
import json
from typing import Optional

from adif_mcp.cli.provider import auth_type, list_supported
from adif_mcp.credentials import (
    SERVICE,
    Credentials,
    delete_creds,
    get_creds,
    set_creds,
)
from adif_mcp.identity.store import PersonaStore

# ---------- Import Keyring ---------

try:
    import keyring
except Exception:
    keyring = None  # type: ignore[assignment]


# --------- Primary Functions ----------


def _redacted(c: Credentials) -> dict[str, str]:
    """Return credential fields with secrets masked."""

    def mask(v: str) -> str:
        return (v[:2] + "…") if len(v) > 4 else "•••"

    out: dict[str, str] = {}
    if c.username:
        out["username"] = c.username
    if c.password:
        out["password"] = mask(c.password)
    if c.api_key:
        out["api_key"] = mask(c.api_key)
    return out


def cmd_set(args: argparse.Namespace) -> int:
    """Set credentials for a persona/provider in the OS keyring."""
    if keyring is None:
        print("Install keyring: uv pip install keyring")
        return 2

    prov = args.provider.lower()
    a = auth_type(prov)

    username: str | None = args.username
    password: str | None = args.password
    api_key: str | None = args.api_key

    def _norm(s: str | None) -> str | None:
        if s is None:
            return None
        s = s.strip()
        return s if s else None

    if a == "username_password":
        username = _norm(username) or input(f"{prov} username/callsign: ").strip() or None
        if password is None:
            pw = getpass.getpass(f"{prov} password: ").strip()
            password = pw or None
        api_key = None
    elif a == "api_key":
        username = _norm(username) or input(f"{prov} username/callsign: ").strip() or None
        api_key = _norm(api_key) or input(f"{prov} API key: ").strip() or None
        password = None
    else:
        # fallback generic
        username = _norm(username) or input("Username (blank to skip): ").strip() or None
        api_key = _norm(api_key) or input("API key (blank to skip): ").strip() or None
        if password is None:
            pw = getpass.getpass("Password (hidden, blank to skip): ").strip()
            password = pw or None

    creds = Credentials(
        username=_norm(username), password=_norm(password), api_key=_norm(api_key)
    )
    set_creds(args.persona, prov, creds)
    print(f"Saved credentials for {args.persona}:{prov} in {SERVICE}.")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    """Show redacted credentials from the OS keyring."""
    if keyring is None:
        print("Install keyring: uv pip install keyring")
        return 2
    c = get_creds(args.persona, args.provider)
    if not c:
        print("No credentials stored.")
        return 1
    if getattr(args, "raw", False):
        # raw JSON of what's in the keyring (no masking)
        print(c.to_json())
    else:
        # redacted, omitting null/empty fields
        print(json.dumps(_redacted(c), indent=2))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """Delete stored credentials from the OS keyring."""
    if keyring is None:
        print("Install keyring: uv pip install keyring")
        return 2
    ok = delete_creds(args.persona, args.provider)
    print("Deleted." if ok else "Nothing to delete.")
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    """Delete ALL personas and ALL credentials — factory reset."""
    if not args.yes:
        print("Refusing to reset without --yes (this deletes ALL personas and credentials)")
        return 2
    if keyring is None:
        print("Install keyring: uv pip install keyring")
        return 2

    store = PersonaStore()
    personas = store.list()
    cred_count = 0

    # Delete all keyring entries for every persona/provider
    for p in personas:
        for prov in list(p.providers.keys()):
            if delete_creds(p.name, prov):
                cred_count += 1

    # Remove all personas
    persona_count = 0
    for p in personas:
        store.remove(p.name)
        persona_count += 1

    print(f"Reset complete: {persona_count} persona(s), {cred_count} credential(s) deleted.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """Explain where keyring entries live."""
    if keyring is None:
        print("Install keyring: uv pip install keyring")
        return 2
    print(
        "Keyring entries are stored under service "
        f"'{SERVICE}' with username 'persona:provider'.\n"
        "Use your OS keychain UI to enumerate entries."
    )
    return 0


def _has_required_fields(c: Optional[Credentials], a: str) -> bool:
    """Check if credentials have the required fields for auth type."""
    a = a.lower()
    if a == "username_password":
        return bool(c and c.username and c.password)
    if a == "api_key":
        return bool(c and c.username and c.api_key)
    # none / unknown: any presence counts
    return bool(c and (c.username or c.password or c.api_key))


def cmd_doctor(args: argparse.Namespace) -> int:
    """Check credential health across personas and providers."""
    store = PersonaStore()
    personas = store.list()
    if not personas:
        print("(no personas) — create one with: adif-mcp persona add --name NAME …")
        return 0

    target = (args.persona or "").lower() if hasattr(args, "persona") else ""
    ok = missing = 0

    for p in personas:
        if not p.name or (target and p.name.lower() != target):
            continue

        for prov in list_supported():
            if prov not in p.providers:
                continue
            a = auth_type(prov)
            c = get_creds(p.name, prov)
            if _has_required_fields(c, a):
                print(f"✓ {p.name}:{prov} — stored ({a})")
                ok += 1
            else:
                need = (
                    "username+password"
                    if a == "username_password"
                    else (
                        "username+api_key" if a == "api_key" else "some secret"
                    )
                )
                print(
                    f"✗ {p.name}:{prov} — missing {need} "
                    f"(run: adif-mcp creds set {p.name} {prov})"
                )
                missing += 1

    print(f"\nSummary: stored={ok}, missing={missing}")
    return 0


# ---------- register_cli(...) ---------


def register_cli(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register credentials subcommands."""
    p = subparsers.add_parser(
        "creds",
        help="Manage credentials in the OS keyring.",
        description="Set/get/delete credentials per persona/provider.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    sp: argparse._SubParsersAction[argparse.ArgumentParser] = p.add_subparsers(
        dest="creds_cmd", required=True
    )

    # --- set ---
    s = sp.add_parser("set", help="Save credentials.")
    s.add_argument("persona", help="Persona name")
    s.add_argument("provider", help="Provider (eqsl, lotw, qrz)")
    s.add_argument("--username", default=None, help="Username/login")
    s.add_argument("--password", default=None, help="Password (unsafe on CLI)")
    s.add_argument("--api-key", default=None, help="API key/token")
    s.set_defaults(func=cmd_set)

    # --- get ---
    g = sp.add_parser("get", help="Show redacted credentials.")
    g.add_argument("persona", help="Persona name")
    g.add_argument("provider", help="Provider")
    g.add_argument("--raw", action="store_true", help="Print raw JSON (Use with Caution)")
    g.set_defaults(func=cmd_get)

    # --- delete ---
    d = sp.add_parser("delete", help="Delete stored credentials.")
    d.add_argument("persona", help="Persona name")
    d.add_argument("provider", help="Provider")
    d.set_defaults(func=cmd_delete)

    # --- list ---
    list_parser = sp.add_parser("list", help="Explain where entries live.")
    list_parser.set_defaults(func=cmd_list)

    # --- reset ---
    r = sp.add_parser("reset", help="Delete ALL personas and credentials (factory reset).")
    r.add_argument("--yes", action="store_true", help="Confirm destructive op")
    r.set_defaults(func=cmd_reset)

    # --- doctor ---
    doc = sp.add_parser("doctor", help="Check creds across personas/providers.")
    doc.add_argument("--persona", default=None, help="Only check this persona")
    doc.add_argument("--debug", action="store_true", help="Print lookup subjects")
    doc.set_defaults(func=cmd_doctor)
