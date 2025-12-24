"""Stub implementation for ClubLog integration tools."""

from typing import TypedDict


class ClublogStatus(TypedDict):
    """Shape of a ClubLog status report."""

    callsign: str
    dxcc_confirmed: int
    slots_confirmed: int
    last_upload: str
    propagation_forecast: str


def fetch_status(callsign: str) -> ClublogStatus:
    """
    Simulates fetching ClubLog status for a given callsign.
    """
    return {
        "callsign": callsign.upper(),
        "dxcc_confirmed": 150,
        "slots_confirmed": 500,
        "last_upload": "2025-01-02",
        "propagation_forecast": "Good conditions on 20m/15m",
    }
