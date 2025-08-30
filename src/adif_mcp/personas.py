"""
Persona models and local storage.

A *persona* groups one callsign identity (optionally bounded by dates) and
contains references to provider credentials (stored externally via a keyring).

Storage layout (index JSON):
{
  "personas": {
    "<name>": {
      "name": "...",
      "callsign": "...",
      "start": "YYYY-MM-DD" | null,
      "end":   "YYYY-MM-DD" | null,
      "providers": {
        "lotw": {"username": "..."},
        "eqsl": {"username": "..."}
      }
    }
  }
}

Secrets:
- Password/API tokens are *not* stored here. They are written to the system
  keyring under a deterministic key:
  service = "adif-mcp"
  username = f"{persona}:{provider}:{account_name}"
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, cast

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


# -----------------------------
# Public datamodel
# -----------------------------


class CredentialRef(TypedDict):
    """Non-secret reference to a provider credential."""

    username: str


@dataclass(slots=True)
class Persona:
    """One operator identity (callsign + optional active date range)."""

    name: str
    callsign: str
    start: Optional[date] = None
    end: Optional[date] = None
    providers: Dict[str, CredentialRef] = field(default_factory=dict)  # provider -> ref

    def active_span(self) -> str:
        """Human-friendly date span."""
        s = self.start.isoformat() if self.start else "—"
        e = self.end.isoformat() if self.end else "—"
        return f"{s} → {e}"


# -----------------------------
# Storage (JSON index)
# -----------------------------
class _PersonaJSON(TypedDict, total=False):
    """Defines the properties in the persona ffile

    Args:
        TypedDict (_type_): a dictionary of values representing a persona
        total (bool, optional): default to false if empty not found Defaults to False.
    """

    name: str
    callsign: str
    start: Optional[str]
    end: Optional[str]
    providers: Dict[str, CredentialRef]


def _dumps(obj: Any) -> str:
    """Dumps the JSON object

    Args:
        obj (Any): object containt JSON personanas

    Returns:
        str: retuens the dumpped object
    """
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


class PersonaStore:
    """
    Loads/saves persona index JSON and provides CRUD helpers.

    This class is *intentionally* ignorant of secrets—use keyring helpers at
    the CLI layer to write passwords/tokens.
    """

    def __init__(self, index_path: Path) -> None:
        """Initialized the path location to the persona"""
        self.index_path = index_path
        self._personas: Dict[str, Persona] = {}
        self._load()

    # -------- JSON IO --------

    def _load(self) -> None:
        """Load personas index JSON into the in-memory map."""
        self._personas = {}

        if not self.index_path.exists():
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self.index_path.write_text(_dumps({"personas": {}}), encoding="utf-8")
            return

        data: Dict[str, Any] = json.loads(self.index_path.read_text(encoding="utf-8"))
        raw = cast(Dict[str, _PersonaJSON], data.get("personas", {}))

        for name, rec in raw.items():
            start = _to_date(rec.get("start"))
            end = _to_date(rec.get("end"))
            providers_raw = rec.get("providers")
            providers_map: Dict[str, CredentialRef] = (
                dict(providers_raw) if providers_raw else {}
            )
            self._personas[name] = Persona(
                name=rec.get("name", name),
                callsign=rec["callsign"],
                start=start,
                end=end,
                providers=providers_map,
            )

    def _save(self) -> None:
        """Save the personna"""
        out: Dict[str, _PersonaJSON] = {}
        for name, p in self._personas.items():
            out[name] = {
                "name": p.name,
                "callsign": p.callsign,
                "start": p.start.isoformat() if p.start else None,
                "end": p.end.isoformat() if p.end else None,
                "providers": p.providers,
            }
        self.index_path.write_text(_dumps({"personas": out}), encoding="utf-8")

    # -------- Queries --------

    def list(self) -> List[Persona]:
        """Return all personas, sorted by name."""
        return [self._personas[k] for k in sorted(self._personas)]

    def get(self, name: str) -> Optional[Persona]:
        """Return a persona by name (or None)."""
        return self._personas.get(name)

    # -------- Mutations --------

    # --- inside PersonaStore.upsert(...) ---

    def upsert(
        self,
        *,
        name: str,
        callsign: str,
        start: Optional[date],
        end: Optional[date],
    ) -> Persona:
        """
        Create or update a persona (non-secret fields only).
        Returns the saved Persona.

        Rules:
        - Callsign is stored uppercase.
        - If both dates are provided, end must be >= start.
        """
        if start and end and end < start:
            raise ValueError("end date cannot be earlier than start date")

        callsign_norm = callsign.upper()

        existing = self._personas.get(name)
        if existing:
            existing.callsign = callsign_norm
            existing.start = start
            existing.end = end
            self._save()
            return existing

        p = Persona(
            name=name,
            callsign=callsign_norm,
            start=start,
            end=end,
        )
        self._personas[name] = p
        self._save()
        return p

    def remove(self, name: str) -> bool:
        """Delete a persona; return True if deleted."""
        if name in self._personas:
            del self._personas[name]
            self._save()
            return True
        return False

    def set_provider_ref(
        self,
        *,
        persona: str,
        provider: str,
        username: str,
    ) -> Persona:
        """
        Set/replace a provider reference (non-secret) for a persona.
        """
        p = self._personas.get(persona)
        if not p:
            raise KeyError(f"Persona not found: {persona}")
        p.providers[provider] = {"username": username}
        self._save()
        return p


__all__ = ["Persona", "CredentialRef", "PersonaStore"]
