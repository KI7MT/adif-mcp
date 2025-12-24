"""Unit tests for the ADIF-MCP server entry point."""

from datetime import date, time

import pytest

from adif_mcp.models import QSO
from adif_mcp.server import (
    calculate_distance_impl,
    calculate_heading_impl,
    clublog_query_impl,
    eqsl_query_impl,
    get_service_metadata_impl,
    lookup_country_impl,
    lotw_query_impl,
    normalize_band_impl,
    parse_adif_impl,
    qrz_query_impl,
    validate_qso_impl,
)


def test_get_service_metadata() -> None:
    """
    Verify get_service_metadata returns a dictionary.

    This ensures the tool handles both the presence and absence of
    the metadata file gracefully (returning content or an error dict).
    """
    result = get_service_metadata_impl()
    assert isinstance(result, dict)


def test_validate_qso() -> None:
    """
    Verify validate_qso accepts a QSO object and returns its JSON representation.

    Also verifies that the Pydantic validators (uppercase) are applied
    before the tool processes the data.
    """
    input_qso = QSO(
        call="ki7mt",
        qso_date=date(2025, 1, 1),
        time_on=time(12, 0),
        band="20m",
        mode="cw",
        rst_sent="599",
    )

    result = validate_qso_impl(input_qso)

    assert result["call"] == "KI7MT"
    assert result["band"] == "20M"
    assert result["mode"] == "CW"
    assert result["qso_date"] == "2025-01-01"
    assert result["time_on"] == "12:00:00"


def test_calculate_distance() -> None:
    """
    Verify calculate_distance returns a reasonable float for known grids.
    FN20 to FN21 is 1 degree latitude difference (~111 km).
    """
    # FN20 center: 40.5, -73.0
    # FN21 center: 41.5, -73.0
    dist = calculate_distance_impl("FN20", "FN21")
    assert 110.0 < dist < 112.0


def test_calculate_heading() -> None:
    """
    Verify calculate_heading returns a valid azimuth.
    FN20 (NY) to IO91 (London) should be roughly Northeast (~50-55 deg).
    """
    heading = calculate_heading_impl("FN20", "IO91")
    assert 45.0 < heading < 60.0


def test_normalize_band() -> None:
    """Verify normalize_band handles frequencies and strings correctly."""
    # Frequency to Band
    assert normalize_band_impl("14.074") == "20M"
    assert normalize_band_impl("7.030") == "40M"
    assert normalize_band_impl("50.313") == "6M"

    # String normalization
    assert normalize_band_impl("20m") == "20M"
    assert normalize_band_impl("40M") == "40M"


def test_parse_adif() -> None:
    """Verify parse_adif decodes a simple ADIF string."""
    adi = "<CALL:5>KI7MT<QSO_DATE:8>20250101<EOR>"
    recs = parse_adif_impl(adi)
    assert len(recs) == 1
    assert recs[0]["call"] == "KI7MT"
    assert recs[0]["qso_date"] == "20250101"


def test_eqsl_query() -> None:
    """Verify eqsl_query returns the expected stub structure."""
    result = eqsl_query_impl("KI7MT")
    assert "records" in result
    assert isinstance(result["records"], list)
    assert len(result["records"]) > 0


def test_lotw_query() -> None:
    """Verify lotw_query returns the expected stub structure."""
    result = lotw_query_impl("KI7MT")
    assert result["callsign"] == "KI7MT"
    assert result["qsls_count"] == 1234
    assert isinstance(result["dxcc_credits"], dict)


def test_clublog_query() -> None:
    """Verify clublog_query returns the expected stub structure."""
    result = clublog_query_impl("KI7MT")
    assert result["callsign"] == "KI7MT"
    assert result["dxcc_confirmed"] == 150
    assert "propagation_forecast" in result


def test_qrz_query() -> None:
    """Verify qrz_query returns the expected stub structure."""
    result = qrz_query_impl("KI7MT")
    assert result["callsign"] == "KI7MT"
    assert result["license_class"] == "Extra"
    assert "image_url" in result


def test_lookup_country() -> None:
    """Verify lookup_country identifies correct entities from the static map."""
    # Test 1-letter match
    k_ent = lookup_country_impl("KI7MT")
    assert k_ent.name == "United States"
    assert k_ent.continent == "NA"

    # Test 2-letter match
    ja_ent = lookup_country_impl("JA1ABC")
    assert ja_ent.name == "Japan"
    assert ja_ent.itu_zone == 45

    # Test unknown
    with pytest.raises(ValueError):
        lookup_country_impl("ZZ99")
