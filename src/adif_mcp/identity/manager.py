"""PersonaManager facade for identity operations."""

from __future__ import annotations

from adif_mcp.credentials import get_creds

from .errors import PersonaNotFound, ProviderRefMissing, SecretMissing
from .models import Persona, ProviderRef
from .store import PersonaStore


class PersonaManager:
    """High-level API for personas + credentials (no network I/O)."""

    def __init__(self, store: PersonaStore | None = None) -> None:
        """Create a new manager with a persona store."""
        self.store: PersonaStore = store or PersonaStore()

    # -------- Persona lookups --------

    def get_persona(self, name: str) -> Persona | None:
        """Return the persona by name, or None if missing."""
        return self.store.get(name)

    def get_provider_username(self, persona: str, provider: str) -> str | None:
        """Return the stored (non-secret) username for persona/provider."""
        p = self.get_persona(persona)
        if p is None:
            return None
        ref: ProviderRef | None = p.providers.get(provider.lower())
        if ref is None:
            return None
        user = ref.get("username")
        return user if user else None

    # -------- Strict API --------

    def require(self, persona: str, provider: str) -> tuple[str, str]:
        """Return (username, secret) or raise typed errors for UX-friendly flow."""
        p = self.get_persona(persona)
        if p is None:
            raise PersonaNotFound(persona, provider, f"No such persona: '{persona}'")

        ref: ProviderRef | None = p.providers.get(provider.lower())
        if ref is None:
            raise ProviderRefMissing(
                persona, provider, f"Persona '{persona}' has no '{provider}' ref"
            )

        username = ref.get("username")
        if not username:
            raise ProviderRefMissing(
                persona, provider,
                f"Persona '{persona}' has empty username for '{provider}'"
            )

        # Use the credentials module (same key format as CLI)
        creds = get_creds(persona, provider)
        if not creds:
            raise SecretMissing(
                persona, provider,
                f"Missing credentials for {provider} on persona '{persona}' "
                f"(run: adif-mcp creds set {persona} {provider})"
            )

        # Return password or api_key depending on what's stored
        secret = creds.password or creds.api_key
        if not secret:
            raise SecretMissing(
                persona, provider,
                f"No password/api_key for {provider} on persona '{persona}'"
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
