#!/usr/bin/env python3
"""
convert-adi.py — Convert ADIF (.adi) logs into JSON/NDJSON of QsoRecord with provenance.

Highlights:
- Auto-detect station callsign from ADIF header (<EOH>) or CLI --station-call
- Normalizes band ("40M"→"40m"), maps eQSL eqsl_qslrdate→eqsl_qsl_date
- Provenance in `adif_fields`: _station_call_source, _band_source,
                _eqsl_date_mapped,_source_program, etc.
- NDJSON streaming for huge logs (500k–1M QSOs)
- Streaming errors (NDJSON) and on-the-fly stats
- Provider-agnostic streaming filters: band, mode, call, date range,
                confirmed-only, comment contains

Exit codes:
  0 → all emitted records converted cleanly (no validation errors)
  1 → some records failed validation (see --errors / --errors-ndjson)
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TypedDict


class _ErrorRec(TypedDict):
    index: int
    error: str
    fields: dict[str, str]


# ---------- ADIF parsing primitives ----------

ADIF_EOR = re.compile(r"<EOR>", re.IGNORECASE)
ADIF_FIELD = re.compile(
    r"<(?P<name>[A-Za-z0-9_]+):(?P<len>\d+)(?::(?P<type>[A-Za-z]))?>",
    re.IGNORECASE,
)


def _coerce_value(raw: str, vtype: str | None) -> str:
    # Keep as string for safety; schema validation downstream handles types.
    """_summary_

    Args:
        raw (str): _description_
        vtype (str | None): _description_

    Returns:
        str: _description_
    """
    return raw


def parse_adif(text: str) -> Iterator[dict[str, str]]:
    """Yield ADIF records as dicts (keys lowercased)."""
    m_eoh = re.search(r"<EOH>", text, flags=re.IGNORECASE)
    body = text[m_eoh.end() :] if m_eoh else text

    idx: int = 0
    current: dict[str, str] = {}

    while idx < len(body):
        m_eor = ADIF_EOR.match(body, idx)
        if m_eor:
            if current:
                yield current
                current = {}
            idx = m_eor.end()
            continue

        m = ADIF_FIELD.match(body, idx)
        if not m:
            idx += 1
            continue

        name = m.group("name").lower()
        length = int(m.group("len"))
        vtype = m.group("type")
        val = body[m.end() : m.end() + length]
        idx = m.end() + length
        current[name] = _coerce_value(val.strip(), vtype)

    if current:
        yield current


# ---------- Header parsing (for station call + source program) ----------
HEADER_CALL_PATTERNS = [
    re.compile(r"Received\s+eQSLs\s+for\s+([A-Z0-9/]+)", re.IGNORECASE),
]


def _extract_header_info(
    full_text: str,
) -> tuple[str | None, str | None, str | None]:
    """
    Returns (station_call, station_call_source, source_program)
      station_call_source: "header_tag:<tag>" | "header_text" | None
      source_program: e.g., "eQSL.cc DownloadInBox" if <PROGRAMID:...> present
    """
    m_eoh = re.search(r"<EOH>", full_text, flags=re.IGNORECASE)
    header = full_text[: m_eoh.start()] if m_eoh else full_text

    # 1) ADIF tags in header
    idx = 0
    station_tag_val: str | None = None
    station_tag_name: str | None = None
    source_program: str | None = None

    while True:
        m = ADIF_FIELD.search(header, idx)
        if not m:
            break
        name = m.group("name").lower()
        length = int(m.group("len"))
        vtype = m.group("type")
        val = _coerce_value(header[m.end() : m.end() + length].strip(), vtype)
        if (
            name in ("station_callsign", "my_call", "operator", "station_call")
            and val
            and not station_tag_val
        ):
            station_tag_val = val.upper()
            station_tag_name = name
        if name == "programid" and val:
            source_program = val  # e.g., "eQSL.cc DownloadInBox"
        idx = m.end() + length

    if station_tag_val:
        return station_tag_val, f"header_tag:{station_tag_name}", source_program

    # 2) Plain-text fallback (eQSL style)
    for pat in HEADER_CALL_PATTERNS:
        pm = pat.search(header)
        if pm:
            return pm.group(1).upper(), "header_text", source_program

    return None, None, source_program


# ---------- helpers ----------
def _float_opt(s: str | None) -> float | None:
    """_summary_

    Args:
        s (str | None): _description_

    Returns:
        float | None: _description_
    """
    if s is None or s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _band_from_freq_mhz(freq: float | None) -> str | None:
    """_summary_

    Args:
        freq (float | None): _description_

    Returns:
        str | None: _description_
    """
    if freq is None:
        return None
    f = freq
    if 1.8 <= f < 2.0:
        return "160m"
    if 3.3 <= f < 4.0:
        return "80m"
    if 5.2 <= f < 5.5:
        return "60m"
    if 7.0 <= f < 7.3:
        return "40m"
    if 10.0 <= f < 10.15:
        return "30m"
    if 14.0 <= f < 14.35:
        return "20m"
    if 18.068 <= f < 18.168:
        return "17m"
    if 21.0 <= f < 21.45:
        return "15m"
    if 24.89 <= f < 24.99:
        return "12m"
    if 28.0 <= f < 29.7:
        return "10m"
    if 50.0 <= f < 54.0:
        return "6m"
    if 144.0 <= f < 148.0:
        return "2m"
    if 420.0 <= f < 450.0:
        return "70cm"
    return None


# ---------- domain ----------
@dataclass(frozen=True)
class QsoRecord:
    """_summary_"""

    station_call: str
    call: str
    qso_date: str  # YYYYMMDD
    time_on: str  # HHMM[SS]
    band: str
    mode: str
    freq: float | None = None
    rst_sent: str | None = None
    rst_rcvd: str | None = None
    my_gridsquare: str | None = None
    gridsquare: str | None = None
    tx_pwr: float | None = None
    comment: str | None = None
    lotw_qsl_rcvd: str | None = None
    eqsl_qsl_rcvd: str | None = None
    lotw_qsl_date: str | None = None
    eqsl_qsl_date: str | None = None
    adif_fields: dict[str, str] | None = field(default=None)


# module-global defaults used by builder/filters
_DEFAULT_STATION_CALL: str | None = None
_DEFAULT_STATION_CALL_SOURCE: str | None = None  # "cli" | "header_tag:<tag>" | "header_text"
_DEFAULT_SOURCE_PROGRAM: str | None = None  # e.g., "eQSL.cc DownloadInBox"


def build_qso(fields: dict[str, str]) -> QsoRecord:
    """Construct a QsoRecord from raw ADIF field map with provenance."""
    f = dict(fields)  # copy to annotate provenance/adif_fields
    prov: dict[str, str] = {}

    # Map real-world variants: eQSL eqsl_qslrdate → eqsl_qsl_date
    if "eqsl_qslrdate" in f and "eqsl_qsl_date" not in f:
        f["eqsl_qsl_date"] = f.get("eqsl_qslrdate", "")
        prov["_eqsl_date_mapped"] = "eqsl_qslrdate→eqsl_qsl_date"

    # If clearly an eQSL Inbox export and rcvd missing, imply Y
    if (
        (f.get("eqsl_qsl_rcvd") in (None, ""))
        and _DEFAULT_SOURCE_PROGRAM
        and "downloadinbox" in _DEFAULT_SOURCE_PROGRAM.lower()
    ):
        f["eqsl_qsl_rcvd"] = "Y"
        prov["_eqsl_inbox_implied_rcvd"] = "Y"

    # station_call with fallbacks
    if f.get("station_callsign"):
        station_call = f["station_callsign"]
        sc_source = "record:station_callsign"
    elif f.get("my_call"):
        station_call = f["my_call"]
        sc_source = "record:my_call"
    elif f.get("operator"):
        station_call = f["operator"]
        sc_source = "record:operator"
    elif f.get("station_call"):
        station_call = f["station_call"]
        sc_source = "record:station_call"
    else:
        station_call = _DEFAULT_STATION_CALL or ""
        sc_source = _DEFAULT_STATION_CALL_SOURCE or "unknown"

    call = f.get("call", "")
    qso_date = f.get("qso_date") or f.get("qso_date_off") or ""
    time_on = f.get("time_on") or f.get("time_off") or ""
    band = f.get("band") or ""
    mode = f.get("mode") or ""

    # Normalize/derive band
    band_source = "record"
    if band:
        b = band.strip()
        if b.endswith(("M", "m")) and b[:-1].isdigit():
            band = b[:-1].lower() + "m"
        else:
            band = b.lower()
    else:
        band = _band_from_freq_mhz(_float_opt(f.get("freq"))) or ""
        if band:
            band_source = "derived_from_freq"
    prov["_band_source"] = band_source

    # Validate requireds
    missing = [
        k
        for k, v in {
            "station_call": station_call,
            "call": call,
            "qso_date": qso_date,
            "time_on": time_on,
            "band": band,
            "mode": mode,
        }.items()
        if not v
    ]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Validate formats
    if not re.fullmatch(r"\d{8}", qso_date):
        raise ValueError(f"qso_date must be YYYYMMDD, got: {qso_date}")
    if not re.fullmatch(r"\d{4}(\d{2})?", time_on):
        raise ValueError(f"time_on must be HHMM[SS], got: {time_on}")

    # Provenance markers into adif_fields
    f["_station_call_source"] = sc_source
    if "eqsl_qslrdate" in fields:
        f["_had_eqsl_qslrdate"] = "1"
    if _DEFAULT_SOURCE_PROGRAM:
        f["_source_program"] = _DEFAULT_SOURCE_PROGRAM
    for k, v in prov.items():
        f[k] = v

    def _opt(k: str) -> str | None:
        v = f.get(k)
        return v if v not in ("", None) else None

    return QsoRecord(
        station_call=station_call,
        call=call,
        qso_date=qso_date,
        time_on=time_on,
        band=band,
        mode=mode,
        freq=_float_opt(f.get("freq")),
        rst_sent=_opt("rst_sent"),
        rst_rcvd=_opt("rst_rcvd"),
        my_gridsquare=_opt("my_gridsquare"),
        gridsquare=_opt("gridsquare"),
        tx_pwr=_float_opt(f.get("tx_pwr")),
        comment=_opt("comment"),
        lotw_qsl_rcvd=_opt("lotw_qsl_rcvd"),
        eqsl_qsl_rcvd=_opt("qsl_rcvd") or _opt("eqsl_qsl_rcvd"),
        lotw_qsl_date=_opt("lotw_qsl_date"),
        eqsl_qsl_date=_opt("eqsl_qsl_date"),
        adif_fields={k: str(v) for k, v in f.items() if v not in (None, "")} or None,
    )


# ---------- Writers (streaming-safe) ----------
# ---------- Writers (streaming-safe) ----------
def write_json(records: list[QsoRecord], out_path: Path, pretty: bool = False) -> None:
    """Write a JSON array of QsoRecord to disk.

    Uses a fixed signature for json.dumps so static type checkers don't
    see a generic **dict expansion (which confuses mypy).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(r) for r in records]
    if pretty:
        text = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        text = json.dumps(payload)
    out_path.write_text(text, encoding="utf-8")


