"""adif-mcp resources

Provides easy acces to the following
- adif_meta.json
- adif_catalog.json
- { lotw,eqsl,clublog,wrz,usage }.json
- manifest.v1.json
"""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any, Dict, Iterable, List, cast

# -------- Spec --------


def get_adif_meta() -> Dict[str, Any]:
    """TODO: Add docstrings for: get_adif_meta

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.spec").joinpath("adif_meta.json")
    return cast(Dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


def get_adif_catalog() -> Dict[str, Any]:
    """Add docstrings for: get_adif_catalog

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.spec").joinpath("adif_catalog.json")
    return cast(Dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


# -------- Providers --------


def list_providers() -> List[str]:
    """TODO: Add docstrings for: list providers

    Returns:
        List[str]: _description_
    """
    pkg = files("adif_mcp.resources.providers")
    entries: Iterable[str] = (child.name for child in pkg.iterdir())
    return sorted(n[:-5] for n in entries if n.endswith(".json"))


def load_provider(name: str) -> Dict[str, Any]:
    """TODO: Add docstrings for load_providers

    Args:
        name (str): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.providers").joinpath(f"{name.lower()}.json")
    return cast(Dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


# -------- Schemas --------


def get_manifest_schema() -> Dict[str, Any]:
    """TODO: add docstrings for: get_manifest_schema

    Returns:
        Dict[str, Any]: _description_
    """
    p = files("adif_mcp.resources.schemas").joinpath("manifest.v1.json")
    return cast(Dict[str, Any], json.loads(p.read_text(encoding="utf-8")))
