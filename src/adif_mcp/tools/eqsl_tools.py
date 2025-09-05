# src/adif_mcp/tools/eqsl_tools.py
from __future__ import annotations

import os
import re
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal, TypedDict

from adif_mcp.identity import PersonaManager
from adif_mcp.providers.adapters import build_request

# ---------------------------
# Types
# ---------------------------


class QsoRecord(TypedDict, total=False):
    """Minimal, normalized QSO record for the demo tools."""

    call: str
    qso_date: str  # YYYYMMDD
    time_on: str  # HHMM or HHMMSS
    band: str | None
    mode: str | None
    freq: float | None  # MHz
    eqsl_qsl_rcvd: str | None  # Y/N/I/…
    eqsl_qslrdate: str | None  # YYYYMMDD
    adif: dict[str, str]


@dataclass(frozen=True)
class FetchResult:
    records: list[QsoRecord]


# ---------------------------
# Helpers
# ---------------------------

_FIELD_RE = re.compile(r"<([A-Za-z0-9_]+):(\d+)(?::[A-Za-z])?>([^<]*)", re.IGNORECASE)


def _today_yyyymmdd() -> str:
    return datetime.utcnow().strftime("%Y%m%d")


def _to_yyyymmdd(d: str | date | None) -> str:
    if d is None:
        return _today_yyyymmdd()
    if isinstance(d, date):
        return d.strftime("%Y%m%d")
    # assume ISO date "YYYY-MM-DD"
    try:
        return date.fromisoformat(d).strftime("%Y%m%d")
    except Exception:
        return _today_yyyymmdd()


def _parse_adif_min(text: str) -> list[dict[str, str]]:
    """
    Extremely small ADIF extractor that collects tag->value pairs per <EOR>.
    Not a full ADIF parser—good enough for the demo scope.
    """
    out: list[dict[str, str]] = []
    current: dict[str, str] = {}
    i = 0
    n = len(text)
    while i < n:
        # End of record?
        if text[i : i + 5].upper() == "<EOR>":
            if current:
                out.append(current)
                current = {}
            i += 5
            continue
        m = _FIELD_RE.match(text, i)
        if not m:
            i += 1
            continue
        tag, length_s, value = m.group(1), m.group(2), m.group(3)
        try:
            length = int(length_s)
        except ValueError:
            length = len(value)
        # Ensure we honor the declared length if value was truncated by regex
        if len(value) < length:
            # pull the missing tail straight from the stream after the match
            end = m.end()
            need = length - len(value)
            value = value + text[end : end + need]
            i = end + need
        else:
            i = m.end()
        current[tag.upper()] = value
    # trailing record without <EOR>
    if current:
        out.append(current)
    return out


def _to_qso(rec: dict[str, str]) -> QsoRecord:
    def ffloat(s: str | None) -> float | None:
        try:
            return float(s) if s else None
        except Exception:
            return None

    return QsoRecord(
        call=rec.get("CALL", "").upper(),
        qso_date=rec.get("QSO_DATE", ""),
        time_on=rec.get("TIME_ON", ""),
        band=rec.get("BAND"),
        mode=rec.get("MODE"),
        freq=ffloat(rec.get("FREQ")),
        eqsl_qsl_rcvd=rec.get("EQSL_QSL_RCVD"),
        eqsl_qslrdate=rec.get("EQSL_QSLRDATE"),
        adif=rec,  # pass the raw tags through for transparency
    )


