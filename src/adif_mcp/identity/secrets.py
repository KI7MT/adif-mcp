"""Secret backends used by the identity manager.

Defines a small protocol plus concrete backends:
- KeyringSecretStore: uses the `keyring` package (OS keychain)
- InMemorySecretStore: test/dummy backend for CI or unit tests
"""

from __future__ import annotations

from typing import Any, Optional, Protocol, cast, runtime_checkable


@runtime_checkable
class SecretStore(Protocol):
    """Protocol for credential secret storage."""

    def get(self, service: str, key: str) -> Optional[str]:
        """Return secret for (service, key) or None if missing."""

    def set(self, service: str, key: str, secret: str) -> None:
        """Persist secret for (service, key)."""

    def delete(self, service: str, key: str) -> None:
        """Remove secret for (service, key) if present."""


class KeyringSecretStore:
    """SecretStore backed by the OS keychain via `keyring`.

    Safe to construct even if keyring is unavailable; operations become no-ops
    that return None or raise RuntimeError with a friendly message.
    """

    # Explicit attributes to satisfy mypy under --strict
    _keyring: Any | None
    _err: Exception | None

    def __init__(self) -> None:
        """Initialize the KeyRingStor Object"""
        try:
            import keyring as kr
        except Exception as e:  # pragma: no cover - environment dependent
            self._keyring = None
            self._err = e
        else:
            self._keyring = kr
            self._err = None

    def _ensure(self) -> None:
        """Initialize secrets.py: _ensure object

        Raises:
            RuntimeError: returns error
        """
        if self._keyring is None:  # pragma: no cover - environment dependent
            raise RuntimeError(f"keyring unavailable: {self._err}")

    def get(self, service: str, key: str) -> Optional[str]:
        """TODO: Add valid docstring for KeyringSecretStore: get

        Args:
            service (str): _description_
            key (str): _description_

        Returns:
            Optional[str]: _description_
        """
        if self._keyring is None:
            return None
        # keyring.get_password returns Optional[str], but our _keyring is Any.
        # Cast to keep mypy happy without leaking Any.
        return cast(Optional[str], self._keyring.get_password(service, key))

    def set(self, service: str, key: str, secret: str) -> None:
        """TODO: Add valid docstring for KeyringSecretStore: set

        Args:
            service (str): _description_
            key (str): _description_
            secret (str): _description_
        """
        self._ensure()
        assert self._keyring is not None
        self._keyring.set_password(service, key, secret)

    def delete(self, service: str, key: str) -> None:
        """TODO: Add valid docstring for KeyringSecretStore: delete

        Args:
            service (str): _description_
            key (str): _description_
        """
        if self._keyring is None:
            return
        try:
            self._keyring.delete_password(service, key)
        except Exception:
            # Mirror tolerant behavior: ignore per-entry delete failures
            pass


class InMemorySecretStore:
    """Volatile SecretStore for tests."""

    def __init__(self) -> None:
        """In-Memory Class initialization"""
        self._data: dict[tuple[str, str], str] = {}

    def get(self, service: str, key: str) -> Optional[str]:
        """TODO: Add valid docstring for InMemorySecretStore: get
        Args:
            service (str): _description_
            key (str): _description_

        Returns:
            Optional[str]: _description_
        """
        return self._data.get((service, key))

    def set(self, service: str, key: str, secret: str) -> None:
        """TODO: Add valid docstring for InMemorySecretStore: set

        Args:
            service (str): _description_
            key (str): _description_
            secret (str): _description_
        """
        self._data[(service, key)] = secret

    def delete(self, service: str, key: str) -> None:
        """TODO: Add valid docstring for InMemorySecretStore: delete

        Args:
            service (str): _description_
            key (str): _description_
        """
        self._data.pop((service, key), None)
