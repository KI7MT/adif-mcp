#!/usr/bin/env python3
"""
Provider inbox probe (stub) for adif-mcp.

Purpose
-------
Verify that a persona has usable credentials for a given provider using the
centralized PersonaManager (no direct file/keyring access here):
- Persona + provider mapping yields a username.
- Secret/password is available from the OS keyring via PersonaManager.

No network calls by default. This is CI-safe and useful as a quick gate.
You can extend the `--real` branch per provider to call actual APIs later.

Usage
-----
From repo root:

    uv run python scripts/provider_inbox_probe.py --persona MyEQSL --provider eqsl
    uv run python scripts/provider_inbox_probe.py --persona MyLoTW --provider lotw
    uv run python scripts/provider_inbox_probe.py --persona MyQRZ  --provider qrz
    uv run python scripts/provider_inbox_probe.py --persona MyClub --provider clublog

Optional flags:

    --real            # reserved; when implemented, will perform a real provider call
    --verbose         # prints extra information (e.g., masked username, backend)

Exit codes
----------
0  success
2  persona/provider not configured (username resolution failed)
5  secret not found or keyring unavailable
10 --real requested but not implemented

Notes
-----
- Reads the personas index and secrets only via PersonaManager.
- Keyring backend is displayed in --verbose (if importable).
"""

from __future__ import annotations

import argparse
from typing import Final, Optional

from adif_mcp import PersonaManager

# Optional keyring import only for backend name in --verbose (not required to run)
try:
    import keyring as _keyring
except Exception:  # pragma: no cover
    _keyring = None


SUPPORTED: Final[set[str]] = {"eqsl", "lotw", "qrz", "clublog"}


def _mask(u: str) -> str:
    """Return a lightly masked username for display."""
    if not u:
        return "—"
    if len(u) <= 2:
        return "*" * len(u)
    return f"{u[0]}***{u[-1]}"


def _backend_label() -> str:
    """Return a friendly keyring backend label (or 'unavailable')."""
    if _keyring is None:
        return "unavailable"
    try:
        bk = _keyring.get_keyring()
        return f"{bk.__class__.__module__}.{bk.__class__.__name__}"
    except Exception:
        return "available (unknown backend)"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify persona/provider credentials (no network by default)."
    )
    ap.add_argument(
        "--persona",
        required=True,
        help="Persona name (e.g., MyEQSL, MyLoTW)",
    )
    ap.add_argument(
        "--provider",
        required=True,
        choices=sorted(SUPPORTED),
        help="Provider to probe: eqsl | lotw | qrz | clublog",
    )
    ap.add_argument(
        "--real",
        action="store_true",
        help="Reserved: perform a real provider call (not implemented; stub).",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Show additional details (masked username, keyring backend).",
    )
    args = ap.parse_args()

    persona_name: str = args.persona
    provider: str = args.provider.lower()

    pm = PersonaManager()

    # Resolve username via the manager (single source of truth)
    username: Optional[str] = pm.get_provider_username(persona_name, provider)
    if not username:
        # We don’t rely on implementation details to distinguish persona vs provider
        # in this probe; both are “not configured” failures here.
        print(
            f"[error] persona/provider not configured "
            f"(persona='{persona_name}', provider='{provider}')."
        )
        return 2

    # Resolve secret via the manager (keyring abstraction)
    secret: Optional[str] = pm.get_secret(persona_name, provider)
    if not secret:
        print(
            "[error] secret not found in keyring (or keyring unavailable) for "
            f"persona='{persona_name}', provider='{provider}', username='{username}'."
        )
        return 5

    if args.verbose:
        print(f"[info] backend={_backend_label()} user={_mask(username)}")

    if args.real:
        # Future: add a tiny authenticated call per provider
        print(f"[warn] --real not implemented for provider '{provider}'.")
        return 10

    print(f"[OK] creds present for {persona_name}/{provider} (username={username})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
