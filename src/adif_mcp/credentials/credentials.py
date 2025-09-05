"""OS keyring helpers for persona/provider credentials."""

from __future__ import annotations

import json
from dataclasses import dataclass

try:
    import keyring
except Exception:  # pragma: no cover
    keyring = None  # type: ignore[assignment]

SERVICE = "adif-mcp"  # how it appears in the OS keyring


@dataclass(frozen=True)
class Credentials:
    """Structured credentials payload stored in keyring."""

    username: str | None = None
    password: str | None = None
    api_key: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Serialize to a dict, skipping empty fields."""
        out: dict[str, str] = {}
        if self.username:
            out["username"] = self.username
        if self.password:
            out["password"] = self.password
        if self.api_key:
            out["api_key"] = self.api_key
        return out

    def to_json(self) -> str:
        """Serialize to JSON, skipping empty fields."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str) -> Credentials:
        """Parse JSON produced by to_json()."""
        data = json.loads(s or "{}")
        return cls(
            username=data.get("username"),
            password=data.get("password"),
            api_key=data.get("api_key"),
        )


def _subject(persona: str, provider: str) -> str:
    """Keyring username field used under SERVICE."""
    return f"{persona}:{provider}".lower()


def ensure_keyring() -> None:
    """Raise a friendly error if keyring backend is unavailable."""
    if keyring is None:  # pragma: no cover
        raise RuntimeError(
            "Python package 'keyring' not installed or unavailable.\n"
            "Install with: uv pip install keyring\n"
            "Linux servers may need a Secret Service backend or keyrings.alt."
        )


def set_creds(persona: str, provider: str, creds: Credentials) -> None:
    """Save credentials to the OS keyring."""
    ensure_keyring()
    keyring.set_password(SERVICE, _subject(persona, provider), creds.to_json())


def get_creds(persona: str, provider: str) -> Credentials | None:
    """Load credentials from the OS keyring."""
    ensure_keyring()
    raw = keyring.get_password(SERVICE, _subject(persona, provider))
    return Credentials.from_json(raw) if raw else None


def delete_creds(persona: str, provider: str) -> bool:
    """Delete a stored credential; returns True if removed.

    Tries lowercased subject (current format) then legacy exact-case.
    """
    ensure_keyring()
    subjects = [
        _subject(persona, provider),  # lowercased (current)
        f"{persona}:{provider}",  # legacy (exact case)
    ]
    any_deleted = False
    for subj in subjects:
        try:
            keyring.delete_password(SERVICE, subj)
            any_deleted = True
        except Exception:
            pass
    return any_deleted
