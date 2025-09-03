# src/adif_mcp/cli/provider.py
from __future__ import annotations

from typing import cast

import click

from adif_mcp import __adif_spec__, __version__
from adif_mcp.probes import inbox_probe, index_probe
from adif_mcp.providers import ProviderKey


def register_provider(root: click.Group) -> None:
    """Attach the `provider` command group to the root CLI."""

    @root.group("provider")
    @click.version_option(version=__version__, prog_name="adif-mcp provider")
    def provider_group() -> None:
        """Provider tools (probes, etc.)."""
        return

    @provider_group.command("version")
    def provider_version() -> None:
        """Show package version and ADIF spec compatibility."""
        click.echo(f"adif-mcp provider {__version__} (ADIF {__adif_spec__} compatible)")

    @provider_group.command("probe")
    @click.option(
        "--provider",
        required=True,
        type=click.Choice(["lotw", "eqsl", "qrz", "clublog"], case_sensitive=False),
    )
    @click.option("--persona", required=True)
    @click.option("--timeout", type=float, default=10.0, show_default=True)
    @click.option("--verbose", is_flag=True)
    @click.option(
        "--real", is_flag=True, help="Reserved; behaves same as GET probe for now."
    )
    def provider_probe(
        provider: str, persona: str, timeout: float, verbose: bool, real: bool
    ) -> None:
        """Probe the provider for valid connection."""
        pkey = cast(ProviderKey, provider.lower())
        code = inbox_probe.run(pkey, persona, timeout=timeout, verbose=verbose)
        raise SystemExit(code)

    @provider_group.command("index-check")
    @click.option(
        "--provider",
        required=True,
        type=click.Choice(["lotw", "eqsl", "qrz", "clublog"], case_sensitive=False),
    )
    @click.option("--persona", required=True)
    def provider_index_check(provider: str, persona: str) -> None:
        """Verify credentials by performing an index check on the provider."""
        pkey = cast(ProviderKey, provider.lower())
        code = index_probe.run(pkey, persona)
        raise SystemExit(code)
