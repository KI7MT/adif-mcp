"""Provider package exports and shared types."""

from __future__ import annotations

from typing import Literal

# Literal across the package for mypy strictness.
ProviderKey = Literal["lotw", "eqsl", "qrz", "clublog"]

__all__ = ["ProviderKey"]
