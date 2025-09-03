from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, cast


def load_env_defaults(p: Path) -> dict[str, object]:
    """Load a JSON file of environment defaults as a plain dict[str, object]."""
    # json.loads returns dict[str, Any]; narrow to object for tests
    data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return cast(Dict[str, object], data)


def _load_sample(name: str) -> Dict[str, object]:
    """Load a test JSON blob from test/data and return as dict[str, object]."""
    here = Path(__file__).parent / "data"
    data: Dict[str, Any] = json.loads((here / name).read_text(encoding="utf-8"))
    return cast(Dict[str, object], data)


def records_min() -> List[Dict[str, str]]:
    """Small minimal record list used by several tests."""
    return [
        {
            "station_call": "KI7MT",
            "call": "K7ABC",
            "qso_date": "20250101",
            "time_on": "010203",
            "band": "20m",
            "mode": "FT8",
            "rst_sent": "59",
            "rst_rcvd": "59",
            "freq": "14.074",
            "gridsquare": "DN41",
        }
    ]


def records_two_modes() -> List[Dict[str, str]]:
    """Two records with different modes for summary tests."""
    return [
        {
            "station_call": "KI7MT",
            "call": "K7ABC",
            "qso_date": "20250101",
            "time_on": "010203",
            "band": "20m",
            "mode": "FT8",
            "rst_sent": "59",
            "rst_rcvd": "59",
            "freq": "14.074",
            "gridsquare": "DN41",
        },
        {
            "station_call": "KI7MT",
            "call": "K7XYZ",
            "qso_date": "20250102",
            "time_on": "020304",
            "band": "20m",
            "mode": "CW",
            "rst_sent": "599",
            "rst_rcvd": "599",
            "freq": "14.020",
            "gridsquare": "DN41",
        },
    ]
