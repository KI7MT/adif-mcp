# src/adif_mcp/util_paths.py
"""
Cross-platform config path resolver for ADIF-MCP.

Features:
- OS-agnostic per-user config dir
  * Linux/macOS: $XDG_CONFIG_HOME/<project> or ~/.config/<project>
  * Windows: %APPDATA%\\<project>

- Optional overrides via pyproject.toml:
    [tool.adif]
    project_name = "adif-mcp"               # folder name under the user config root
    personas_index = "{config_dir}/personas.json"

Public API:
- config_dir() -> Path
- config_path(name: str) -> Path
- personas_index_path() -> Path
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover - py<=3.10 not supported by this project
    tomllib = None  # type: ignore[assignment]


# ---------------------------
# pyproject reading utilities
# ---------------------------


def _find_pyproject(start: Path | None = None) -> Path | None:
    """
    Walk upward from `start` (or CWD) to locate a pyproject.toml file.

    Returns:
        Path to pyproject.toml or None if not found (within a few levels).
    """
    root = (start or Path.cwd()).resolve()
    for _ in range(8):
        cand = root / "pyproject.toml"
        if cand.is_file():
            return cand
        if root.parent == root:
            break
        root = root.parent
    return None


def _load_tool_adif(pyproject: Path | None) -> tuple[str | None, str | None]:
    """
    Load `[tool.adif]` fields we care about.

    Returns:
        (project_name, personas_index) where either may be None if absent.
    """
    if not pyproject or tomllib is None:
        return None, None

    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except Exception:
        return None, None

    tool = data.get("tool", {})
    adif = tool.get("adif", {}) if isinstance(tool, dict) else {}
    pn = adif.get("project_name")
    pi = adif.get("personas_index")
    return (
        str(pn) if isinstance(pn, str) else None,
        str(pi) if isinstance(pi, str) else None,
    )


# ---------------------------
# OS-agnostic config root
# ---------------------------


def _os_config_root() -> Path:
    """
    OS-agnostic user config root (without project suffix).
    """
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)

    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base)
        # Reasonable fallback
        return Path.home() / "AppData" / "Roaming"

    # Linux/macOS default
    return Path.home() / ".config"


def _project_name() -> str:
    """
    Determine the config folder name under the user config root.

    Prefers `[tool.adif].project_name`, else defaults to 'adif-mcp'.
    """
    pyproj = _find_pyproject()
    name, _ = _load_tool_adif(pyproj)
    return name or "adif-mcp"


def config_dir() -> Path:
    """
    Resolve and create the per-user config directory for the project.

    Returns:
        Path to the user config directory (guaranteed to exist).
    """
    root = _os_config_root() / _project_name()
    root.mkdir(parents=True, exist_ok=True)
    return root


def config_path(filename: str) -> Path:
    """
    Resolve a file under the project’s per-user config directory.

    Args:
        filename: File name under the config directory.

    Returns:
        Full path to `<config_dir()>/<filename>`. Parent dirs ensured.
    """
    p = config_dir() / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def personas_index_path() -> Path:
    """
    Resolve the personas index file path, honoring pyproject override.

    If `[tool.adif].personas_index` is provided, it may include the
    `{config_dir}` placeholder, which will be expanded to `config_dir()`.

    Returns:
        Path to personas index JSON.
    """
    pyproj = _find_pyproject()
    _, override = _load_tool_adif(pyproj)
    if override:
        expanded = override.replace("{config_dir}", str(config_dir()))
        path = Path(expanded)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    return config_path("personas.json")
