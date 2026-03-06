"""Identity namespace (personas, credential orchestration).

This package defines a clean boundary for AuthN concerns:
- models:   pure data types (Persona, ProviderRef)
- store:    persistence (PersonaStore) with OS-agnostic paths
- manager:  orchestration facade with typed errors and helpers
- errors:   typed exception classes for predictable failure modes
"""

from __future__ import annotations

from .errors import CredentialError, PersonaNotFound, ProviderRefMissing, SecretMissing
from .manager import PersonaManager
from .models import Persona, ProviderRef
from .store import PersonaStore

__all__ = [
    "CredentialError",
    "Persona",
    "PersonaManager",
    "PersonaNotFound",
    "PersonaStore",
    "ProviderRef",
    "ProviderRefMissing",
    "SecretMissing",
]
