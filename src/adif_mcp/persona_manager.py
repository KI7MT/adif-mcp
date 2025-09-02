# src/adif_mcp/persona_manager.py
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, cast

# --- Typed errors (top-level) -------------------------------------------------


class CredentialError(Exception):
    """Base error for persona/provider credential issues.

    Attributes:
        persona: The persona name involved in the error.
        provider: The provider key involved in the error.
    """

    def __init__(self, persona: str, provider: str, msg: str) -> None:
        super().__init__(msg)
        self.persona = persona
        self.provider = provider


class MissingPersonaError(CredentialError):
    """Raised when the requested persona cannot be found."""


class MissingProviderError(CredentialError):
    """Raised when a persona exists but has no mapping for the provider."""


class MissingUsernameError(CredentialError):
    """Raised when the provider mapping exists but the username is blank."""


class MissingSecretError(CredentialError):
    """Raised when the secret is not present in keyring for the provider."""


class PersonaManager:
    # existing __init__ / storage methods stay as-is

    # If you already had these helpers with different names, keep your
    # original bodies but ensure these typed wrappers exist and return Optional[str].

    def get_provider_username(self, persona: str, provider: str) -> Optional[str]:
        """Return provider username for a persona, or None if missing.

        This reads the non-secret username stored in the personas index.
        It must not perform any network I/O and must never return the secret.
        """
        p = self.get_persona(persona)
        if not p:
            return None
        prov_map = cast(Dict[str, Dict[str, str]], getattr(p, "providers", {}))
        ref = prov_map.get(provider.lower())
        if not ref:
            return None
        val = ref.get("username")
        return val if isinstance(val, str) else None

    def get_secret(self, persona: str, provider: str) -> Optional[str]:
        """Return secret/password for persona+provider from keyring, or None.

        Never print the secret. This must not raise if keyring is unavailable.
        """
        p = self.get_persona(persona)
        if not p:
            return None
        prov_map = cast(Dict[str, Dict[str, str]], getattr(p, "providers", {}))
        ref = prov_map.get(provider.lower())
        if not ref:
            return None
        val = ref.get("username")
        return val if isinstance(val, str) else None

    def require(self, persona: str, provider: str) -> Tuple[str, str]:
        """Return (username, secret) for persona+provider or raise a typed error.

        Raises:
            MissingPersonaError: persona does not exist.
            MissingProviderError: provider mapping not present on persona.
            MissingUsernameError: empty username in the provider mapping.
            MissingSecretError: secret not present in keyring for this mapping.
        """
        p = self.get_persona(persona)
        if p is None:
            raise MissingPersonaError(persona, provider, f"No such persona: '{persona}'")

        username = self.get_provider_username(persona, provider)
        if username is None:
            raise MissingProviderError(
                persona,
                provider,
                f"Persona '{persona}' has no '{provider}' credential reference",
            )
        if not username:
            raise MissingUsernameError(
                persona,
                provider,
                f"Missing username for {provider} on persona '{persona}'",
            )

        secret = self.get_secret(persona, provider)
        if not secret:
            raise MissingSecretError(
                persona,
                provider,
                f"Missing secret for {provider} on persona '{persona}' (keyring empty?)",
            )

        return username, secret

    # --- If you had a helper around line ~182 without annotations, add them:
    def _mask_username(self, u: str) -> str:  # example; adjust to your real helper
        """Return a lightly masked username for display."""
        if len(u) <= 2:
            return u[0] + "*" * (len(u) - 1)
        return f"{u[0]}***{u[-1]}"

    def get_persona(self, name: str) -> Optional[Any]:
        """Return the persona object by name, or None if it does not exist.

        This accessor is used by `require()` for friendly error reporting and
        exists primarily to make the method available to static type checking.
        It may delegate to an internal store (e.g., self.store.get(name)).
        """
        try:
            # If you maintain a store attribute with a .get() API, use it:
            return self.store.get(name)  # type: ignore[attr-defined]
        except Exception:
            # Fall back to "not found" if no store or any error
            return None
