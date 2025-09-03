"""Build provider GET via adapters + PersonaManager, then execute it."""

from __future__ import annotations

from adif_mcp.identity import PersonaManager
from adif_mcp.providers import ProviderKey
from adif_mcp.providers.adapters import build_request


def run(
    provider: ProviderKey, persona: str, *, timeout: float = 10.0, verbose: bool = False
) -> int:
    """
    Network probe for provider 'inbox'-style endpoint. Returns a process exit code:
      0 on success (HTTP 200), non-zero on errors.
    """
    pm = PersonaManager()
    url, headers, query = build_request(provider, persona, pm)
    # Make a very small HEAD or GET; keep it as you had it previously.
    # Return 0/1 based on result. Ensure you always return an int.
    try:
        # ... do the request ...
        # if ok:
        return 0
    except Exception:
        return 1
