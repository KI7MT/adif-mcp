"""adif-mcp resources

Provides easy access to the following
- adif_meta.json
- adif_catalog.json
- { lotw,eqsl,clublog,wrz,usage }.json
- manifest.v1.json
- usage.json
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from importlib.resources import files
from typing import Any, cast


def _load_json(package: str, name: str) -> dict[str, Any]:
    """
    Load a JSON file from inside the package resources.

    Args:
        package: dotted package name (e.g. "adif_mcp.resources.providers")
        name: filename (e.g. "eqsl.json")

    Returns:
        dict[str, Any]: parsed JSON
    """
    p = files(package).joinpath(name)
    text = p.read_text(encoding="utf-8")
    return cast(dict[str, Any], json.loads(text))


# -------- Spec --------


def get_adif_meta() -> dict[str, Any]:
    """TODO: Add docstrings for: get_adif_meta

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.spec").joinpath("adif_meta.json")
    return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


def get_adif_catalog() -> dict[str, Any]:
    """Add docstrings for: get_adif_catalog

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.spec").joinpath("adif_catalog.json")
    return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


# -------- Providers --------


def list_providers() -> list[str]:
    """TODO: Add docstrings for: list providers

    Returns:
        List[str]: _description_
    """
    pkg = files("adif_mcp.resources.providers")
    entries: Iterable[str] = (child.name for child in pkg.iterdir())
    return sorted(n[:-5] for n in entries if n.endswith(".json"))


def load_provider(name: str) -> dict[str, Any]:
    """TODO: Add docstrings for load_providers

    Args:
        name (str): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.providers").joinpath(f"{name.lower()}.json")
    return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


# -------- Schemas --------


def get_manifest_schema() -> dict[str, Any]:
    """TODO: add docstrings for: get_manifest_schema

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.schemas").joinpath("manifest.v1.json")
    return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


# -------- Usage Mapping --------


# --- usage mapping ---------------------------------------------------------
def get_usage_map() -> dict[str, Any]:
    """
    Load the provider usage/mapping registry.

    Prefers the new canonical location:
        adif_mcp/resources/mapping/usage.json
    Falls back to legacy:
        adif_mcp/resources/providers/usage.json
    """
    # New location
    try:
        p = files("adif_mcp.resources.mapping").joinpath("usage.json")
        if p.is_file():
            return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        pass

    # Legacy fallback (temporary)
    p_old = files("adif_mcp.resources.providers").joinpath("usage.json")
    if p_old.is_file():
        return cast(dict[str, Any], json.loads(p_old.read_text(encoding="utf-8")))

    raise FileNotFoundError(
        "usage.json not found in resources/mapping (or legacy providers/) — "
        "did you package the resource?"
    )


# --- providers -------------------------------------------------------------
def get_provider_schema(provider: str) -> dict[str, Any]:
    """
    Load the JSON schema/field map for a given provider.

    Args:
        provider: Provider key (e.g., "eqsl", "lotw", "clublog", "qrz").

    Returns:
        dict[str, Any]: Parsed provider JSON definition.

    Raises:
        FileNotFoundError: If the provider JSON file is not found.
        json.JSONDecodeError: If the file exists but contains invalid JSON.
    """
    provider = provider.lower()
    p = files("adif_mcp.resources.providers").joinpath(f"{provider}.json")
    if not p.is_file():  # <-- Traversable.has .is_file(), not .exists()
        raise FileNotFoundError(f"No schema JSON for provider '{provider}'")
    return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))
