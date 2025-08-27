from __future__ import annotations

from typing import Annotated, Literal, Optional, List, Dict
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Literal, Optional

import click

# src/adif_mcp/models.py
# TODO: generate Mode/Band/QSLRcvd literals from ADIF 3.1.5 tables into adif_mcp.enums.

# ─────────────────────────────
# Reusable constrained aliases
# ─────────────────────────────

# Core strings
Callsign = Annotated[str, Field(min_length=3, max_length=20, regex=r"^[A-Z0-9/]{3,20}$")]
RST      = Annotated[str, Field(regex=r"^\d{2,3}[A-Z]?$")]
Grid     = Annotated[str, Field(max_length=8)]                       # Maidenhead (4/6/8)
ADIFDate = Annotated[str, Field(regex=r"^\d{8}$")]                   # YYYYMMDD
ADIFTime = Annotated[str, Field(regex=r"^\d{4}(\d{2})?$")]           # HHMM[SS]

# Numeric
FreqMHz  = Annotated[float, Field(gt=0)]
PowerW   = Annotated[float, Field(ge=0)]
SNRdB    = Annotated[float, Field(ge=-50, le=50)]                    # tweak later if needed

# Enums
Band = Literal["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","4m","2m","70cm","23cm"]
Mode = Literal["CW","SSB","AM","FM","RTTY","PSK31","FT8","FT4","JT65","JT9","MFSK","OLIVIA","OTHER"]
BoolFlag = Literal["Y","N"]
QSLRcvd  = Literal["Y","N","R","I","V","Q","E"]  # per ADIF

# ─────────────────────────────
# Models
# ─────────────────────────────

class QsoCore(BaseModel):
    """Minimal, safe QSO record (AI/validation friendly)."""
    station_call: Callsign = Field(..., description="Your station callsign")
    call:         Callsign = Field(..., description="Worked station callsign")
    qso_date:     ADIFDate
    time_on:      ADIFTime
    band:         Band
    mode:         Mode
    freq:         Optional[FreqMHz] = None           # MHz
    rst_sent:     Optional[RST] = None
    rst_rcvd:     Optional[RST] = None
    my_gridsquare: Optional[Grid] = None
    gridsquare:    Optional[Grid] = None
    tx_pwr:        Optional[PowerW] = None           # watts
    comment:       Optional[Annotated[str, Field(max_length=200)]] = None

    # Normalize case / whitespace where ADIF is case-insensitive by convention
    @validator("station_call", "call", pre=True)
    def _upper_calls(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip().upper()
        return v

    @validator("my_gridsquare", "gridsquare", pre=True)
    def _upper_grids(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip().upper()
        return v

class QslStatus(BaseModel):
    lotw_qsl_rcvd: Optional[QSLRcvd] = None
    eqsl_qsl_rcvd: Optional[QSLRcvd] = None
    lotw_qsl_date: Optional[ADIFDate] = None
    eqsl_qsl_date: Optional[ADIFDate] = None

class QsoRecord(QsoCore, QslStatus):
    adif_fields: Dict[str, str] = Field(
        default_factory=dict,
        description="Original ADIF name→value map (optional).",
    )

# ─────────────────────────────
# Batch I/O envelopes
# ─────────────────────────────

class ValidateRequest(BaseModel):
    records: List[Dict[str, str]]  # raw ADIF field dicts
    strict: bool = True

class ValidateResult(BaseModel):
    ok: bool
    errors: List[Dict[str, str]]               # {index, field, message}
    normalized: Optional[List[QsoRecord]] = None

class EnumList(BaseModel):
    modes: List[str]
    bands: List[str]
    qsl_rcvd: List[str]
