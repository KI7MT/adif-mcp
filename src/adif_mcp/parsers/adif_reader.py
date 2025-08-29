"""
Tiny, dependency-free ADIF (.adi) reader.

- Understands the core ADIF tag form: <FIELD[:len][:type]>value
- Records are separated by <EOR>
- Field/tag names are treated case-insensitively
- Returns a list[QSORecord] (a TypedDict), with basic normalization:
    * "station_callsign" -> "station_call"
    * keys are lower_snake_case
    * common fields available when present: call, station_call, band,
      mode, qso_date, time_on, time_off, rst_rcvd, rst_sent, freq
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, TypedDict, cast

__all__ = ["QSORecord", "parse_adi_text", "parse_adi_file"]


class QSORecord(TypedDict, total=False):
    """A single QSO in normalized, lower_snake_case key form."""

    call: str
    station_call: str  # normalized from station_callsign
    band: str
    mode: str
    qso_date: str  # YYYYMMDD per ADIF
    time_on: str  # HHMM[SS]
    time_off: str  # HHMM[SS]
    rst_rcvd: str
    rst_sent: str
    freq: str
    # Other keys may be present at runtime (TypedDict total=False).


_TAG_RE = re.compile(
    r"""
    <                             # opening
    (?P<tag>[A-Za-z0-9_]+)        # tag name
    (?: : (?P<len>\d+) )?         # optional :length
    (?: : (?P<typ>[A-Za-z0-9]+) )? # optional :type (unused here)
    >                             # closing
    """,
    re.VERBOSE,
)

_EOR = "EOR"  # end-of-record marker


def _to_snake(name: str) -> str:
    """
    Converts `str `name` to str lower case
    """
    return name.strip().lower()


def _normalize_key(k: str) -> str:
    """Map ADIF field names to the normalized keys we use."""
    k = _to_snake(k)
    if k == "station_callsign":
        return "station_call"
    return k


@dataclass
class _Token:
    """Internal representation of a parsed ADIF field token.

    A token marks a single ADIF field definition found in the raw
    text stream. It records the tag name, optional declared length,
    and character offsets for locating the field within the input.

    Attributes:
        tag: The ADIF field name (e.g., "CALL", "BAND").
        length: Optional explicit field length if given (e.g., <CALL:5>).
        start: Index in the input string where this token begins.
        end: Index just after the closing '>' of the token.
    """

    tag: str
    length: Optional[int]
    start: int
    end: int  # index just after the '>'


def _scan_tokens(s: str) -> Iterator[_Token]:
    """Scan a raw ADIF string and yield field tokens.

    This function iterates through the input text and locates ADIF
    field definitions using the compiled tag regex. Each match is
    converted into an internal `_Token` that captures the tag name,
    optional field length, and character positions.

    Args:
        s: Raw ADIF text containing one or more <TAG:len> definitions.

    Yields:
        _Token objects for each ADIF field found in the input.
    """
    for m in _TAG_RE.finditer(s):
        length = m.group("len")
        yield _Token(
            tag=m.group("tag").upper(),
            length=int(length) if length is not None else None,
            start=m.start(),
            end=m.end(),
        )


def parse_adi_text(text: str) -> List[QSORecord]:
    """
    Parse ADIF text into a list of QSORecord dicts.

    Parameters
    ----------
    text:
        Full contents of a .adi file (header + records).

    Returns
    -------
    list[QSORecord]
    """
    # Build raw dictionaries first (easier for TypedDict constraints).
    records_raw: List[Dict[str, str]] = []
    cur: Dict[str, str] = {}

    tokens = list(_scan_tokens(text))
    for i, tok in enumerate(tokens):
        tag = tok.tag
        next_start = tokens[i + 1].start if i + 1 < len(tokens) else len(text)

        if tok.length is not None:
            val = text[tok.end : tok.end + tok.length]
        else:
            val = text[tok.end : next_start]

        val = val.strip()

        if tag == _EOR:
            if cur:
                records_raw.append(cur)
                cur = {}
            continue

        key = _normalize_key(tag)
        if val != "":
            cur[key] = val

    if cur:
        records_raw.append(cur)

    return [record_as_qso(r) for r in records_raw]


def parse_adi_file(path: str | Path, encoding: str = "utf-8") -> List[QSORecord]:
    """
    Read and parse an ADIF (.adi) file.

    Parameters
    ----------
    path:
        File path to the ADIF text.
    encoding:
        Text encoding. ADIF files are commonly UTF-8; change if needed.
    """
    p = Path(path)
    data = p.read_text(encoding=encoding, errors="replace")
    return parse_adi_text(data)


def record_as_qso(d: Dict[str, str]) -> QSORecord:
    """
    Convert a raw parsed dict to a QSORecord.

    - Normalizes ADIF field names to lower_snake_case.
    - Uppercases callsigns (`call`, `station_call`) if present.
    - Drops keys not declared in `QSORecord` (keeps the record schema-tight).
    """
    # Normalize keys first
    tmp: Dict[str, str] = {_normalize_key(k): v for k, v in d.items()}

    # Keep only fields that exist on the TypedDict schema
    allowed = set(QSORecord.__annotations__.keys())
    filtered = {k: v for k, v in tmp.items() if k in allowed}

    # Normalize callsigns to uppercase (if present)
    for key in ("call", "station_call"):
        if key in filtered and isinstance(filtered[key], str):
            filtered[key] = filtered[key].upper()

    return cast(QSORecord, filtered)
