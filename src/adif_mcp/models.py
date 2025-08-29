"""Pydantic models & constrained types for ADIF MCP core.

These models define a safe, minimal record shape used for validation and
normalization of ADIF-style QSO data, plus small batch I/O envelopes.
"""

from __future__ import annotations

import re
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, constr, validator
from typing_extensions import Annotated

_RST_RE = re.compile(r"^[1-5][1-9](?:[1-9])?$")  # R 1–5, S 1–9, optional T 1–9

# ---- Atomic field types (constrained) ----
Callsign = Annotated[str, Field(strip_whitespace=True, min_length=3, max_length=20)]
Band = Literal[
    "160m",
    "80m",
    "60m",
    "40m",
    "30m",
    "20m",
    "17m",
    "15m",
    "12m",
    "10m",
    "6m",
    "4m",
    "2m",
    "70cm",
    "23cm",
]
Mode = Literal[
    "CW",
    "SSB",
    "AM",
    "FM",
    "RTTY",
    "PSK31",
    "FT8",
    "FT4",
    "JT65",
    "JT9",
    "MFSK",
    "OLIVIA",
    "OTHER",
]
RST = constr(regex=r"^[1-5][1-9](?:[1-9])?$")
BoolFlag = Literal["Y", "N"]
QSLRcvd = Literal["Y", "N", "R", "I", "V", "Q", "E"]


class QsoCore(BaseModel):
    """QSO Base Model that includes:
    station_call    `str`
    qso_date        `str`
    time_on         `str`
    band            `str`
    mode            `str`
    freq            `float`
    rst_sent        `int`
    ret_rcvd        `int`
    my_gridsquare   `str`
    tx_power        `float`
    comment         1str`
    """

    station_call: Callsign
    call: Callsign
    qso_date: Annotated[str, Field(regex=r"^\d{8}$")]  # YYYYMMDD
    time_on: Annotated[str, Field(regex=r"^\d{4}(\d{2})?$")]  # HHMM[SS]
    band: Band
    mode: Mode
    freq: Optional[Annotated[float, Field(gt=0)]] = None  # MHz
    rst_sent: Optional[str] = None
    rst_rcvd: Optional[str] = None
    my_gridsquare: Optional[Annotated[str, Field(max_length=8)]] = None
    gridsquare: Optional[Annotated[str, Field(max_length=8)]] = None
    tx_pwr: Optional[Annotated[float, Field(ge=0)]] = None  # watts
    comment: Optional[Annotated[str, Field(max_length=200)]] = None

    @validator("rst_sent", "rst_rcvd")
    def _validate_rst(cls, v: Optional[str]) -> Optional[str]:
        """Validation of sent and recieved RSTs"""
        if v is None:
            return v
        if not _RST_RE.match(v):
            raise ValueError(f"Invalid RST: {v!r}")
        return v


class QslStatus(BaseModel):
    """QSO Status for lotw qsl received and the dates"""

    lotw_qsl_rcvd: Optional[QSLRcvd] = None
    eqsl_qsl_rcvd: Optional[QSLRcvd] = None
    lotw_qsl_date: Optional[Annotated[str, Field(regex=r"^\d{8}$")]] = None
    eqsl_qsl_date: Optional[Annotated[str, Field(regex=r"^\d{8}$")]] = None


class QsoRecord(QsoCore, QslStatus):
    """Normalized QSO record that merges core ADIF fields with QSL status.

    `adif_fields` preserves the original name→value map for round-tripping.
    """

    adif_fields: Dict[str, str] = Field(
        default_factory=dict,
        description="Original ADIF name→value map (optional).",
    )


class ValidateRequest(BaseModel):
    """Batch validation request wrapper."""

    records: List[Dict[str, str]]  # raw ADIF field dicts (pre-model)
    strict: bool = True


class ValidateResult(BaseModel):
    """Batch validation result wrapper."""

    ok: bool
    errors: List[Dict[str, str]]  # {index, field, message}
    normalized: Optional[List[QsoRecord]] = None  # present if ok


class EnumList(BaseModel):
    """Enumerations exposed by the MCP (for UI drop-downs / validation)."""

    modes: List[str]
    bands: List[str]
    qsl_rcvd: List[str]
