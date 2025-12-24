"""ADIF-MCP Server entry point."""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, cast

from fastmcp import FastMCP

from adif_mcp.models import QSO, Entity
from adif_mcp.parsers.adif_reader import parse_adi_text
from adif_mcp.tools.clublog_stub import fetch_status
from adif_mcp.tools.eqsl_stub import fetch_inbox
from adif_mcp.tools.lotw_stub import fetch_report
from adif_mcp.tools.qrz_stub import fetch_bio

# Initialize the FastMCP server as per Technical Bedrock
mcp = FastMCP("ADIF-MCP")


def get_service_metadata_impl() -> Dict[str, Any]:
    """
    Retrieves the ADIF-MCP service metadata, including supported features
    and ADIF specification version.
    """
    # Locate the metadata file relative to this module
    meta_path = Path(__file__).parent / "adif_meta.json"

    if not meta_path.exists():
        return {"error": "Metadata file not found", "path": str(meta_path)}

    with open(meta_path, "r") as f:
        return cast(Dict[str, Any], json.load(f))


@mcp.tool()
def get_service_metadata() -> Dict[str, Any]:
    """
    Retrieves the ADIF-MCP service metadata, including supported features
    and ADIF specification version.
    """
    return get_service_metadata_impl()


def validate_qso_impl(qso: QSO) -> Dict[str, Any]:
    """
    Validates a QSO record against the ADIF 3.1.5 schema.
    """
    return qso.model_dump(mode="json")


@mcp.tool()
def validate_qso(qso: QSO) -> Dict[str, Any]:
    """
    Validates a QSO record against the ADIF 3.1.5 schema.
    """
    return validate_qso_impl(qso)


def _to_latlon(locator: str) -> tuple[float, float]:
    """
    Decodes a Maidenhead locator to (latitude, longitude).
    Supports 4 or 6 character locators.
    Returns the center of the grid square.
    """
    locator = locator.strip().upper()
    if len(locator) < 4:
        raise ValueError("Locator must be at least 4 characters")

    # Field 1 (A-R)
    lon = (ord(locator[0]) - ord("A")) * 20.0 - 180.0
    lat = (ord(locator[1]) - ord("A")) * 10.0 - 90.0

    # Field 2 (0-9)
    lon += (ord(locator[2]) - ord("0")) * 2
    lat += (ord(locator[3]) - ord("0")) * 1

    # Field 3 (A-X) - optional
    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord("A")) * (5 / 60)
        lat += (ord(locator[5]) - ord("A")) * (2.5 / 60)
        # Center of 6-char subsquare
        lon += 2.5 / 60  # 5 min width / 2
        lat += 1.25 / 60  # 2.5 min height / 2
    else:
        # Center of 4-char square
        lon += 1.0  # 2 deg width / 2
        lat += 0.5  # 1 deg height / 2

    return lat, lon


def calculate_distance_impl(start: str, end: str) -> float:
    """
    Calculates the great-circle distance between two Maidenhead locators in kilometers.
    """
    lat1, lon1 = _to_latlon(start)
    lat2, lon2 = _to_latlon(end)

    R = 6371.0  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)


@mcp.tool()
def calculate_distance(start: str, end: str) -> float:
    """
    Calculates the great-circle distance between two Maidenhead locators in kilometers.
    """
    return calculate_distance_impl(start, end)


def calculate_heading_impl(start: str, end: str) -> float:
    """
    Calculates the initial beam heading (azimuth) from start to end in degrees.
    """
    lat1, lon1 = _to_latlon(start)
    lat2, lon2 = _to_latlon(end)

    # Convert to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)

    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)

    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360) % 360

    return round(bearing, 1)


@mcp.tool()
def calculate_heading(start: str, end: str) -> float:
    """
    Calculates the beam heading (azimuth) between two Maidenhead locators.
    """
    return calculate_heading_impl(start, end)


def normalize_band_impl(value: str) -> str:
    """
    Canonicalizes a band name or frequency string into a standard ADIF band enumeration.
    Returns Uppercase (e.g. '20M') to match the QSO model validators.
    """
    value = str(value).strip()

    # 1. Check if it's a frequency (float-like)
    try:
        freq = float(value)
        # Simple HF/VHF mapping (Primary allocations)
        if 1.8 <= freq <= 2.0:
            return "160M"
        if 3.5 <= freq <= 4.0:
            return "80M"
        if 7.0 <= freq <= 7.3:
            return "40M"
        if 10.1 <= freq <= 10.15:
            return "30M"
        if 14.0 <= freq <= 14.35:
            return "20M"
        if 18.068 <= freq <= 18.168:
            return "17M"
        if 21.0 <= freq <= 21.45:
            return "15M"
        if 24.89 <= freq <= 24.99:
            return "12M"
        if 28.0 <= freq <= 29.7:
            return "10M"
        if 50.0 <= freq <= 54.0:
            return "6M"
    except ValueError:
        pass  # Not a number, treat as band string

    # 2. Treat as band string
    # ADIF bands are case-insensitive, but our QSO model enforces Upper.
    # We assume valid input if it ends in M or CM.
    return value.upper()


