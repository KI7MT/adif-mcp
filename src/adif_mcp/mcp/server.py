"""ADIF-MCP Server: Authoritative 3.1.6 Specification Server."""

import json
from importlib import resources
from typing import Any, Dict, List, cast

from mcp.server.fastmcp import FastMCP

from adif_mcp.parsers.adif_reader import parse_adi_text
from adif_mcp.utils.geography import calculate_distance_impl, calculate_heading_impl

# Initialize the FastMCP server
mcp = FastMCP("ADIF-MCP")


# --- Helper Logic for Versioned Resources ---


def get_spec_text(filename: str, version: str = "316") -> str:
    """Reads a specification file from the versioned resource directory."""
    try:
        res = resources.files(f"adif_mcp.resources.spec.{version}")
        resource_path = res.joinpath(f"{filename}.json")
        return resource_path.read_text()
    except Exception as e:
        return json.dumps({"error": f"Resource {filename} not found", "details": str(e)})


# --- MCP Resources (The "Contract") ---


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
def get_service_metadata() -> Dict[str, Any]:
    """Retrieves ADIF-MCP metadata, including the 3.1.6 spec status."""
    res = resources.files("adif_mcp.resources.spec")
    meta_path = res.joinpath("adif_meta.json")
    with open(str(meta_path), "r") as f:
        return cast(Dict[str, Any], json.load(f))


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
    """Parses raw .adi text into structured JSON records."""
    return cast(List[Dict[str, Any]], parse_adi_text(adif_text))


# --- Entry Points ---


def run() -> None:
    """Entry point for the server to be called by the CLI."""
    mcp.run()


if __name__ == "__main__":
    mcp.run()
