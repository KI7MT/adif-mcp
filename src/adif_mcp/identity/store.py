# src/adif_mcp/identity/store.py

"""Persistence layer for personas (JSON index via util_paths).

This module is intentionally ignorant of secrets. It only manages the persona
index (non-secret fields) and leaves credential storage to the secrets backend.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, cast

from adif_mcp.util_paths import personas_index_path

from .models import Persona, ProviderRef

# ---------- JSON helpers ----------


class _PersonaJSON(TypedDict, total=False):
    """TODO: Add valid docstring for  store.py _PersonaJSON

    Args:
        TypedDict (_type_): _description_
        total (bool, optional): _description_. Defaults to False.
    """

    name: str
    callsign: str
    start: Optional[str]  # ISO date
    end: Optional[str]  # ISO date
    providers: Dict[str, ProviderRef]


def _to_date(s: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD or return None."""
    if not s:
        return None
    # Let ValueError bubble up if malformed (keeps failures obvious in dev)
    return date.fromisoformat(s)


def _dumps(obj: Any) -> str:
    """Stable JSON for on-disk file (pretty + sorted)."""
    return json.dumps(obj, indent=2, sort_keys=True)


# ---------- Store ----------


class PersonaStore:
    """
    Loads/saves the persona index JSON and provides CRUD helpers.

    Notes:
      - No secret handling here. Only non-secret references (e.g., usernames).
      - Path is determined by util_paths.personas_index_path() in most callers.
    """

    def __init__(self, index_path: Optional[Path] = None) -> None:
        """Initialize the store with a JSON index path."""
        self.index_path = index_path or personas_index_path()
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
            providers_map: Dict[str, ProviderRef] = (
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
        """Persist the current in-memory map to disk."""
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

    def upsert(
        self,
        *,
        name: str,
        callsign: str,
        start: Optional[date],
        end: Optional[date],
    ) -> Persona:
        """
        Create or update a persona (non-secret fields only) and return it.

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
            providers={},  # ensure map exists for new personas
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
        """Set/replace a provider reference (non-secret) for a persona."""
        p = self._personas.get(persona)
        if not p:
            raise KeyError(f"Persona not found: {persona}")
        key = provider.lower()
        # ProviderRef is a TypedDict; store only non-secret username here
        p.providers[key] = {"username": username}
        self._save()
        return p
