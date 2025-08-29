"""eQSL stub tools: synthetic inbox + simple summaries.

This module is a temporary, offline stub to demo the MCP flow without
network calls. It produces a few plausible QSO records and can summarize
them by band or mode.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Literal

from adif_mcp.parsers.adif_reader import QSORecord  # canonical TypedDict

# Export a friendlier alias that tests (and callers) can import.
QsoRecord = QSORecord

__all__ = ["fetch_inbox", "filter_summary", "QsoRecord"]


def _sample_records(station: str) -> List[QSORecord]:
    """Return a small set of plausible QSO records for a station (synthetic)."""
    # Keep to fields defined by QSORecord; don't add extras like `adif_fields`.
    base: List[QSORecord] = [
        {
            "station_call": station,
            "call": "K7ABC",
            "qso_date": "20240812",
            "time_on": "0315",
            "band": "20m",
            "mode": "FT8",
        },
        {
            "station_call": station,
            "call": "JA1XYZ",
            "qso_date": "20240813",
            "time_on": "0712",
            "band": "30m",
            "mode": "CW",
        },
        {
            "station_call": station,
            "call": "W1AW",
            "qso_date": "20240814",
            "time_on": "1845",
            "band": "40m",
            "mode": "SSB",
        },
    ]
    # Slightly vary content by callsign to make tests less trivial
    if station.upper().startswith("K"):
        base.append(
            {
                "station_call": station,
                "call": "DL1ZZZ",
                "qso_date": "20240815",
                "time_on": "2010",
                "band": "20m",
                "mode": "FT8",
            }
        )
    return base


def fetch_inbox(callsign: str) -> Dict[str, List[QSORecord]]:
    """Synthetic 'inbox' for eQSL — returns a dict with 'records' list."""
    records = _sample_records(callsign.upper())
    return {"records": records}


def filter_summary(
    records: Iterable[QSORecord],
    by: Literal["band", "mode"],
) -> Dict[str, Dict[str, int]]:
    """Summarize an inbox by band or mode.

    Args:
        records: Iterable of QSORecord objects.
        by: Either "band" or "mode".

    Returns:
        {"summary": {<key>: count, ...}}

    Raises:
        ValueError: if `by` is not one of the allowed selectors.
    """
    # Runtime guard (protects against tests bypassing the Literal with cast(Any, ...))
    if by not in ("band", "mode"):
        raise ValueError(f"invalid selector for summary: {by!r}")

    counts: Dict[str, int] = {}
    for r in records:
        key = r.get(by) or "UNKNOWN"  # ensure a string
        counts[key] = counts.get(key, 0) + 1

    return {"summary": counts}
