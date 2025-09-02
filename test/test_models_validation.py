"""Pydantic models (QSO, enums) validation and normalization."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from adif_mcp.models import QsoRecord


def test_valid_qso_parses() -> None:
    """A normal record validates cleanly."""
    raw: Dict[str, Any] = {
        "station_call": "KI7MT",
        "call": "K7ABC",
        "qso_date": "20250101",
        "time_on": "1200",
        "band": "20m",
        "mode": "FT8",
    }
    rec = QsoRecord(**raw)
    assert rec.band == "20m"
    assert rec.mode == "FT8"


def test_invalid_rst_rejected() -> None:
    """Bad RST fails validation."""
    d: Dict[str, Any] = {
        "station_call": "KI7MT",
        "call": "K7ABC",
        "qso_date": "20250101",
        "time_on": "1200",
        "band": "20m",
        "mode": "FT8",
        "rst_rcvd": "9X9",  # invalid
    }
    with pytest.raises(ValueError):
        QsoRecord(**d)
