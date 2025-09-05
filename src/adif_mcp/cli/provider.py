"""Provider subcommands and metadata access (dynamic discovery)."""

from __future__ import annotations

import argparse
import json
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, List, cast

from adif_mcp.credentials import get_creds

from .persona import resolve_home

# ---------- Provider metadata (resources/providers/*.json) ----------

# importlib.resources.files returns a Traversable; convert to Path for typing
PROVIDERS_DIR: Path = Path(files("adif_mcp.resources") / "providers")  # type: ignore[arg-type]


def _provider_path(slug: str) -> Path:
    """_summary_

    Args:
        slug (str): _description_

    Returns:
        Path: _description_
    """
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


# ---------- YAML IO for persona configs ----------


def _cfg_dir(home: Path) -> Path:
    """_summary_

    Args:
        home (Path): _description_

    Returns:
        Path: _description_
    """
    return home / "config"


def _persona_path(home: Path, name: str) -> Path:
    """_summary_

    Args:
        home (Path): _description_
        name (str): _description_

    Returns:
        Path: _description_
    """
    return _cfg_dir(home) / f"{name}.yaml"


def _load_yaml(path: Path) -> Dict[str, Any]:
    """_summary_

    Args:
        path (Path): _description_

    Raises:
        RuntimeError: _description_

    Returns:
        Dict[str, Any]: _description_
    """
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyYAML required. Install: uv pip install pyyaml") from exc
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
        return cast(Dict[str, Any], data or {})


def _save_yaml(path: Path, data: Dict[str, Any]) -> None:
    """_summary_

    Args:
        path (Path): _description_
        data (Dict[str, Any]): _description_

    Raises:
        RuntimeError: _description_
    """
    try:
        import yaml
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyYAML required. Install: uv pip install pyyaml") from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)


def _require_supported(provider: str) -> str:
    """_summary_

    Args:
        provider (str): _description_

    Raises:
        SystemExit: _description_

    Returns:
        str: _description_
    """
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
    home = resolve_home(args.home)
    cfg = _cfg_dir(home)

    providers = list_supported()
    print("Supported providers: " + ", ".join(providers or ["(none found)"]))

    if not cfg.exists():
        print("(no personas discovered)")
        return 0

    # discover personas
    personas: List[Dict[str, Any]] = []
    for f in sorted(cfg.glob("*.yaml")):
        data = _load_yaml(f)
        if data:
            personas.append(data)

    if not personas:
        print("(no personas discovered)")
        return 0

    print("\nEnabled per persona:")
    for pdata in personas:
        name = str(pdata.get("persona") or "(unnamed)")
        enabled = [str(p).lower() for p in (pdata.get("enabled_providers") or [])]
        enabled = [p for p in enabled if p in providers]
        print(f"  {name:15s} -> {', '.join(enabled) or '(none)'}")
    return 0


def cmd_enable(args: argparse.Namespace) -> int:
    """Enable a provider for a persona, warn if creds missing."""
    home = resolve_home(args.home)
    persona = args.persona
    provider = _require_supported(args.provider)

    path = _persona_path(home, persona)
    data = _load_yaml(path)
    if not data:
        print(f"Persona '{persona}' not found at {path}")
        return 1

    enabled: List[str] = [str(p).lower() for p in (data.get("enabled_providers") or [])]
    if provider in enabled:
        print(f"{provider} already enabled for {persona}")
    else:
        enabled.append(provider)
        data["enabled_providers"] = sorted(enabled)
        _save_yaml(path, data)
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
    home = resolve_home(args.home)
    persona = args.persona
    provider = _require_supported(args.provider)

    path = _persona_path(home, persona)
    data = _load_yaml(path)
    if not data:
        print(f"Persona '{persona}' not found at {path}")
        return 1

    enabled: List[str] = [str(p).lower() for p in (data.get("enabled_providers") or [])]
    if provider not in enabled:
        print(f"{provider} already disabled for {persona}")
        return 0

    enabled = [p for p in enabled if p != provider]
    data["enabled_providers"] = sorted(enabled)
    _save_yaml(path, data)
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
    p.add_argument("--home", help="Override SSOT home directory.")
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
