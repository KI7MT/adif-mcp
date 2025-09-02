"""PersonaManager façade for identity operations."""

from __future__ import annotations

from typing import Optional, Tuple

from .errors import PersonaNotFound, ProviderRefMissing, SecretMissing
from .models import Persona, ProviderRef
from .secrets import KeyringSecretStore, SecretStore
from .store import PersonaStore

_SERVICE = "adif-mcp"  # keyring service name


class PersonaManager:
    """High-level API for personas  secrets (no network I/O)."""

    def __init__(
        self,
        store: Optional[PersonaStore] = None,
        secrets: Optional[SecretStore] = None,
    ) -> None:
        """Create a new manager with a persona store and secret backend."""
        self.store: PersonaStore = store or PersonaStore()
        self.secrets: SecretStore = secrets or KeyringSecretStore()

    # -------- Persona lookups --------

    def get_persona(self, name: str) -> Optional[Persona]:
        """Return the persona by name, or None if missing."""
        return self.store.get(name)

    def get_provider_username(self, persona: str, provider: str) -> Optional[str]:
        """Return the stored (non-secret) username for persona/provider."""
        p = self.get_persona(persona)
        if p is None:
            return None
        ref: Optional[ProviderRef] = p.providers.get(provider.lower())
        if ref is None:
            return None
        user = ref.get("username")
        return user if user else None

    # -------- Secrets --------

    def _secret_key(self, persona: str, provider: str, username: str) -> str:
        """TODO: Add vlaid docstring for PersonaManager: _secret_key

        Args:
            persona (str): _description_
            provider (str): _description_
            username (str): _description_

        Returns:
            str: _description_
        """
        return f"{persona}:{provider}:{username}"

    def get_secret(self, persona: str, provider: str) -> Optional[str]:
        """Return secret/password for personaprovider from secrets backend."""
        username = self.get_provider_username(persona, provider)
        if not username:
            return None
        key = self._secret_key(persona, provider, username)
        return self.secrets.get(_SERVICE, key)

    def has_secret(self, persona: str, provider: str) -> bool:
        """True if a secret exists for personaprovider."""
        return self.get_secret(persona, provider) is not None

    # -------- Strict API --------

    def require(self, persona: str, provider: str) -> Tuple[str, str]:
        """Return (username, secret) or raise typed errors for UX-friendly flow."""
        p = self.get_persona(persona)
        if p is None:
            raise PersonaNotFound(f"No such persona: '{persona}'")

        ref: Optional[ProviderRef] = p.providers.get(provider.lower())
        if ref is None:
            raise ProviderRefMissing(f"Persona '{persona}' has no '{provider}' ref")

        username = ref.get("username")
        if not username:
            raise ProviderRefMissing(
                f"Persona '{persona}' has empty username for '{provider}'"
            )

        key = self._secret_key(persona, provider, username)
        secret = self.secrets.get(_SERVICE, key)
        if not secret:
            raise SecretMissing(
                f"Missing secret for {provider} on persona '{persona}' (keyring empty?)"
            )
        return username, secret

    # -------- Display helpers --------

    @staticmethod
    def mask_username(u: str) -> str:
        """Return a lightly masked username for display."""
        if not u:
            return ""
        if len(u) <= 2:
            return u[0] + "*" * (len(u) - 1)
        return f"{u[0]}***{u[-1]}"
