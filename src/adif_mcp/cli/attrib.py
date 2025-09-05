"""Annotate NDJSON QSOs with persona-based callsign attribution by date."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

from .persona import _load_yaml, _persona_path, resolve_home  # reuse helpers


def _parse_iso(d: str) -> date:
    """_summary_

    Args:
        d (str): _description_

    Returns:
        date: _description_
    """
    y, m, d2 = d.split("-")
    return date(int(y), int(m), int(d2))


def _parse_yyyymmdd(d: str) -> date:
    """_summary_

    Args:
        d (str): _description_

    Returns:
        date: _description_
    """
    return date(int(d[0:4]), int(d[4:6]), int(d[6:8]))


def _ranges_from_persona(data: Dict[str, Any]) -> List[Tuple[str, date, Optional[date]]]:
    """Return [(callsign, start, end)] from persona YAML.

    Supports either:
      - single top-level {callsign, start, end}, or
      - 'ranges': [{callsign, start, end}, ...]
    """
    out: list[tuple[str, date, date | None]] = []
    rs = data.get("ranges")
    if isinstance(rs, list) and rs:
        for r in rs:
            cs = str((r or {}).get("callsign") or "").upper().strip()
            s = str((r or {}).get("start") or "").strip()
            e_val = str((r or {}).get("end") or "").strip()
            if not cs or not s:
                continue
            ds = _parse_iso(s)
            de = _parse_iso(e_val) if e_val else None
            out.append((cs, ds, de))
        return out

        cs = str(data.get("callsign") or "").upper().strip()

        s_val = data.get("start")
        e_val = data.get("end")
        s_str = str(s_val).strip() if s_val is not None else ""
        e_str = str(e_val).strip() if e_val is not None else ""

        if cs and s_str:
            out.append(
                (
                    cs,
                    _parse_iso(s_str),
                    _parse_iso(e_str) if e_str else None,
                )
            )
    return out


def _choose_callsign(ranges: list[tuple[str, date, date | None]], qso_d: date) -> str | None:
    """Pick the range whose [start, end] contains qso_d. If multiple match,
    choose the one with the latest start."""
    matches = []
    for cs, s, e in ranges:
        if qso_d >= s and (e is None or qso_d <= e):
            matches.append((s, cs))
    if not matches:
        return None
    matches.sort(key=lambda t: t[0], reverse=True)
    return matches[0][1]


def _iter_ndjson(path: Path) -> Iterable[Dict[str, Any]]:
    """_summary_

    Args:
        path (Path): _description_

    Returns:
        Iterable[Dict[str, Any]]: _description_

    Yields:
        Iterator[Iterable[Dict[str, Any]]]: _description_
    """
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield cast(Dict[str, Any], json.loads(line))


def cmd_attrib(args: argparse.Namespace) -> int:
    """_summary_

    Args:
        args (argparse.Namespace): _description_

    Returns:
        int: _description_
    """
    home = resolve_home(args.home)
    ppath = _persona_path(home, args.persona)
    pdata = _load_yaml(ppath)
    if not pdata:
        print(f"Persona '{args.persona}' not found at {ppath}")
        return 1

    ranges = _ranges_from_persona(pdata)
    if not ranges:
        print(f"No callsign/date ranges defined for persona '{args.persona}'.")
        return 2

    ip = Path(args.input)
    op = Path(args.output)
    op.parent.mkdir(parents=True, exist_ok=True)

    count = done = 0
    with op.open("w", encoding="utf-8") as outf:
        for rec in _iter_ndjson(ip):
            count += 1
            qd = str(rec.get("qso_date") or "")
            try:
                qd_dt = _parse_yyyymmdd(qd)
            except Exception:
                # cannot attribute without a date
                rec["_attrib"] = {
                    "persona": args.persona,
                    "callsign": None,
                    "source": "none",
                    "note": "missing_or_invalid_qso_date",
                }
                print(json.dumps(rec), file=outf)
                continue

            cs = _choose_callsign(ranges, qd_dt)
            if cs:
                if args.force_overwrite or not rec.get("station_call"):
                    rec["station_call"] = cs
                rec["_attrib"] = {
                    "persona": args.persona,
                    "callsign": cs,
                    "source": "range",
                }
            else:
                # no range matched; preserve record station_call if any
                rec["_attrib"] = {
                    "persona": args.persona,
                    "callsign": rec.get("station_call"),
                    "source": "record" if rec.get("station_call") else "none",
                }

            print(json.dumps(rec), file=outf)
            done += 1

    if args.stats:
        print(f"attributed={done} total={count} → {op}")
    return 0


def register_cli(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """_summary_

    Args:
        subparsers (argparse._SubParsersAction[argparse.ArgumentParser]): _description_
    """
    p = subparsers.add_parser(
        "attrib",
        help="Annotate NDJSON with persona-based callsign attribution.",
        description=(
            "Map each QSO to a callsign from persona date ranges. Operates on local NDJSON."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--home", help="Override SSOT home directory.")
    p.add_argument("--persona", required=True, help="Persona name with ranges")
    p.add_argument("-i", "--input", required=True, help="Input NDJSON path")
    p.add_argument("-o", "--output", required=True, help="Output NDJSON path")
    p.add_argument(
        "--force-overwrite",
        action="store_true",
        help="Overwrite station_call even if already set",
    )
    p.add_argument("--stats", action="store_true", help="Print summary stats")
    p.set_defaults(func=cmd_attrib)
