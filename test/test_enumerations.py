"""Tests for enumeration listing, searching, and validation (v0.7.0)."""

import os
import re

from adif_mcp.mcp.server import (
    list_enumerations,
    search_enumerations,
    validate_adif_record,
)

_TEST_DATA = os.path.join(os.path.dirname(__file__), "data")

# --- list_enumerations ---


def test_list_enumerations_count() -> None:
    """Returns exactly 25 enumerations."""
    result = list_enumerations()
    assert result["enumeration_count"] == 25
    assert len(result["enumerations"]) == 25


def test_list_enumerations_has_mode() -> None:
    """Mode enumeration present with correct record count."""
    result = list_enumerations()
    mode = result["enumerations"]["Mode"]
    assert mode["record_count"] == 90
    assert mode["import_only_count"] == 42
    assert "Mode" in mode["searchable_fields"]


def test_list_enumerations_has_band() -> None:
    """Band enumeration present with 33 records."""
    result = list_enumerations()
    band = result["enumerations"]["Band"]
    assert band["record_count"] == 33
    assert band["import_only_count"] == 0


# --- search_enumerations ---


def test_search_mode_ft8() -> None:
    """Find FT8 in Mode enumeration."""
    result = search_enumerations("FT8", enumeration="Mode")
    assert "results" in result
    mode_results = result["results"]["Mode"]
    assert mode_results["match_count"] >= 1
    found_modes = [
        rec.get("Mode") for rec in mode_results["records"].values()
    ]
    assert "FT8" in found_modes


def test_search_band_20m() -> None:
    """Find 20m in Band enumeration."""
    result = search_enumerations("20m", enumeration="Band")
    assert "results" in result
    band_results = result["results"]["Band"]
    found_bands = [
        rec.get("Band") for rec in band_results["records"].values()
    ]
    assert "20m" in found_bands


def test_search_dxcc_entity() -> None:
    """Find United States in DXCC_Entity_Code."""
    result = search_enumerations(
        "United States", enumeration="DXCC_Entity_Code"
    )
    assert "results" in result
    assert "DXCC_Entity_Code" in result["results"]


def test_search_contest_cq_ww() -> None:
    """Find CQ-WW in Contest_ID."""
    result = search_enumerations("CQ-WW", enumeration="Contest_ID")
    assert "results" in result
    assert result["results"]["Contest_ID"]["match_count"] >= 1


def test_search_all_enums() -> None:
    """Search without filter hits multiple enumerations."""
    result = search_enumerations("CW")
    assert "results" in result
    # CW appears in Mode and possibly Submode
    assert result["enumerations_matched"] >= 1


def test_search_specific_enum() -> None:
    """Search with filter returns only that enumeration."""
    result = search_enumerations("CW", enumeration="Mode")
    assert "results" in result
    assert list(result["results"].keys()) == ["Mode"]


def test_search_case_insensitive() -> None:
    """Lowercase 'ft8' finds FT8."""
    result = search_enumerations("ft8", enumeration="Mode")
    assert "results" in result
    found_modes = [
        rec.get("Mode")
        for rec in result["results"]["Mode"]["records"].values()
    ]
    assert "FT8" in found_modes


def test_search_not_found() -> None:
    """Returns not-found message for nonexistent term."""
    result = search_enumerations("ZZZZNOTREAL")
    assert "message" in result
    assert "not found" in result["message"]


def test_search_invalid_enum() -> None:
    """Returns error for invalid enumeration name."""
    result = search_enumerations("CW", enumeration="FakeEnum")
    assert "error" in result
    assert "Unknown enumeration" in result["error"]


# --- validate_adif_record (enumeration validation) ---


def test_validate_valid_mode() -> None:
    """MODE=CW passes validation."""
    adif = "<MODE:2>CW<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_invalid_mode() -> None:
    """MODE=INVALID produces an error."""
    adif = "<MODE:7>INVALID<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("MODE" in e and "INVALID" in e for e in result["errors"])


def test_validate_valid_band() -> None:
    """BAND=20m passes validation."""
    adif = "<BAND:3>20m<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_invalid_band() -> None:
    """BAND=25m produces an error."""
    adif = "<BAND:3>25m<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("BAND" in e and "25m" in e for e in result["errors"])


def test_validate_import_only_warns() -> None:
    """Import-only MODE value produces warning, not error."""
    # AMTORFEC is import-only in the Mode enumeration
    adif = "<MODE:8>AMTORFEC<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert any("import-only" in w for w in result["warnings"])
    assert not result["errors"]


