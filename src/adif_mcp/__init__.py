"""adif-mcp (Python) — DEPRECATED.

This package is no longer maintained. Future development is moving to Java 21.
See: https://github.com/KI7MT/adif-mcp for details.
"""

__all__ = ["__version__", "DEPRECATION_MSG"]

__version__ = "0.3.7"
DEPRECATION_MSG = (
    "adif-mcp (Python) is deprecated. Future development is moving to Java 21.\n"
    "See the repository README for migration details."
)

# Original __init__.py before tombstone
# src/adif_mcp/__init__.py
# from __future__ import annotations

# from importlib.metadata import PackageNotFoundError, version
# from typing import Final

# # Resolve once, then bind to Final exactly once
# try:
#     _pkg_version = version("adif-mcp")
# except PackageNotFoundError:  # local dev / editable installs without dist metadata
#     _pkg_version = "0.0.0"

# __version__: Final[str] = _pkg_version
# __adif_spec__: Final[str] = "3.1.5"
