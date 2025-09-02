"""No-network credential presence check for a provider+persona."""

from __future__ import annotations

from typing import Optional

from adif_mcp.identity.errors import (
    PersonaNotFound,
    ProviderRefMissing,
    SecretMissing,
)
from adif_mcp.identity.manager import PersonaManager
from adif_mcp.providers import ProviderKey

EXIT_OK = 0
EXIT_MISSING = 5


def _mask_username(u: Optional[str]) -> str:
    """Lightly mask a username for display."""
    if not u:
        return ""
    return (u[0] + "***" + u[-1]) if len(u) > 2 else u[0] + "*" * (len(u) - 1)


def run(provider: ProviderKey | str, persona: str) -> int:
    """Return 0 if persona+provider creds exist; otherwise EXIT_MISSING."""
    pm = PersonaManager()
    p = str(provider).lower()
    try:
        username, _ = pm.require(persona, p)
    except (
        PersonaNotFound,
        ProviderRefMissing,
        ProviderRefMissing,  # username missing maps to ProviderRefMissing
        SecretMissing,
    ):
        return EXIT_MISSING

    print(f"[OK] {p} persona={persona} username={_mask_username(username)}")
    return EXIT_OK
