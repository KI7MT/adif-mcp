"""Package metadata and tombstone flags for adif-mcp."""

from __future__ import annotations

__all__ = [
    "__version__",
    "__adif_spec__",
    "__deprecated__",
]

# Keep version in pyproject; hatch/pep621 will reflect it at build time,
# but we still mirror it here for runtime/tests.
__version__ = "0.3.7"

# Tests expect these to exist:
__adif_spec__ = "3.1.5"
__deprecated__ = True