def write_ndjson(records_iter: Iterable[QsoRecord], out_path: Path) -> int:
    """_summary_

    Args:
        records_iter (Iterable[QsoRecord]): _description_
        out_path (Path): _description_

    Returns:
        int: _description_
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for r in records_iter:
            f.write(json.dumps(asdict(r), ensure_ascii=False))
            f.write("\n")
            n += 1
    return n


def write_errors_ndjson(errors_iter: Iterable[dict[str, str]], out_path: Path) -> int:
    """_summary_

    Args:
        errors_iter (Iterable[dict[str, str]]): _description_
        out_path (Path): _description_

    Returns:
        int: _description_
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for e in errors_iter:
            f.write(json.dumps(e, ensure_ascii=False))
            f.write("\n")
            n += 1
    return n


# ---------- Filters ----------
def _record_matches_filters(
    r: QsoRecord,
    bands: list[str],
    modes: list[str],
    calls: list[str],
    since: str | None,
    until: str | None,
    confirmed_only: bool,
    contains_comment: str | None,
) -> bool:
    """_summary_

    Args:
        r (QsoRecord): _description_
        bands (list[str]): _description_
        modes (list[str]): _description_
        calls (list[str]): _description_
        since (str | None): _description_
        until (str | None): _description_
        confirmed_only (bool): _description_
        contains_comment (str | None): _description_

    Returns:
        bool: _description_
    """
    # bands (normalized to lowercase)
    if bands:
        if r.band.lower() not in [b.lower() for b in bands]:
            return False
    # modes (case-insensitive exact)
    if modes:
        if r.mode.upper() not in [m.upper() for m in modes]:
            return False
    # calls (exact, case-insensitive)
    if calls:
        if r.call.upper() not in [c.upper() for c in calls]:
            return False
    # date range (YYYYMMDD string compare is safe)
    if since and r.qso_date < since:
        return False
    if until and r.qso_date > until:
        return False
    # confirmation flag
    if confirmed_only:
        if not ((r.eqsl_qsl_rcvd == "Y") or (r.lotw_qsl_rcvd == "Y")):
            return False
    # comment substring
    if contains_comment:
        hay = (r.comment or "").lower()
        if contains_comment.lower() not in hay:
            return False
    return True


