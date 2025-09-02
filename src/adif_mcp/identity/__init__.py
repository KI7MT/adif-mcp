"""Identity namespace (personas, credential orchestration, secrets).

This package defines a clean boundary for AuthN concerns:
- models:   pure data types (Persona, ProviderRef)
- store:    persistence (PersonaStore) with OS-agnostic paths
- secrets:  secret backends (e.g., keyring), swappable & testable
- manager:  orchestration facade with typed errors and helpers
- errors:   typed exception classes for predictable failure modes

During v0.3.0 this namespace wraps legacy modules to keep imports
stable while we migrate implementations. In a later minor release,
implementations will live here natively.
"""

from __future__ import annotations

from .errors import CredentialError, PersonaNotFound, ProviderRefMissing, SecretMissing
from .manager import PersonaManager
from .models import Persona, ProviderRef
from .secrets import InMemorySecretStore, KeyringSecretStore, SecretStore
from .store import PersonaStore

__all__ = [
    "Persona",
    "ProviderRef",
    "PersonaStore",
    "SecretStore",
    "KeyringSecretStore",
    "InMemorySecretStore",
    "PersonaManager",
    "CredentialError",
    "PersonaNotFound",
    "ProviderRefMissing",
    "SecretMissing",
]
