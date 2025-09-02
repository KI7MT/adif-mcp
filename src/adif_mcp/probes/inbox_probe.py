"""Build provider GET via adapters + PersonaManager, then execute it."""

from __future__ import annotations

from typing import cast

from adif_mcp.identity import PersonaManager
from adif_mcp.probes import http_probe
from adif_mcp.providers import ProviderKey, adapters


def run(
    provider: ProviderKey | str,
    persona: str,
    *,
    timeout: float = 10.0,
    verbose: bool = False,
) -> int:
    """Run a single provider probe; return exit code (0 on OK)."""
    p: ProviderKey = cast(ProviderKey, provider.lower())
    pm = PersonaManager()
    url, headers, query = adapters.build_request(p, persona, pm)
    return http_probe.execute(
        provider=p,
        url=url,
        headers=headers,
        query=query,
        timeout=timeout,
        verbose=verbose,
    )
