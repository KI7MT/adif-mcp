# src/adif_mcp/models.py
# TODO: generate Mode/Band/QSLRcvd literals from ADIF 3.1.5 tables into adif_mcp.enums.
from pydantic import BaseModel, Field, constr, conint, confloat
from typing import Literal, Optional, List, Dict

# ---- Atomic field types (constrained) ----
Callsign = constr(strip_whitespace=True, to_upper=True, min_length=3, max_length=20)
Band = Literal["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","4m","2m","70cm","23cm"]
Mode = Literal["CW","SSB","AM","FM","RTTY","PSK31","FT8","FT4","JT65","JT9","MFSK","OLIVIA","OTHER"]  # (generated later)
RST = constr(regex=r"^\d{2,3}[A-Z]?$")  # simplistic; refine later
BoolFlag = Literal["Y","N"]              # ADIF convention
QSLRcvd = Literal["Y","N","R","I","V","Q","E"]  # ADIF enum; refine later

# ---- A minimal, safe QSO “core” record used by tools ----
class QsoCore(BaseModel):
    station_call: Callsign = Field(..., description="Your station")
    call: Callsign = Field(..., description="Worked station")
    qso_date: constr(regex=r"^\d{8}$")  # YYYYMMDD
    time_on: constr(regex=r"^\d{4}(\d{2})?$")  # HHMM[SS]
    band: Band
    mode: Mode
    freq: Optional[confloat(gt=0)] = None  # MHz
    rst_sent: Optional[RST] = None
    rst_rcvd: Optional[RST] = None
    my_gridsquare: Optional[constr(max_length=8)] = None
    gridsquare: Optional[constr(max_length=8)] = None
    tx_pwr: Optional[confloat(ge=0)] = None  # watts
    comment: Optional[constr(max_length=200)] = None

class QslStatus(BaseModel):
    lotw_qsl_rcvd: Optional[QSLRcvd] = None
    eqsl_qsl_rcvd: Optional[QSLRcvd] = None
    lotw_qsl_date: Optional[constr(regex=r"^\d{8}$")] = None
    eqsl_qsl_date: Optional[constr(regex=r"^\d{8}$")] = None

class QsoRecord(QsoCore, QslStatus):
    adif_fields: Dict[str, str] = Field(default_factory=dict, description="Original ADIF name→value map (optional).")

# ---- Batch I/O envelopes ----
class ValidateRequest(BaseModel):
    records: List[Dict[str, str]]  # raw ADIF field dicts (pre-model)
    strict: bool = True

class ValidateResult(BaseModel):
    ok: bool
    errors: List[Dict[str, str]]  # {index, field, message}
    normalized: Optional[List[QsoRecord]] = None  # present if ok

class EnumList(BaseModel):
    modes: List[str]
    bands: List[str]
    qsl_rcvd: List[str]
