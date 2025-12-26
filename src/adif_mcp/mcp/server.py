"""ADIF-MCP Server: Authoritative 3.1.6 Specification Server."""

import json
from importlib import resources
from typing import Any, Dict, List, cast

from mcp.server.fastmcp import FastMCP

import adif_mcp
from adif_mcp.parsers.adif_reader import parse_adi_text
from adif_mcp.utils.geography import calculate_distance_impl, calculate_heading_impl

# Initialize the FastMCP server
mcp = FastMCP("ADIF-MCP")


# --- Helper Logic for Versioned Resources ---


import os

def get_spec_text(filename: str, version: str = "316") -> str:
    """
    Directly reads JSON files from the disk to avoid 'module not found' crashes.
    """
    # 1. Get the path to where this server.py file is sitting
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Build the path to your 316 folder
    # Path: /src/adif_mcp/mcp/server.py -> ../resources/spec/316
    json_dir = os.path.abspath(os.path.join(current_dir, "..", "resources", "spec", "316"))

    name = filename.lower().strip()

    # 3. List of files to check in order of priority
    targets = [
        os.path.join(json_dir, f"enumerations_{name}.json"),
        os.path.join(json_dir, f"{name}.json"),
        os.path.join(json_dir, "all.json")
    ]

    for target_path in targets:
        if os.path.exists(target_path):
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                continue

    # If nothing works, return a JSON string so the parser doesn't break
    return json.dumps({"error": f"Resource {name} not found in {json_dir}"})


# --- MCP Resources (The "Contract") ---


@mcp.resource("adif://system/version")
async def get_system_version() -> str:
    """Provides the current service and ADIF specification versions."""
    return json.dumps(
        {
            "service_version": adif_mcp.__version__,
            "adif_spec_version": adif_mcp.__adif_spec__,
            "status": "online",
        }
    )


@mcp.resource("adif://spec/316/all")
async def get_all_spec() -> str:
    """Provides the ADIF 3.1.6 Master Specification."""
    return get_spec_text("all")


@mcp.resource("adif://spec/316/fields")
async def get_fields_spec() -> str:
    """Provides the ADIF 3.1.6 Field Definitions."""
    return get_spec_text("fields")


@mcp.resource("adif://spec/316/enumerations")
async def get_enums_spec() -> str:
    """Provides the ADIF 3.1.6 Enumerations."""
    return get_spec_text("enumerations")


@mcp.resource("adif://spec/catalog")
async def get_catalog_resource() -> str:
    """Provides the ADIF Field Catalog."""
    res = resources.files("adif_mcp.resources.spec")
    cat_path = res.joinpath("adif_catalog.json")
    return cat_path.read_text()


# --- Core Validation & Utility Tools ---


@mcp.tool()
def get_version_info() -> Dict[str, Any]:
    """Returns the version of the ADIF-MCP server and the ADIF spec it supports."""
    return {
        "service_version": adif_mcp.__version__,
        "adif_spec_version": adif_mcp.__adif_spec__,
    }


@mcp.tool()
def get_service_metadata() -> Dict[str, Any]:
    """Retrieves ADIF-MCP metadata, including the 3.1.6 spec status."""
    res = resources.files("adif_mcp.resources.spec")
    meta_path = res.joinpath("adif_meta.json")
    with open(str(meta_path), "r") as f:
        return cast(Dict[str, Any], json.load(f))


@mcp.tool()
def read_specification_resource(resource_name: str) -> str:
    """
    Reads a specific ADIF 3.1.6 specification resource.
    Now supports modular files like 'mode', 'band', and 'submode'.
    """
    # Special case for the root catalog which sits one level up
    if resource_name.lower() == "catalog":
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cat_path = os.path.join(current_dir, "..", "resources", "spec", "adif_catalog.json")
        if os.path.exists(cat_path):
            with open(cat_path, 'r', encoding='utf-8') as f:
                return f.read()

    # Everything else (mode, band, fields, etc.) goes through the smart path logic
    return get_spec_text(resource_name)

@mcp.tool()
def search_enumerations(search_term: str) -> Dict[str, Any]:
    """
    Surgically searches local enumeration files using the 3.1.6 Records format.
    """
    target = "primary_administrative_subdivision"
    raw_data = get_spec_text(target)

    try:
        data = json.loads(raw_data)

        # 1. Surgical Drill-down to the Records object
        # Structure: Adif -> Enumerations -> Primary_Administrative_Subdivision -> Records
        if isinstance(data, dict):
            if "Adif" in data: data = data["Adif"]
            if "Enumerations" in data: data = data["Enumerations"]

            # Handle the specific case-sensitive key from your JSON
            sub_key = "Primary_Administrative_Subdivision"
            if sub_key in data:
                data = data[sub_key]

            if isinstance(data, dict) and "Records" in data:
                data = data["Records"]

        results = {}
        term = search_term.upper().strip()

        # 2. Search within the Records (where keys are like "NS.1", "AL.291", etc.)
        if isinstance(data, dict):
            for rec_id, fields in data.items():
                # Check the ID (e.g., "AL.291") or the internal "Code" (e.g., "AL")
                code = str(fields.get("Code", "")).upper()
                name = str(fields.get("Primary Administrative Subdivision", "")).upper()

                if term == code or term in name:
                    results[rec_id] = fields

        return results if results else {"message": f"'{search_term}' not found in local records."}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


