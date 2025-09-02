"""Data models for personas and provider references.

Note: For v0.3.0 we re-export the legacy, battle-tested models
to keep behavior identical while we migrate code into this
namespace. This preserves mypy stability and avoids duplicate logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional, TypedDict

# -----------------------------
# Persona Helper functions
# -----------------------------


def _to_date(s: Optional[str]) -> Optional[date]:
    """None-safe ISO date parser."""
    return date.fromisoformat(s) if s else None


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


class ProviderRef(TypedDict, total=False):
    """Non-secret reference for a provider on a persona."""

    provider: str
    username: str


class CredentialRef(TypedDict):
    """Non-secret reference to a provider credential."""

    username: str


@dataclass(slots=True)
class Persona:
    """Persona record stored in the JSON index (no secrets)."""

    name: str
    callsign: str
    start: Optional[date] = None
    end: Optional[date] = None
    # Typed map of provider -> ProviderRef; default empty
    providers: Dict[str, ProviderRef] = field(default_factory=dict)

    def active_span(self) -> str:
        """Human-friendly date span."""
        s = self.start.isoformat() if self.start else "—"
        e = self.end.isoformat() if self.end else "—"
        return f"{s} → {e}"