# ---------- Main pipeline ----------
def main(argv: Iterable[str] | None = None) -> int:
    """_summary_

    Args:
        argv (Iterable[str] | None, optional): _description_. Defaults to None.

    Returns:
        int: _description_

    Yields:
        Iterator[int]: _description_
    """
    p = argparse.ArgumentParser(
        prog="convert-adi",
        description="Convert ADIF (.adi) to QsoRecord "
        "JSON/NDJSON (streaming) with provenance.",
    )
    p.add_argument("-i", "--input", required=True, type=Path, help="Path to ADIF .adi file")
    p.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Path to write JSON/NDJSON output",
    )
    p.add_argument(
        "--errors",
        type=Path,
        default=None,
        help="Optional path to write validation errors (JSON or NDJSON)",
    )
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON array output")
    p.add_argument(
        "--ndjson",
        action="store_true",
        help="Write NDJSON (one QSO per line, memory-efficient)",
    )
    p.add_argument(
        "--errors-ndjson",
        action="store_true",
        help="Write errors as NDJSON (one error per line)",
    )
    p.add_argument(
        "--stats", action="store_true", help="Print totals and band/mode counts to stdout"
    )
    p.add_argument(
        "--station-call",
        type=str,
        default=None,
        help="Your station callsign; overrides header value if supplied",
    )

    # Filters
    p.add_argument(
        "--band",
        action="append",
        default=[],
        help="Filter: include only these bands (repeatable)",
    )
    p.add_argument(
        "--mode",
        action="append",
        default=[],
        help="Filter: include only these modes (repeatable)",
    )
    p.add_argument(
        "--call",
        action="append",
        default=[],
        help="Filter: include only these counterpart calls (repeatable)",
    )
    p.add_argument(
        "--since", type=str, default=None, help="Filter: qso_date >= YYYYMMDD (inclusive)"
    )
    p.add_argument(
        "--until", type=str, default=None, help="Filter: qso_date <= YYYYMMDD (inclusive)"
    )
    p.add_argument(
        "--confirmed-only",
        action="store_true",
        help="Filter: only confirmed (eQSL or LoTW == 'Y')",
    )
    p.add_argument(
        "--contains-comment",
        type=str,
        default=None,
        help="Filter: substring match in comment (case-insensitive)",
    )

    a = p.parse_args(list(argv) if argv is not None else None)

    # Read once, set defaults from header (or CLI)
    full_text = a.input.read_text(encoding="utf-8", errors="ignore")
    hdr_call, hdr_source, source_program = _extract_header_info(full_text)

    global _DEFAULT_STATION_CALL, _DEFAULT_STATION_CALL_SOURCE, _DEFAULT_SOURCE_PROGRAM
    if a.station_call:
        _DEFAULT_STATION_CALL = a.station_call.strip().upper()
        _DEFAULT_STATION_CALL_SOURCE = "cli"
    else:
        _DEFAULT_STATION_CALL = hdr_call
        _DEFAULT_STATION_CALL_SOURCE = hdr_source
    _DEFAULT_SOURCE_PROGRAM = source_program

    # Process records (stream)
    records_parser = parse_adif(full_text)

    # streaming stats for the *emitted subset*
    total_emitted = 0
    eqsl_y_emitted = 0
    by_band: Counter[str] = Counter()
    by_mode: Counter[str] = Counter()

    # errors handling
    errors_buffer: list[dict[str, str]] = [] if (a.errors and not a.errors_ndjson) else []

    if a.ndjson:
        # stream records to NDJSON
        def rec_iter() -> Iterator[QsoRecord]:
            nonlocal total_emitted, eqsl_y_emitted
            for idx, fields in enumerate(records_parser, start=1):
                try:
                    rec = build_qso(fields)
                    if _record_matches_filters(
                        rec,
                        bands=a.band,
                        modes=a.mode,
                        calls=a.call,
                        since=a.since,
                        until=a.until,
                        confirmed_only=a.confirmed_only,
                        contains_comment=a.contains_comment,
                    ):
                        total_emitted += 1
                        if rec.eqsl_qsl_rcvd == "Y":
                            eqsl_y_emitted += 1
                        by_band[rec.band] += 1
                        by_mode[rec.mode] += 1
                        yield rec
                except Exception as e:
                    err_obj: dict[str, str] = {
                        "index": str(idx),
                        "error": str(e),
                        "fields": json.dumps(fields, ensure_ascii=False),
                    }
                    if a.errors and a.errors_ndjson:
                        write_errors_ndjson([err_obj], a.errors)
                    elif a.errors:
                        errors_buffer.append(err_obj)

        write_ndjson(rec_iter(), a.output)
    else:
        # collect to list, then write JSON array
        rec_buffer: list[QsoRecord] = []
        for idx, fields in enumerate(records_parser, start=1):
            try:
                rec = build_qso(fields)
                if _record_matches_filters(
                    rec,
                    bands=a.band,
                    modes=a.mode,
                    calls=a.call,
                    since=a.since,
                    until=a.until,
                    confirmed_only=a.confirmed_only,
                    contains_comment=a.contains_comment,
                ):
                    rec_buffer.append(rec)
                    total_emitted += 1
                    if rec.eqsl_qsl_rcvd == "Y":
                        eqsl_y_emitted += 1
                    by_band[rec.band] += 1
                    by_mode[rec.mode] += 1
            except Exception as e:
                # Make a plain dict[str, str] so it matches write_errors_ndjson
                # and errors_buffer types
                err: dict[str, str] = {
                    "index": str(idx),
                    "error": str(e),
                    "fields": json.dumps(fields, ensure_ascii=False),
                }
                if a.errors and a.errors_ndjson:
                    write_errors_ndjson([err], a.errors)
                elif a.errors:
                    errors_buffer.append(err)

        write_json(rec_buffer, a.output, pretty=a.pretty)

    # write any buffered errors (single JSON)
    if a.errors and errors_buffer:
        a.errors.parent.mkdir(parents=True, exist_ok=True)
        a.errors.write_text(
            json.dumps(errors_buffer, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # print stats for the emitted subset
    if a.stats:
        print(f"Total QSOs (emitted): {total_emitted}")
        print(f"eQSL received (Y):    {eqsl_y_emitted}")
        if by_band:
            print("By band:")
            for b, n in by_band.most_common():
                print(f"  {b:>5}  {n}")
        if by_mode:
            print("By mode:")
            for m, n in by_mode.most_common():
                print(f"  {m:>6}  {n}")

    # exit code
    had_errors = a.errors and (errors_buffer or a.errors_ndjson)
    return 0 if not had_errors else 1


def add_convert_args(p: argparse.ArgumentParser) -> None:
    """_summary_

    Args:
        p (argparse.ArgumentParser): _description_
    """
    p.add_argument("-i", "--input", required=True, type=Path, help="Path to ADIF .adi file")
    p.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Path to write JSON/NDJSON output",
    )
    p.add_argument(
        "--errors",
        type=Path,
        default=None,
        help="Optional path to write validation errors (JSON or NDJSON)",
    )
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON array output")
    p.add_argument(
        "--ndjson",
        action="store_true",
        help="Write NDJSON (one QSO per line, memory-efficient)",
    )
    p.add_argument(
        "--errors-ndjson",
        action="store_true",
        help="Write errors as NDJSON (one error per line)",
    )
    p.add_argument(
        "--stats", action="store_true", help="Print totals and band/mode counts to stdout"
    )
    p.add_argument(
        "--station-call",
        type=str,
        default=None,
        help="Your station callsign; overrides header value if supplied",
    )
    # filters
    p.add_argument(
        "--band",
        action="append",
        default=[],
        help="Filter: include only these bands (repeatable)",
    )
    p.add_argument(
        "--mode",
        action="append",
        default=[],
        help="Filter: include only these modes (repeatable)",
    )
    p.add_argument(
        "--call",
        action="append",
        default=[],
        help="Filter: include only these counterpart calls (repeatable)",
    )
    p.add_argument(
        "--since", type=str, default=None, help="Filter: qso_date >= YYYYMMDD (inclusive)"
    )
    p.add_argument(
        "--until", type=str, default=None, help="Filter: qso_date <= YYYYMMDD (inclusive)"
    )
    p.add_argument(
        "--confirmed-only",
        action="store_true",
        help="Filter: only confirmed (eQSL or LoTW == 'Y')",
    )
    p.add_argument(
        "--contains-comment",
        type=str,
        default=None,
        help="Filter: substring match in comment (case-insensitive)",
    )


def build_convert_parser(prog: str | None = None) -> argparse.ArgumentParser:
    """_summary_

    Args:
        prog (str | None, optional): _description_. Defaults to None.

    Returns:
        argparse.ArgumentParser: _description_
    """
    p = argparse.ArgumentParser(
        prog=prog or "convert",
        description="Convert ADIF (.adi) to QsoRecord JSON/NDJSON (streaming) "
        "with provenance.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_convert_args(p)
    return p


# def main(argv: list[str] | None = None) -> int:
#     parser = build_convert_parser()
#     parser.parse_args(argv)

if __name__ == "__main__":
    main()
