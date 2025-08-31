# src/adif_mcp/persona_manager.py
"""
Persona Manager

A thin, typed façade over the personas index + keyring secrets.

Responsibilities
----------------
- Resolve the personas index path (via util_paths.personas_index_path()).
- CRUD for personas (delegates to PersonaStore).
- CRUD for provider refs (non-secret usernames).
- Secret I/O in the system keyring (optional dependency; safe if missing).

Keyring
-------
Secrets are stored under:
    service = "adif-mcp"
    key     = f"{persona}:{provider}:{username}"

APIs are intentionally minimal so they can be moved to a separate package later.

Examples
--------
from adif_mcp.persona_manager import PersonaManager

pm = PersonaManager()  # uses default index path
p = pm.get_by_name("MyEQSL")
if p:
    user = pm.get_provider_username("MyEQSL", "eqsl")
    secret = pm.get_secret("MyEQSL", "eqsl")
    print(user, bool(secret))

# Set or update a secret
pm.set_secret("MyEQSL", "eqsl", "ki7mt", "s3cr3t")

# Remove one secret
pm.delete_secret("MyEQSL", "eqsl", "ki7mt")

# Remove all secrets for a persona
count = pm.delete_all_secrets("MyEQSL")
print("removed", count)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional, Tuple, cast

from .personas import CredentialRef, Persona, PersonaStore
from .util_paths import personas_index_path as _util_personas_index_path

# Public constant: keyring "service" name for secrets we store
PERSONA_SERVICE: str = "adif-mcp"


def personas_index_path() -> Path:
    """
    Resolve the personas index path using util_paths (OS-agnostic and pyproject-aware).
    """
    return _util_personas_index_path()


def _keyring_available() -> bool:
    """Return True if keyring is importable and usable."""
    try:
        import keyring  # noqa: F401
    except Exception:
        return False
    return True


def _keyring_set(service: str, key: str, secret: str) -> bool:
    """Set a secret in keyring; returns True on success, False otherwise."""
    if not _keyring_available():
        return False
    try:
        import keyring

        keyring.set_password(service, key, secret)
        return True
    except Exception:
        return False


def _keyring_get(service: str, key: str) -> Optional[str]:
    """Return the secret from keyring or None if unavailable/missing.

    We fetch `keyring.get_password` dynamically and cast the callable’s
    signature so mypy knows it returns `Optional[str]` instead of `Any`.
    """
    if not _keyring_available():
        return None
    try:
        import keyring
    except Exception:
        return None

    get_pw_obj = getattr(keyring, "get_password", None)
    if not callable(get_pw_obj):
        return None

    get_pw = cast(Callable[[str, str], Optional[str]], get_pw_obj)
    return get_pw(service, key)


def _keyring_del(service: str, key: str) -> bool:
    """Delete a secret from keyring; returns True if deleted, False otherwise."""
    if not _keyring_available():
        return False
    try:
        import keyring

        keyring.delete_password(service, key)
        return True
    except Exception:
        return False


@dataclass(frozen=True)
class _ProviderKey:
    """
    Immutable compound identifier for a provider credential binding.

    Attributes:
        persona: Persona name (e.g., "MyLoTW").
        provider: Provider slug ("lotw", "eqsl", "qrz", "clublog").
        username: Account username for the provider.

    Methods:
        keyring_key(): Compose the deterministic key used for keyring lookups:
                       "<persona>:<provider>:<username>"
    """

    persona: str
    provider: str
    username: str

    def keyring_key(self) -> str:
        """Return the key string used with keyring."""
        return f"{self.persona}:{self.provider}:{self.username}"


class PersonaManager:
    """
    High-level persona/credential manager.

    Notes
    -----
    - Non-secret provider refs (usernames) live in the JSON personas index.
    - Secrets live in the OS keyring under PERSONA_SERVICE.
    - All operations are name-based (persona name, not callsign).
    """

    def __init__(self, index_path: Optional[Path] = None) -> None:
        self._index_path: Path = index_path or personas_index_path()
        self._store = PersonaStore(self._index_path)

    # --- Persona CRUD ---

    def list_personas(self) -> list[Persona]:
        """List all personas, sorted by name."""
        return self._store.list()

    def get_persona(self, name: str) -> Optional[Persona]:
        """Get a persona by name."""
        return self._store.get(name)

    def upsert_persona(
        self, *, name: str, callsign: str, start: Optional[date], end: Optional[date]
    ) -> Persona:
        """Create or update a persona."""
        return self._store.upsert(name=name, callsign=callsign, start=start, end=end)

    def remove_persona(self, name: str) -> bool:
        """Remove a persona (index only; does not remove secrets)."""
        return self._store.remove(name)

    # --- Provider refs (non-secret) ---

    def set_provider(self, *, persona: str, provider: str, username: str) -> Persona:
        """
        Set/replace a provider ref (non-secret) for a persona.
        """
        return self._store.set_provider_ref(
            persona=persona, provider=provider.lower(), username=username
        )

    def get_provider_username(self, persona: str, provider: str) -> Optional[str]:
        """
        Return the configured username for (persona, provider) or None.
        """
        p = self._store.get(persona)
        if not p:
            return None
        ref = p.providers.get(provider.lower())
        if not ref:
            return None
        return ref.get("username")

    # --- Secrets (keyring) ---

    def set_secret(
        self, *, persona: str, provider: str, username: str, secret: str
    ) -> bool:
        """Store a secret in keyring (returns True on success)."""
        key = _ProviderKey(persona, provider.lower(), username).keyring_key()
        return _keyring_set(PERSONA_SERVICE, key, secret)

    def get_secret(self, persona: str, provider: str) -> Optional[str]:
        """
        Retrieve a secret for (persona, provider). Uses the username defined in the
        persona's provider ref. Returns None if unavailable or missing.
        """
        uname = self.get_provider_username(persona, provider)
        if not uname:
            return None
        key = _ProviderKey(persona, provider.lower(), uname).keyring_key()
        return _keyring_get(PERSONA_SERVICE, key)

    def delete_secret(self, persona: str, provider: str) -> bool:
        """
        Delete a secret for (persona, provider). Returns True if deleted.
        """
        uname = self.get_provider_username(persona, provider)
        if not uname:
            return False
        key = _ProviderKey(persona, provider.lower(), uname).keyring_key()
        return _keyring_del(PERSONA_SERVICE, key)

    # --- Utilities ---

    def provider_refs(self, persona: str) -> Dict[str, CredentialRef]:
        """
        Return the provider map for a persona (provider -> {username}).
        Empty dict if persona not found.
        """
        p = self._store.get(persona)
        return dict(p.providers) if p else {}

    def remove_all(
        self, *, delete_keyring: bool = False, providers: Optional[Iterable[str]] = None
    ) -> Tuple[int, int]:
        """
        Remove all personas (index). Optionally delete matching keyring entries.

        Args:
            delete_keyring: If True, attempt to delete all secrets for discovered
                (persona, provider, username) tuples.
            providers: If provided, limit keyring deletion to these
                       providers (lowercased).

        Returns:
            (num_personas_removed, num_keyring_deleted)
        """
        # Snapshot before removal
        people = self._store.list()
        pcount = len(people)

        # Compose keys we might delete
        targets: list[_ProviderKey] = []
        if delete_keyring:
            allowed = {p.lower() for p in providers} if providers else None
            for person in people:
                for prov, ref in person.providers.items():
                    if allowed is not None and prov.lower() not in allowed:
                        continue
                    uname = ref.get("username")
                    if uname:
                        targets.append(_ProviderKey(person.name, prov.lower(), uname))

        # Remove index file completely and recreate fresh
        self._index_path.unlink(missing_ok=True)
        self._store = PersonaStore(self._index_path)  # resets empty

        # Delete secrets
        dcount = 0
        for t in targets:
            if _keyring_del(PERSONA_SERVICE, t.keyring_key()):
                dcount += 1

        return pcount, dcount
