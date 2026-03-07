"""Annotate NDJSON QSOs with persona-based callsign attribution by date."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

from qso_graph_auth.identity.store import PersonaStore


def _parse_yyyymmdd(d: str) -> date:
    """Parse YYYYMMDD date string from QSO records."""
    return date(int(d[0:4]), int(d[4:6]), int(d[6:8]))


def _choose_callsign(
    ranges: list[tuple[str, date, date | None]], qso_d: date,
) -> str | None:
    """Pick the range whose [start, end] contains qso_d.

    If multiple match, choose the one with the latest start.
    """
    matches = []
    for cs, s, e in ranges:
        if qso_d >= s and (e is None or qso_d <= e):
            matches.append((s, cs))
    if not matches:
        return None
    matches.sort(key=lambda t: t[0], reverse=True)
    return matches[0][1]


def _iter_ndjson(path: Path) -> Iterable[Dict[str, Any]]:
    """Iterate over newline-delimited JSON records."""
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield cast(Dict[str, Any], json.loads(line))


def cmd_attrib(args: argparse.Namespace) -> int:
    """Annotate NDJSON QSOs with persona-based callsign attribution."""
    store = PersonaStore()
    p = store.get(args.persona)
    if not p:
        print(f"Persona '{args.persona}' not found")
        return 1

    # Build ranges from persona (single callsign/start/end)
    ranges: List[Tuple[str, date, Optional[date]]] = []
    if p.callsign and p.start:
        ranges.append((p.callsign, p.start, p.end))

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
    """Register the attrib subcommand."""
    p = subparsers.add_parser(
        "attrib",
        help="Annotate NDJSON with persona-based callsign attribution.",
        description=(
            "Map each QSO to a callsign from persona date ranges. "
            "Operates on local NDJSON."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
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
