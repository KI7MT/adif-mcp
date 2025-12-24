"""Stub implementation for eQSL integration tools."""

from typing import Dict, Iterable, List

from adif_mcp.parsers.adif_reader import QSORecord


def fetch_inbox(callsign: str) -> Dict[str, List[QSORecord]]:
    """
    Simulates fetching the eQSL Inbox for a given callsign.
    Returns synthetic data for testing/MVP.
    """
    call = callsign.upper()
    # Synthetic data
    records: List[QSORecord] = [
        {
            "station_call": call,
            "call": "K1JT",
            "qso_date": "20250101",
            "time_on": "1200",
            "band": "20M",
            "mode": "FT8",
        },
        {
            "station_call": call,
            "call": "W1AW",
            "qso_date": "20250102",
            "time_on": "1300",
            "band": "40M",
            "mode": "CW",
        },
    ]
    return {"records": records}


def filter_summary(records: Iterable[QSORecord], by: str) -> Dict[str, Dict[str, int]]:
    """
    Aggregates counts of records by a specific field (band, mode, etc).
    """
    if by not in {"band", "mode", "call", "station_call", "qso_date", "time_on"}:
        raise ValueError(f"Invalid summary field: {by}")

    summary: Dict[str, int] = {}
    for rec in records:
        # TypedDict access with variable key requires casting or ignore for strict mypy
        val = str(rec.get(by, "UNKNOWN"))
        summary[val] = summary.get(val, 0) + 1
    return {"summary": summary}
