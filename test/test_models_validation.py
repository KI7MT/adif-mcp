"""Pydantic models (QSO, enums) validation and normalization."""

from __future__ import annotations

import pytest

from adif_mcp.models import QsoRecord


def test_valid_qso_parses() -> None:
    """A normal record validates cleanly."""
    d = {
        "station_call": "KI7MT",
        "call": "K7ABC",
        "qso_date": "20240812",
        "time_on": "031500",
        "band": "30m",
        "mode": "FT8",
        "rst_sent": "599",
        "rst_rcvd": "579",
    }
    q = QsoRecord(**d)
    assert q.call == "K7ABC"


def test_invalid_rst_rejected() -> None:
    """Bad RST fails validation."""
    d = {
        "station_call": "KI7MT",
        "call": "K7ABC",
        "qso_date": "20240812",
        "time_on": "0315",
        "band": "30m",
        "mode": "FT8",
        "rst_sent": "59X9",  # invalid
    }
    with pytest.raises(Exception):
        QsoRecord(**d)