@mcp.tool()
def list_enumeration_groups() -> List[str]:
    """Returns a list of all available ADIF 3.1.6 enumeration group names."""
    raw_data = get_spec_text("enumerations")
    data = json.loads(raw_data)

    # Unwrap if there's a top-level "Adif" key
    if "Adif" in data and len(data) == 1:
        data = data["Adif"]

    return sorted(list(data.keys()))

@mcp.tool()
def search_adif_spec(search_term: str) -> Dict[str, Any]:
    """
    Searches across ALL ADIF 3.1.6 spec files (fields, datatypes, enumerations).
    Returns matches found in any file.
    """
    results = {}
    term = search_term.upper()
    files_to_search = ["fields", "datatypes", "enumerations"]

    for file_key in files_to_search:
        try:
            data = json.loads(get_spec_text(file_key))
            # Surgical search within this specific JSON structure
            for key, value in data.items():
                # Check if the key matches or if the term is in the description/values
                str_val = str(value).upper()
                if term in key.upper() or term in str_val:
                    # Return just the relevant object, truncated if too long
                    results[f"{file_key} -> {key}"] = str(value)[:500]
        except Exception:
            continue

    return results if results else {"message": f"'{search_term}' not found in any 3.1.6 resource."}


@mcp.tool()
def get_enumeration_values(group_name: str) -> List[str]:
    """Returns the values for a specific group, handling nested 'Adif' keys."""
    raw_data = get_spec_text("enumerations")
    data = json.loads(raw_data)

    if "Adif" in data and len(data) == 1:
        data = data["Adif"]

    # Case-insensitive lookup
    for key in data.keys():
        if key.lower() == group_name.lower():
            return data[key]

    return [f"Group '{group_name}' not found. Available: {list(data.keys())[:5]}..."]


@mcp.tool()
def validate_adif_record(adif_string: str) -> Dict[str, Any]:
    """
    Parses and validates a single ADIF record against 3.1.6 rules.
    Reports if fields exist and if values match their Data Types.
    """
    # 1. Parse the record using your existing logic
    parsed = parse_adif_internal(adif_string) # Call your internal parser logic

    # 2. Load the Master Spec
    fields_spec = json.loads(get_spec_text("fields"))["Adif"]["Fields"]["Records"]

    report = {"status": "success", "errors": [], "warnings": [], "record": parsed}

    for field_name, value in parsed.items():
        upper_field = field_name.upper()

        # Check if field exists in 3.1.6
        if upper_field not in fields_spec:
            report["warnings"].append(f"Field '{upper_field}' is not in the ADIF 3.1.6 spec.")
            continue

        # Check Data Type (e.g., is a Number actually a number?)
        spec_info = fields_spec[upper_field]
        data_type = spec_info.get("Data Type")

        if data_type == "Number" and not is_numeric(value):
            report["errors"].append(f"Field '{upper_field}' expects a Number, got '{value}'.")
            report["status"] = "invalid"

    return report

@mcp.tool()
def calculate_distance(start: str, end: str) -> float:
    """Calculates great-circle distance (km) between Maidenhead locators."""
    return calculate_distance_impl(start, end)


@mcp.tool()
def calculate_heading(start: str, end: str) -> float:
    """Calculates initial beam heading (azimuth) between Maidenhead locators."""
    return calculate_heading_impl(start, end)

@mcp.tool()
def parse_adif(adif_text: str) -> List[Dict[str, Any]]:
    """
    The main tool Claude calls. Handles multiple records
    by splitting on <EOR> and calling the internal parser for each.
    """
    records = adif_text.split("<EOR>")
    parsed_results = []

    for r in records:
        if r.strip():
            # Use the internal function to do the heavy lifting
            data = parse_adif_internal(r)
            if data:
                parsed_results.append(data)

    return parsed_results


def parse_adif_internal(text: str) -> Dict[str, str]:
    # Use a regex that captures the tag AND the data regardless of content
    # pattern: <FIELD_NAME:LENGTH>DATA
    import re
    pattern = re.compile(r"<(?P<name>[^:>]+):(?P<len>\d+)(?::(?P<type>[^>]+))?>(?P<data>.{0,})", re.IGNORECASE | re.DOTALL)

    results = {}
    # Split by <EOR> or just process the whole string for tags
    tags = re.finditer(r"<(?P<name>[^:>]+):(?P<len>\d+)(?::(?P<type>[^>]+))?>(?P<data>.*?)", text, re.IGNORECASE | re.DOTALL)

    for match in tags:
        name = match.group("name").upper()
        length = int(match.group("len"))
        # Grab exactly 'length' characters after the closing bracket
        # This ensures 'INVALID' is captured even if it's "wrong"
        results[name] = match.group("data")[:length]

    return results


# --- Entry Points ---


def run() -> None:
    """Entry point for the server to be called by the CLI."""
    mcp.run()


def main() -> None:
    """Main entry point for the module execution."""
    mcp.run()


if __name__ == "__main__":
    mcp.run()