def test_validate_compound_credit() -> None:
    """CREDIT_SUBMITTED with valid Credit:Medium value passes."""
    # DXCC:CARD is a valid Credit:QSL_Medium pair
    adif = "<CREDIT_SUBMITTED:9>DXCC:CARD<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_compound_credit_plain() -> None:
    """CREDIT_SUBMITTED with plain credit name (no medium) passes."""
    adif = "<CREDIT_SUBMITTED:4>DXCC<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_compound_bad() -> None:
    """CREDIT_SUBMITTED with invalid credit name errors."""
    adif = "<CREDIT_SUBMITTED:9>FAKE:CARD<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("CREDIT_SUBMITTED" in e for e in result["errors"])


def test_validate_submode_match() -> None:
    """SUBMODE=USB with MODE=SSB passes without warning."""
    adif = "<MODE:3>SSB<SUBMODE:3>USB<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]
    # No submode mismatch warning
    submode_warns = [w for w in result["warnings"] if "submode" in w.lower()]
    assert not submode_warns


def test_validate_submode_mismatch() -> None:
    """SUBMODE=USB with MODE=CW produces warning."""
    adif = "<MODE:2>CW<SUBMODE:3>USB<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"  # warning, not error
    assert any("submode" in w.lower() and "USB" in w for w in result["warnings"])


def test_validate_dxcc_valid() -> None:
    """DXCC=291 (United States) passes."""
    adif = "<DXCC:3>291<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_continent() -> None:
    """CONT=NA passes."""
    adif = "<CONT:2>NA<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_case_insensitive() -> None:
    """MODE=cw (lowercase) passes validation."""
    adif = "<MODE:2>cw<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_number_unchanged() -> None:
    """Existing Number validation still works."""
    adif = "<AGE:3>abc<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("AGE" in e and "Number" in e for e in result["errors"])


def test_validate_empty_mode_errors() -> None:
    """Empty MODE value produces an error (Patton finding #2)."""
    adif = "<MODE:0><EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("MODE" in e and "empty" in e for e in result["errors"])


def test_validate_whitespace_band_errors() -> None:
    """Whitespace-only BAND value produces an error (Patton finding #2)."""
    adif = "<BAND:1> <EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("BAND" in e and "empty" in e for e in result["errors"])


# --- Official ADIF 3.1.6 Test File (G3ZOD / adif.org.uk) ---


def test_official_adif_test_file_zero_errors() -> None:
    """ADIF-TCR-001: Zero false errors on official 3.1.6 test corpus.

    Source: https://adif.org.uk/316/resources
    Generator: CreateADIFTestFiles (G3ZOD)
    Records: 6,191 QSOs exercising every enumeration value
    Gate: If our validator rejects an official record, our validator is wrong.
    """
    test_file = os.path.join(
        _TEST_DATA, "ADIF_316_test_QSOs_2025_08_27.adi"
    )
    if not os.path.exists(test_file):
        return  # Skip if test file not present (CI without data)

    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r"<EOH>", content, flags=re.IGNORECASE)
    body = parts[1]
    records = re.findall(r"(.*?<EOR>)", body, re.IGNORECASE | re.DOTALL)

    assert len(records) == 6191, f"Expected 6191 records, got {len(records)}"

    all_errors = []
    for i, rec_text in enumerate(records):
        result = validate_adif_record(rec_text.strip())
        for err in result.get("errors", []):
            all_errors.append(f"Record {i + 1}: {err}")

    assert len(all_errors) == 0, (
        f"{len(all_errors)} false errors on official test file:\n"
        + "\n".join(all_errors[:20])
    )


def test_official_adif_test_file_warning_categories() -> None:
    """ADIF-TCR-002: Warnings on official test file are all legitimate.

    Expected warning categories:
    - user/app-defined fields (USERDEF, APP_ prefixed) — not in fields spec
    - import-only values — valid but obsolete enum values
    Both are correct validator behavior, not false positives.
    """
    test_file = os.path.join(
        _TEST_DATA, "ADIF_316_test_QSOs_2025_08_27.adi"
    )
    if not os.path.exists(test_file):
        return

    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r"<EOH>", content, flags=re.IGNORECASE)
    body = parts[1]
    records = re.findall(r"(.*?<EOR>)", body, re.IGNORECASE | re.DOTALL)

    total_warnings = 0
    for rec_text in records:
        result = validate_adif_record(rec_text.strip())
        for w in result.get("warnings", []):
            total_warnings += 1
            # Every warning must be one of these legitimate categories
            assert (
                "not in spec" in w
                or "import-only" in w
                or "submode" in w.lower()
            ), f"Unexpected warning type: {w}"

    # Expect ~39 warnings (23 user-defined + 16 import-only)
    assert 30 <= total_warnings <= 50, (
        f"Expected ~39 warnings, got {total_warnings}"
    )
