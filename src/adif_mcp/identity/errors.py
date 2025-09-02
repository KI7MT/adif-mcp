"""Typed exception classes for identity/persona management."""

from __future__ import annotations


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


class PersonaNotFound(CredentialError):
    """Requested persona name not present in the store."""


class ProviderRefMissing(CredentialError):
    """Persona exists, but no username ref for the given provider."""


class SecretMissing(CredentialError):
    """Persona/provider ref found, but secret is not available in the backend."""