@mcp.tool()
def normalize_band(value: str) -> str:
    """
    Canonicalizes a band name or frequency string into a standard ADIF band enumeration.
    """
    return normalize_band_impl(value)


def parse_adif_impl(adif_text: str) -> List[Dict[str, Any]]:
    """
    Parses raw ADIF text into a list of dictionaries.
    """
    # The parser returns List[Dict[str, str]], which satisfies List[Dict[str, Any]]
    return cast(List[Dict[str, Any]], parse_adi_text(adif_text))


@mcp.tool()
def parse_adif(adif_text: str) -> List[Dict[str, Any]]:
    """
    Parses raw .adi text blocks into structured, validated JSON records.
    """
    return parse_adif_impl(adif_text)


def eqsl_query_impl(callsign: str) -> Dict[str, Any]:
    """
    Queries eQSL.cc for card status and inbox analysis.
    """
    return fetch_inbox(callsign)


@mcp.tool()
def eqsl_query(callsign: str) -> Dict[str, Any]:
    """
    Queries eQSL.cc for card status and inbox analysis.
    """
    return eqsl_query_impl(callsign)


def lotw_query_impl(callsign: str) -> Dict[str, Any]:
    """
    Queries ARRL's Logbook of The World for QSL confirmations and award credits.
    """
    return cast(Dict[str, Any], fetch_report(callsign))


@mcp.tool()
def lotw_query(callsign: str) -> Dict[str, Any]:
    """
    Queries ARRL's Logbook of The World for QSL confirmations and award credits.
    """
    return lotw_query_impl(callsign)


def clublog_query_impl(callsign: str) -> Dict[str, Any]:
    """
    Queries ClubLog for DXCC status and propagation trends.
    """
    return cast(Dict[str, Any], fetch_status(callsign))


@mcp.tool()
def clublog_query(callsign: str) -> Dict[str, Any]:
    """
    Queries ClubLog for DXCC status and propagation trends.
    """
    return clublog_query_impl(callsign)


def qrz_query_impl(callsign: str) -> Dict[str, Any]:
    """
    Fetches extended operator bio and station data from QRZ.com.
    """
    return cast(Dict[str, Any], fetch_bio(callsign))


@mcp.tool()
def qrz_query(callsign: str) -> Dict[str, Any]:
    """
    Fetches extended operator bio and station data from QRZ.com.
    """
    return qrz_query_impl(callsign)


# Sovereign Data: Minimal prefix map for Smoke/MVP.
# In a full release, this would load from a cty.dat resource.
_PREFIX_MAP: Dict[str, Entity] = {
    "K": Entity(
        name="United States", primary_prefix="K", continent="NA", cq_zone=5, itu_zone=8
    ),
    "W": Entity(
        name="United States", primary_prefix="K", continent="NA", cq_zone=5, itu_zone=8
    ),
    "N": Entity(
        name="United States", primary_prefix="K", continent="NA", cq_zone=5, itu_zone=8
    ),
    "VE": Entity(name="Canada", primary_prefix="VE", continent="NA", cq_zone=5, itu_zone=9),
    "G": Entity(name="England", primary_prefix="G", continent="EU", cq_zone=14, itu_zone=27),
    "JA": Entity(name="Japan", primary_prefix="JA", continent="AS", cq_zone=25, itu_zone=45),
    "VK": Entity(
        name="Australia", primary_prefix="VK", continent="OC", cq_zone=30, itu_zone=59
    ),
}


def lookup_country_impl(callsign: str) -> Entity:
    """
    Identifies the DXCC entity for a given callsign using a local prefix map.
    """
    call = callsign.strip().upper()

    # Simple longest-match strategy for the MVP
    # 1. Try 2-letter prefix
    if len(call) >= 2:
        prefix_2 = call[:2]
        if prefix_2 in _PREFIX_MAP:
            return _PREFIX_MAP[prefix_2]

    # 2. Try 1-letter prefix
    if len(call) >= 1:
        prefix_1 = call[:1]
        if prefix_1 in _PREFIX_MAP:
            return _PREFIX_MAP[prefix_1]

    raise ValueError(f"No entity found for callsign: {callsign}")


@mcp.tool()
def lookup_country(callsign: str) -> Dict[str, Any]:
    """
    Identifies the DXCC entity for a given callsign.
    """
    entity = lookup_country_impl(callsign)
    return entity.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
