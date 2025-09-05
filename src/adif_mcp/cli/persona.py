"""Persona subcommands with callsign date ranges and credentials wiring."""

from __future__ import annotations

import argparse
import os
import platform
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# at top of src/adif_mcp/cli/persona.py
from typing import Any, Dict, List

# YAML io
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

# Keyring-backed creds (reuse existing helpers)
from adif_mcp.credentials import Credentials, set_creds


def resolve_home(cli_home: str | None) -> Path:
    """Resolve the SSOT home directory."""
    if cli_home:
        return Path(cli_home).expanduser().resolve()
    env = os.environ.get("ADIF_MCP_HOME")
    if env:
        return Path(env).expanduser().resolve()
    if platform.system() == "Windows":
        base = Path(os.environ.get("APPDATA", "~")).expanduser()
        return (base / "adif-mcp").resolve()
    if platform.system() == "Darwin":
        return (Path.home() / "Library/Application Support/adif-mcp").resolve()
    return (Path.home() / ".adif-mcp").resolve()


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


def _require_yaml() -> None:
    """_summary_

    Raises:
        RuntimeError: _description_
    """
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML required. Install: uv pip install pyyaml")


def _load_yaml(path: Path) -> Dict[str, Any]:
    """_summary_

    Args:
        path (Path): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    _require_yaml()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _save_yaml(path: Path, data: Dict[str, Any]) -> None:
    """_summary_

    Args:
        path (Path): _description_
        data (Dict[str, Any]): _description_
    """
    _require_yaml()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)


def discover_personas(home: Path) -> List[Dict[str, Any]]:
    """_summary_

    Args:
        home (Path): _description_

    Returns:
        List[Dict[str, Any]]: _description_
    """
    cfg = _cfg_dir(home)
    out: List[Dict[str, Any]] = []
    if not cfg.exists():
        return out
    for f in sorted(cfg.glob("*.yaml")):
        out.append(_load_yaml(f))
    return out


@dataclass(frozen=True)
class DateRange:
    """Inclusive date range (ISO 'YYYY-MM-DD'), end may be None (open-ended)."""

    callsign: str
    start: str
    end: str | None


def _parse_iso(d: str) -> date:
    """_summary_

    Args:
        d (str): _description_

    Returns:
        date: _description_
    """
    y, m, d2 = d.split("-")
    return date(int(y), int(m), int(d2))


def _validate_range(callsign: str, start: str | None, end: str | None) -> DateRange:
    """_summary_

    Args:
        callsign (str): _description_
        start (str | None): _description_
        end (str | None): _description_

    Raises:
        SystemExit: _description_
        SystemExit: _description_
        SystemExit: _description_
        SystemExit: _description_
        SystemExit: _description_

    Returns:
        DateRange: _description_
    """
    cs = (callsign or "").strip().upper()
    if not cs:
        raise SystemExit("callsign is required")
    s = (start or "").strip()
    if not s:
        raise SystemExit("--start YYYY-MM-DD is required")
    try:
        ds = _parse_iso(s)
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"invalid --start '{start}'") from exc
    e_str: str | None = None
    if end:
        end = end.strip()
        try:
            de = _parse_iso(end)
        except Exception as exc:  # pragma: no cover
            raise SystemExit(f"invalid --end '{end}'") from exc
        if de < ds:
            raise SystemExit("end date must be >= start date")
        e_str = end
    return DateRange(callsign=cs, start=s, end=e_str)


def cmd_list(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    home = resolve_home(args.home)
    items = discover_personas(home)
    if not items:
        print("(no personas) — create with: adif-mcp persona add --name NAME …")
        return 0

    verbose = bool(getattr(args, "verbose", False))
    for data in items:
        name = str(data.get("persona") or "(unnamed)")
        providers = ", ".join(data.get("enabled_providers", [])) or "(none)"
        callsign = data.get("callsign") or "(unknown)"
        start = data.get("start")
        end = data.get("end")
        if verbose:
            rng = f"{start or '?'} → {end or '…'}"
            print(f"{name:15s}  {callsign:10s}  {rng:23s}  providers: {providers}")
        else:
            print(f"{name:15s}  providers: {providers}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    home = resolve_home(args.home)
    name = args.name.strip()
    if not name:
        print("persona --name is required")
        return 1

    rng = _validate_range(args.callsign, args.start, args.end)
    providers = [str(p).lower() for p in (args.providers or [])]

    path = _persona_path(home, name)
    if path.exists() and not args.force:
        print(f"Persona {name} already exists at {path}")
        return 1

    data = {
        "persona": name,
        "callsign": rng.callsign,
        "start": rng.start,
        "end": rng.end,
        "enabled_providers": providers,
    }
    _save_yaml(path, data)
    print(f"Created persona {name} at {path}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    home = resolve_home(args.home)
    path = _persona_path(home, args.name)
    if not path.exists():
        print(f"No persona {args.name} at {path}")
        return 1
    path.unlink()
    print(f"Removed persona {args.name}")
    return 0


def cmd_remove_all(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    if not args.yes:
        print("Refusing to remove all personas without --yes")
        return 2
    home = resolve_home(args.home)
    cfg = _cfg_dir(home)
    if not cfg.exists():
        print("(no personas)")
        return 0
    count = 0
    for f in cfg.glob("*.yaml"):
        f.unlink(missing_ok=True)
        count += 1
    print(f"Removed {count} persona(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    home = resolve_home(args.home)
    path = _persona_path(home, args.name)
    data = _load_yaml(path)
    if not data:
        print(f"No persona {args.name} found.")
        return 1
    _require_yaml()
    print(yaml.safe_dump(data, sort_keys=False))
    return 0


def cmd_set_active(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    home = resolve_home(args.home)
    (home / "config").mkdir(parents=True, exist_ok=True)
    marker = home / "config" / "current.txt"
    marker.write_text(args.name, encoding="utf-8")
    print(f"Set active persona to {args.name}")
    return 0


def cmd_set_credential(args: argparse.Namespace) -> int:
    """Set credentials for a persona/provider (keyring-backed)."""
    home = resolve_home(args.home)  # noqa: F841 (kept for symmetry / future use)
    name = args.persona
    provider = args.provider.lower()

    # Normalize blanks to None
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


def cmd_sync_now(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    print(f"(stub) Would sync persona {args.name or '(active)'}")
    return 0


# ---------------- CLI wiring ----------------


def register_cli(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """_summary_

    Args:
        subparsers (argparse._SubParsersAction[argparse.ArgumentParser]): _description_
    """
    p = subparsers.add_parser(
        "persona",
        help="Manage personas",
        description="Manage persona profiles with callsign date ranges.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--home", help="Override SSOT home directory.")
    sp = p.add_subparsers(dest="persona_cmd", required=True)

    # list
    s_list = sp.add_parser("list", help="List personas")
    s_list.add_argument("--verbose", action="store_true", help="Show callsign and date range")
    s_list.set_defaults(func=cmd_list)

    # add
    s_add = sp.add_parser("add", help="Add a new persona")
    s_add.add_argument("--name", required=True, help="Persona name")
    s_add.add_argument("--callsign", required=True, help="Primary callsign")
    s_add.add_argument("--start", required=True, help="Start date YYYY-MM-DD (inclusive)")
    s_add.add_argument("--end", help="End date YYYY-MM-DD (inclusive)")
    s_add.add_argument(
        "--providers",
        nargs="*",
        help="Initial providers to enable (e.g. eqsl lotw qrz clublog)",
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
    s_sc = sp.add_parser("set-credential", help="Set credentials for a persona/provider")
    s_sc.add_argument("--persona", required=True, help="Persona name")
    s_sc.add_argument(
        "--provider",
        required=True,
        choices=["eqsl", "lotw", "qrz", "clublog"],
        help="Provider slug",
    )
    s_sc.add_argument("--username", help="Username/callsign", default=None)
    s_sc.add_argument("--password", help="Password", default=None)
    s_sc.add_argument("--api-key", help="API key/token", default=None)
    s_sc.set_defaults(func=cmd_set_credential)

    # sync-now (stub)
    s_sync = sp.add_parser("sync-now", help="Run sync now (stub)")
    s_sync.add_argument("name", nargs="?", help="Persona name (default active)")
    s_sync.set_defaults(func=cmd_sync_now)
