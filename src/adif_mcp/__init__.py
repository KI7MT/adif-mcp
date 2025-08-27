"""
adif_mcp: Core package for ADIF MCP — models, CLI, and manifest tooling.

This module exposes:
- __version__: the installed package version (from package metadata)
- __adif_spec__: ADIF spec version we target (from pyproject [tool.adif], if available)
- __adif_features__: short list of notable supported features
    (from pyproject [tool.adif], if available)

Design:
- In dev/editable installs, we read pyproject.toml ([tool.adif]) directly.
- In built wheels (where pyproject.toml isn’t packaged),
    we fall back to baked-in defaults.
"""

import json
from importlib import resources as _res
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Any, Dict, List, Tuple

# -------------------------
# Package version (metadata)
# -------------------------
try:
    __version__ = _pkg_version("adif-mcp")
except PackageNotFoundError:
    # Editable or not yet built — keep a harmless placeholder
    __version__ = "0.0.0"


# ------------------------------------------
# Read [tool.adif] from pyproject.toml (dev)
# ------------------------------------------
def _find_pyproject(start: Path) -> Path | None:
    """
    Walk upward from `start` to locate a pyproject.toml file.
    Returns the first match or None.
    """
    cur = start.resolve()
    for _ in range(6):  # walk up a handful of levels; adjust if needed
        cand = cur / "pyproject.toml"
        if cand.is_file():
            return cand
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _load_adif_from_pyproject() -> Tuple[str, List[str]] | None:
    """
    Try to load `[tool.adif]` from a nearby pyproject.toml.
    Returns (spec_version, features) if found, else None.
    """
    try:
        import tomllib  # Python 3.11+
    except Exception:
        return None

    here = Path(__file__).parent
    pyproject = _find_pyproject(here)
    if not pyproject:
        return None

    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except Exception:
        return None

    tool = data.get("tool", {})
    adif: Dict[str, Any] = tool.get("adif", {}) if isinstance(tool, dict) else {}
    spec_version = adif.get("spec_version")
    features = adif.get("features")

    if isinstance(spec_version, str) and isinstance(features, list):
        # Ensure features are strings
        features_str = [str(x) for x in features]
        return spec_version, features_str
    return None


# --------------------------
# Fallback baked-in defaults
# --------------------------

# If pyproject.toml isn’t present at runtime (e.g., installed wheel),
# we still expose meaningful values. Keep these aligned with your releases.

_DEFAULT_ADIF_SPEC = "3.1.5"
_DEFAULT_ADIF_FEATURES = ["core QSO model", "band/mode/QSL_RCVD enums"]


def _adif_meta() -> Tuple[str, List[str]]:
    """
    Resolve ADIF metadata (spec version + features), preferring pyproject.toml.
    """

    try:
        with (
            _res.files("adif_mcp")
            .joinpath("adif_meta.json")
            .open("r", encoding="utf-8") as fh
        ):
            data = json.load(fh)
            spec = data.get("spec_version")
            feats = data.get("features")
            if isinstance(spec, str) and isinstance(feats, list):
                return spec, [str(x) for x in feats]
    except Exception:
        pass

    loaded = _load_adif_from_pyproject()
    if loaded:
        return loaded

    # Optional future enhancement:
    #   Try reading a packaged JSON resource like "adif_meta.json" here.
    return _DEFAULT_ADIF_SPEC, _DEFAULT_ADIF_FEATURES


__adif_spec__, __adif_features__ = _adif_meta()
