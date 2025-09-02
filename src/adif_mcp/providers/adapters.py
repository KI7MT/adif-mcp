"""Provider adapters: build minimal, safe GET requests for probes."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Tuple

from adif_mcp.identity import PersonaManager
from adif_mcp.providers import ProviderKey


def build_request(
    provider: ProviderKey, persona: str, pm: PersonaManager
) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    """Return (url, headers, query) for a GET-only probe for the given provider."""
    p = provider.lower()
    if p == "lotw":
        return _lotw_request(pm, persona)
    if p == "eqsl":
        return _eqsl_request(pm, persona)
    if p == "qrz":
        return _qrz_request(pm, persona)
    if p == "clublog":
        return _clublog_request(pm, persona)
    raise ValueError(f"Unknown provider: {provider!r}")


def _lotw_request(
    pm: PersonaManager, persona: str
) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    """LoTW: report endpoint with tomorrow’s date to keep body minimal."""
    username, secret = pm.require(persona, "lotw")
    qslsince = (date.today() + timedelta(days=1)).isoformat()
    url = "https://lotw.arrl.org/lotwuser/lotwreport.adi"
    headers: Dict[str, str] = {}
    query: Dict[str, Any] = {
        "login": username,
        "password": secret,
        "qso_query": 1,
        "qso_qslsince": qslsince,
    }
    return url, headers, query


def _eqsl_request(
    pm: PersonaManager, persona: str
) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    """eQSL: inbox download with today’s date for minimal response."""
    username, secret = pm.require(persona, "eqsl")
    rcvd_since = date.today().strftime("%Y%m%d")
    url = "https://www.eqsl.cc/qslcard/DownloadInBox.cfm"
    headers: Dict[str, str] = {}
    query: Dict[str, Any] = {
        "UserName": username,
        "Password": secret,
        "RcvdSince": rcvd_since,
    }
    return url, headers, query


def _qrz_request(
    pm: PersonaManager, persona: str
) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    """QRZ: XML login endpoint."""
    username, secret = pm.require(persona, "qrz")
    url = "https://xmldata.qrz.com/xml/current/"
    headers: Dict[str, str] = {}
    query: Dict[str, Any] = {
        "username": username,
        "password": secret,
        "agent": "adif-mcp",
    }
    return url, headers, query


def _clublog_request(
    pm: PersonaManager, persona: str
) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    """Club Log: logsearch JSON with future year to avoid heavy bodies."""
    _username, secret = pm.require(persona, "clublog")
    url = "https://clublog.org/logsearchjson.php"
    headers: Dict[str, str] = {}
    query: Dict[str, Any] = {
        "call": "G7VJR",
        "log": "G3TXF",
        "year": "2099",
        "api": secret,
    }
    return url, headers, query
