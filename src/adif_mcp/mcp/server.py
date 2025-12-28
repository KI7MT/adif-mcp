"""
ADIF-MCP Server: Authoritative 3.1.6 Specification Server.

Provides tools for parsing, streaming, and validating ADIF data.
"""

import json
import os
import re
from typing import Any, Dict, List

import aiofiles
import mcp.types as types
from mcp.server.fastmcp import FastMCP

import adif_mcp
from adif_mcp.utils.geography import calculate_distance_impl, calculate_heading_impl

# Initialize the FastMCP server
mcp = FastMCP("ADIF-MCP")


def get_spec_text(filename: str, version: str = "316") -> str:
    """Retrieve raw text of a 3.1.6 specification JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.abspath(os.path.join(current_dir, "..", "resources", "spec", version))
    name = filename.lower().strip()

    targets = [
        os.path.join(json_dir, f"enumerations_{name}.json"),
        os.path.join(json_dir, f"{name}.json"),
        os.path.join(json_dir, "all.json"),
    ]

    for target_path in targets:
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                continue
    return json.dumps({"error": f"Resource {name} not found in {json_dir}"})


# --- MCP Resources ---


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


# --- Internal Logic ---


def parse_adif_internal(text: str) -> Dict[str, str]:
    """Surgically extracts ADIF tags and their data by length."""
    tag_pattern = re.compile(
        r"<(?P<name>[^:>]+):(?P<len>\d+)(?::(?P<type>[^>]+))?>", re.IGNORECASE
    )
    results: Dict[str, str] = {}

    for match in tag_pattern.finditer(text):
        name = match.group("name").upper()
        length = int(match.group("len"))
        start_of_data = match.end()
        data = text[start_of_data : start_of_data + length]
        results[name] = data

    return results


# --- Core Tools ---


@mcp.tool()
def get_version_info() -> Dict[str, Any]:
    """Returns the version of the ADIF-MCP server and spec."""
    return {
        "service_version": adif_mcp.__version__,
        "adif_spec_version": adif_mcp.__adif_spec__,
    }


@mcp.tool()
def calculate_distance(start: str, end: str) -> float:
    """Calculates distance (km) between Maidenhead locators."""
    return calculate_distance_impl(start, end)


@mcp.tool()
def calculate_heading(start: str, end: str) -> float:
    """Calculates heading (azimuth) between Maidenhead locators."""
    return calculate_heading_impl(start, end)


@mcp.tool()
async def parse_adif(
    file_path: str, start_at: int = 1, limit: int = 20
) -> List[types.TextContent]:
    """Streaming parser for large ADIF files with record seeking."""
    record_pattern = re.compile(r"(.*?)<EOR>", re.IGNORECASE | re.DOTALL)

    try:
        if not os.path.exists(file_path):
            err_msg = f"ERROR: File not found at {file_path}"
            return [types.TextContent(type="text", text=err_msg)]

        async with aiofiles.open(file_path, mode="r") as f:
            content = await f.read()
            matches = list(record_pattern.finditer(content))
            total_count = len(matches)

            start_idx = max(0, start_at - 1)
            end_idx = start_idx + limit
            requested = matches[start_idx:end_idx]

            output_text = f"FILE: {file_path}\nTOTAL RECORDS: {total_count}\n"
            current_max = min(start_at + len(requested) - 1, total_count)
            output_text += f"DISPLAYING: {start_at} to {current_max}\n\n"

            for i, match in enumerate(requested):
                current_num = start_at + i
                output_text += f"--- RECORD {current_num} ---\n"
                output_text += f"{match.group(0).strip()}\n\n"

            return [types.TextContent(type="text", text=output_text)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"STREAM ERROR: {str(e)}")]


@mcp.tool()
def read_specification_resource(resource_name: str) -> str:
    """Reads an ADIF 3.1.6 specification resource (e.g., 'mode')."""
    return get_spec_text(resource_name)


@mcp.tool()
def search_enumerations(search_term: str) -> Dict[str, Any]:
    """Surgically searches local enumeration files."""
    target = "primary_administrative_subdivision"
    raw_data = get_spec_text(target)

    try:
        data: Any = json.loads(raw_data)
        if isinstance(data, dict):
            data = data.get("Adif", data)
            data = data.get("Enumerations", data)
            data = data.get("Primary_Administrative_Subdivision", data)
            if isinstance(data, dict):
                data = data.get("Records", data)

        results: Dict[str, Any] = {}
        term = search_term.upper().strip()

        if isinstance(data, dict):
            for rec_id, fields in data.items():
                code = str(fields.get("Code", "")).upper()
                sub_key = "Primary Administrative Subdivision"
                name = str(fields.get(sub_key, "")).upper()
                if term == code or term in name:
                    results[rec_id] = fields

        if not results:
            msg = f"'{search_term}' not found in local records."
            return {"message": msg}
        return results
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


@mcp.tool()
def validate_adif_record(adif_string: str) -> Dict[str, Any]:
    """Validates an ADIF record against 3.1.6 rules."""
    parsed = parse_adif_internal(adif_string)

    try:
        raw_fields = get_spec_text("fields")
        fields_spec = json.loads(raw_fields)["Adif"]["Fields"]["Records"]
    except Exception as e:
        return {"status": "error", "message": f"Could not load spec: {str(e)}"}

    report: Dict[str, Any] = {
        "status": "success",
        "errors": [],
        "warnings": [],
        "record": parsed,
    }

    for field_name, value in parsed.items():
        upper_field = field_name.upper()

        if upper_field not in fields_spec:
            msg = f"Field '{upper_field}' is not in spec."
            report["warnings"].append(msg)
            continue

        spec_info = fields_spec[upper_field]
        data_type = spec_info.get("Data Type")

        if data_type == "Number":
            # Validates integers and decimals
            if not re.match(r"^-?\d*\.?\d+$", str(value).strip()):
                msg = f"Field '{upper_field}' expects Number, got '{value}'."
                report["errors"].append(msg)
                report["status"] = "invalid"

    return report


# --- Entry Points ---


def run() -> None:
    """Entry point for the server."""
    mcp.run()


def main() -> None:
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()
