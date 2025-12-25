# Internal API Reference

This section documents the internal Python APIs available for developers extending `adif-mcp`.

## Credentials Module

The `adif_mcp.credentials.credentials` module provides a secure abstraction over the operating system's keyring service.

### Constants

- **`SERVICE`**: `str`
  The keyring service name used by the application (`"adif-mcp"`).

### Functions

#### `get_creds`

```python
def get_creds(service: str, username: str) -> str | None:
    ...
```

Retrieves a secret from the secure keyring.

- **Parameters**:
    - `service` (`str`): The service name (usually `SERVICE`).
    - `username` (`str`): The account username or identifier.
- **Returns**:
    - `str | None`: The secret if found, otherwise `None`.

#### `set_creds`

```python
def set_creds(service: str, username: str, secret: str) -> None:
    ...
```

Securely stores a secret in the keyring.

- **Parameters**:
    - `service` (`str`): The service name (usually `SERVICE`).
    - `username` (`str`): The account username or identifier.
    - `secret` (`str`): The password or API token to store.

> **Note**: If no keyring backend is available (e.g., headless Linux without `gnome-keyring`), these functions may fallback to a warning or no-op depending on the configuration, but secrets are **never** stored in plain text on disk.
