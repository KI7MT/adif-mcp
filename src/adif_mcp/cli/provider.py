"""Provider subcommands and metadata access (dynamic discovery)."""

from __future__ import annotations

import argparse
import json
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, List, cast

from adif_mcp.credentials import get_creds
from adif_mcp.identity.store import PersonaStore

# ---------- Provider metadata (resources/providers/*.json) ----------

# importlib.resources.files returns a Traversable; convert to Path for typing
PROVIDERS_DIR: Path = Path(files("adif_mcp.resources") / "providers")  # type: ignore[arg-type]


def _provider_path(slug: str) -> Path:
    """Return path to provider JSON metadata file."""
    return Path(PROVIDERS_DIR) / f"{slug}.json"


def list_supported() -> List[str]:
    """Return provider slugs discovered in resources/providers."""
    p = Path(PROVIDERS_DIR)
    if not p.exists():
        return []
    return sorted(f.stem for f in p.glob("*.json"))


@cache
def get_provider(slug: str) -> Dict[str, Any]:
    """Load and cache provider metadata by slug."""
    path = _provider_path(slug)
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            return cast(Dict[str, Any], data or {})
    except FileNotFoundError:
        return {"name": slug, "slug": slug, "auth": "none"}
    except json.JSONDecodeError:
        return {"name": slug, "slug": slug, "auth": "none"}


def auth_type(slug: str) -> str:
    """Auth type for a provider: 'username_password', 'api_key', or 'none'."""
    meta = get_provider(slug)
    return str(meta.get("auth", "none")).lower()


def _require_supported(provider: str) -> str:
    """Validate provider slug against supported list."""
    p = provider.lower()
    supported = set(list_supported())
    if p not in supported:
        raise SystemExit(
            f"Unknown provider '{provider}'. Supported: {', '.join(sorted(supported))}"
        )
    return p


# ---------- Commands ----------


def cmd_list(args: argparse.Namespace) -> int:
    """Print supported providers and which personas enable them."""
    providers = list_supported()
    print("Supported providers: " + ", ".join(providers or ["(none found)"]))

    store = PersonaStore()
    personas = store.list()
    if not personas:
        print("(no personas discovered)")
        return 0

    print("\nEnabled per persona:")
    for p in personas:
        enabled = [k for k in sorted(p.providers.keys()) if k in providers]
        print(f"  {p.name:15s} -> {', '.join(enabled) or '(none)'}")
    return 0


def cmd_enable(args: argparse.Namespace) -> int:
    """Enable a provider for a persona, warn if creds missing."""
    persona = args.persona
    provider = _require_supported(args.provider)

    store = PersonaStore()
    p = store.get(persona)
    if not p:
        print(f"Persona '{persona}' not found")
        return 1

    if provider in p.providers:
        print(f"{provider} already enabled for {persona}")
    else:
        store.set_provider_ref(persona=persona, provider=provider, username="")
        print(f"Enabled {provider} for {persona}")

    # warn if creds missing for this persona/provider
    c = get_creds(persona, provider)
    a = auth_type(provider)
    need = (
        "username+password"
        if a == "username_password"
        else ("username+api_key" if a == "api_key" else "some secret")
    )
    missing = (
        not c
        or (a == "username_password" and not (c.username and c.password))
        or (a == "api_key" and not (c.username and c.api_key))
    )
    if missing:
        print(
            f"note: no credentials for {persona}:{provider} ({a}). "
            f"Run: adif-mcp creds set {persona} {provider}  # need {need}"
        )
    return 0


def cmd_disable(args: argparse.Namespace) -> int:
    """Disable a provider for a persona."""
    persona = args.persona
    provider = _require_supported(args.provider)

    store = PersonaStore()
    p = store.get(persona)
    if not p:
        print(f"Persona '{persona}' not found")
        return 1

    try:
        removed = store.remove_provider_ref(persona=persona, provider=provider)
    except KeyError:
        print(f"Persona '{persona}' not found")
        return 1

    if not removed:
        print(f"{provider} already disabled for {persona}")
    else:
        print(f"Disabled {provider} for {persona}")
    return 0


# ---------- CLI wiring ----------


def register_cli(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the provider subcommands."""
    p = subparsers.add_parser(
        "provider",
        help="Provider operations",
        description="Enable/disable providers on persona profiles.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sp: argparse._SubParsersAction[argparse.ArgumentParser] = p.add_subparsers(
        dest="provider_cmd", required=True
    )

    s_list = sp.add_parser("list", help="List supported and enabled providers.")
    s_list.set_defaults(func=cmd_list)

    s_en = sp.add_parser("enable", help="Enable a provider for a persona.")
    s_en.add_argument("persona", help="Persona name")
    s_en.add_argument("provider", help="Provider to enable")
    s_en.set_defaults(func=cmd_enable)

    s_dis = sp.add_parser("disable", help="Disable a provider for a persona.")
    s_dis.add_argument("persona", help="Persona name")
    s_dis.add_argument("provider", help="Provider to disable")
    s_dis.set_defaults(func=cmd_disable)
