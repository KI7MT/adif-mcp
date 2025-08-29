"""Validate our MCP manifest with the local schema checker."""

from __future__ import annotations

from pathlib import Path

from scripts.validate_manifest import validate_one


def test_manifest_jsonschema_ok() -> None:
    """mcp/manifest.json should validate against mcp/schemas/manifest.v1.json."""
    assert validate_one(Path("mcp/manifest.json"))
