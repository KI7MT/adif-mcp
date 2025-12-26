"""ADIF-MCP Server: Authoritative 3.1.6 Specification Server."""

import json
from importlib import resources
from typing import Any, Dict, List, cast

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource
from pydantic import AnyUrl

from adif_mcp.parsers.adif_reader import parse_adi_text

# Initialize the FastMCP server
mcp = FastMCP("ADIF-MCP")


# --- Helper Logic for Versioned Resources ---


def get_spec_text(filename: str, version: str = "316") -> str:
    """
    Reads a specification file from the versioned resource directory.

    Args:
        filename: The name of the JSON file (without extension).
        version: The ADIF version directory name.

    Returns:
        The string content of the JSON resource.
    """
    try:
        # Path: src/adif_mcp/resources/spec/316/{filename}.json
        res = resources.files(f"adif_mcp.resources.spec.{version}")
        resource_path = res.joinpath(f"{filename}.json")
        return resource_path.read_text()
    except Exception as e:
        return json.dumps(
            {
                "error": f"Resource {filename} not found for version {version}",
                "details": str(e),
            }
        )


# --- MCP Resources (The "Contract") ---


@mcp.list_resources()  # type: ignore[operator]
async def list_adif_resources() -> List[Resource]:
    """Exposes the authoritative ADIF 3.1.6 specification to the AI."""
    return [
        Resource(
            uri=AnyUrl("adif://spec/316/all"),
            name="ADIF 3.1.6 Master Spec",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("adif://spec/316/fields"),
            name="ADIF 3.1.6 Field Definitions",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("adif://spec/316/enumerations"),
            name="ADIF 3.1.6 Enums",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("adif://spec/catalog"),
            name="ADIF Field Catalog",
            mimeType="application/json",
        ),
    ]


@mcp.read_resource()  # type: ignore[operator]
async def read_adif_resource(uri: AnyUrl) -> str:
    """
    Reads specific ADIF specification data from local storage.

    Args:
        uri: The unique resource URI.

    Returns:
        The string content of the requested resource.
    """
    uri_str = str(uri)
    if uri_str == "adif://spec/catalog":
        res = resources.files("adif_mcp.resources.spec")
        cat_path = res.joinpath("adif_catalog.json")
        return cat_path.read_text()

    if uri_str.startswith("adif://spec/316/"):
        spec_type = uri_str.split("/")[-1]  # e.g., 'all' or 'fields'
        return get_spec_text(spec_type)

    raise ValueError(f"Resource not found: {uri}")


# --- Core Validation & Utility Tools ---


@mcp.tool()
def get_service_metadata() -> Dict[str, Any]:
    """Retrieves ADIF-MCP metadata, including the 3.1.6 spec status."""
    res = resources.files("adif_mcp.resources.spec")
    meta_path = res.joinpath("adif_meta.json")
    with open(str(meta_path), "r") as f:
        return cast(Dict[str, Any], json.load(f))


@mcp.tool()
def normalize_band(value: str) -> str:
    """
    Canonicalizes a frequency or band string using ADIF standards.

    Args:
        value: The raw string input (e.g., '14.074' or '20m').

    Returns:
        The uppercase ADIF band enumeration.
    """
    return str(value).strip().upper()


@mcp.tool()
def parse_adif(adif_text: str) -> List[Dict[str, Any]]:
    """
    Parses raw .adi text into structured JSON records.

    Args:
        adif_text: The string content of an ADIF file.

    Returns:
        A list of dictionaries representing QSO records.
    """
    return cast(List[Dict[str, Any]], parse_adi_text(adif_text))


# --- Entry Points ---


def run() -> None:
    """Entry point for the server to be called by the CLI."""
    mcp.run()


def main() -> None:
    """Main entry point for the module execution."""
    mcp.run()


if __name__ == "__main__":
    mcp.run()