def _download(
    url: str, headers: dict[str, str], query: dict[str, Any], timeout: float
) -> tuple[int, bytes]:
    q = urllib.parse.urlencode(query, doseq=True)
    full = f"{url}?{q}" if q else url
    req = urllib.request.Request(full, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        return resp.status, data


# ---------------------------
# Public API
# ---------------------------


def fetch_inbox(
    *,
    persona: str,
    since: str | date | None = None,
    timeout: float = 10.0,
    pm: PersonaManager | None = None,
    mock: bool | None = None,
) -> FetchResult:
    """
    Fetch the eQSL inbox since a date and return normalized QSO records.

    Selection:
      - mock=True or ADIF_MCP_EQSL_MOCK=1 uses a local sample ADIF file
        (env ADIF_MCP_EQSL_ADIF=<path>) or a small embedded sample.
      - Otherwise, performs a real GET using the provider adapter and persona creds.
    """
    if mock is None:
        mock = os.getenv("ADIF_MCP_EQSL_MOCK") == "1"

    if mock:
        # a) external sample path
        sample = os.getenv("ADIF_MCP_EQSL_ADIF")
        if sample and os.path.exists(sample):
            text = open(sample, encoding="utf-8").read()
        else:
            # b) tiny embedded sample (2 records, confirmed + unconfirmed)
            text = (
                "<CALL:5>KI7MT<QSO_DATE:8>20250901<TIME_ON:6>010203<BAND:3>20M<MODE:3>FT8"
                "<EQSL_QSL_RCVD:1>Y<EQSL_QSLRDATE:8>20250902<EOR>"
                "<CALL:5>K7ABC<QSO_DATE:8>20250901<TIME_ON:6>040506<BAND:3>40M<MODE:3>CW"
                "<EQSL_QSL_RCVD:1>N<EOR>"
            )
        recs = [_to_qso(r) for r in _parse_adif_min(text)]
        return FetchResult(records=recs)

    # Real fetch
    pm = pm or PersonaManager()
    url, headers, query = build_request("eqsl", persona, pm)
    # Respect since date if present; eQSL expects YYYYMMDD via 'RcvdSince'
    query = dict(query)  # copy; don't mutate adapter defaults
    query["RcvdSince"] = _to_yyyymmdd(since)

    status, body = _download(url, headers, query, timeout=timeout)
    if status != 200:
        # Return an empty set to keep the demo tool resilient (no secrets leaked)
        return FetchResult(records=[])
    text = body.decode("utf-8", errors="replace")
    recs = [_to_qso(r) for r in _parse_adif_min(text)]
    return FetchResult(records=recs)


def filter_summary(
    records: Iterable[QsoRecord],
    *,
    by: Literal["band", "mode"] = "band",
    confirmed_only: bool = False,
    date_from: str | None = None,  # YYYY-MM-DD
    date_to: str | None = None,  # YYYY-MM-DD
) -> dict[str, Any]:
    """Summarize QSOs by band or mode with optional date + confirmation filters."""

    def yyyymmdd_ok(d: str) -> bool:
        return bool(re.fullmatch(r"\d{8}", d or ""))

    def in_window(r: QsoRecord) -> bool:
        d = r.get("eqsl_qslrdate") or r.get("qso_date") or ""
        if not yyyymmdd_ok(d):
            return False if (date_from or date_to) else True
        if date_from and d < _to_yyyymmdd(date_from):
            return False
        if date_to and d > _to_yyyymmdd(date_to):
            return False
        return True

    # Work on a concrete list to satisfy both mypy (Sized) and logic clarity
    items: list[QsoRecord] = list(records)

    if confirmed_only:
        items = [r for r in items if (r.get("eqsl_qsl_rcvd") or "").upper() == "Y"]
    if date_from or date_to:
        items = [r for r in items if in_window(r)]

    key = "band" if by == "band" else "mode"
    tally: dict[str, int] = {}
    for r in items:
        # Guard each .upper() with a default string
        v = r.get(key)
        k = (v if isinstance(v, str) else "UNKNOWN").upper()
        tally[k] = tally.get(k, 0) + 1

    sample = items[:10]
    total_in = len(items)
    confirmed_in = sum(1 for r in items if (r.get("eqsl_qsl_rcvd") or "").upper() == "Y")

    return {
        "total": total_in,
        "confirmed": confirmed_in,
        f"by_{by}": [{"key": k, "count": v} for k, v in sorted(tally.items())],
        "sample": sample,
    }
