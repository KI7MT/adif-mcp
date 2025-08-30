"""Shared pytest fixtures for adif-mcp tests.

Fixtures provided:
- inbox_for_callsign: factory that returns synthetic eQSL inbox records.
- sample_adi_records: minimal ADIF snippet parsed to QSO records.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from typing import Callable, List

import pytest

from adif_mcp.parsers.adif_reader import QSORecord, parse_adi_text
from adif_mcp.tools.eqsl_stub import fetch_inbox


@pytest.fixture(scope="session")
def inbox_for_callsign() -> Callable[[str], List[QSORecord]]:
    """Factory that returns a list of QSO dicts for the given callsign
    using the eqsl_stub."""

    def _get(cs: str) -> List[QSORecord]:
        """Returns a list of QSRecords

        Args:
            cs (list): Get list of QSORecord

        Returns:
            List[QSORecord]: Return a list of QQSORecord
        """
        out = fetch_inbox(cs)  # returns {"records": List[QSORecord]}
        # return cast(List[QSORecord], out["records"])
        return out["records"]

    return _get


@pytest.fixture(scope="session")
def sample_adi_records() -> List[QSORecord]:
    """Minimal ADIF snippet parsed into QSO records for smoke tests."""
    txt = "<CALL:5>KI7MT<QSO_DATE:8>20240812<TIME_ON:4>0315<EOR>"
    # return cast(List[QSORecord], parse_adi_text(txt))
    return parse_adi_text(txt)
