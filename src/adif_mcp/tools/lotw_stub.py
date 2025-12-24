"""Stub implementation for LoTW integration tools."""

from typing import Dict, TypedDict


class LotwReport(TypedDict):
    """Shape of a LoTW report."""

    callsign: str
    last_upload: str
    qsls_count: int
    dxcc_credits: Dict[str, int]


def fetch_report(callsign: str) -> LotwReport:
    """
    Simulates fetching a LoTW report for a given callsign.
    """
    return {
        "callsign": callsign.upper(),
        "last_upload": "2025-01-01",
        "qsls_count": 1234,
        "dxcc_credits": {
            "Mixed": 100,
            "CW": 50,
            "Phone": 50,
            "Digital": 25,
        },
    }
