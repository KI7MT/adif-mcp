"""Validate the MCP manifest(s) against basic shape assumptions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

# Prefer the in-package validator; if unavailable, we still do shape checks.
try:
    from adif_mcp.tools.validate_manifest import validate_one
except Exception:  # pragma: no cover - optional path
    validate_one = None  # type: ignore[assignment]

try:
    from importlib.resources import files as pkg_files
except ImportError:  # pragma: no cover - py<3.9 fallback (not expected)
    pkg_files = None  # type: ignore


def _load_package_manifest() -> Tuple[Path, Dict[str, Any]]:
    """
    Load the canonical manifest shipped with the package.

    First tries: src/adif_mcp/mcp/manifest.json (via importlib.resources).
    Falls back to repo-root mcp/manifest.json if needed.
    """
    # Try packaged path
    if pkg_files is not None:
        try:
            p = pkg_files("adif_mcp.mcp").joinpath("manifest.json")
            text = p.read_text(encoding="utf-8")
            return Path(str(p)), json.loads(text)
        except Exception:
            pass

    # Fallback: repo path
    fallback = Path("mcp/manifest.json")
    if fallback.exists():
        return fallback, json.loads(fallback.read_text(encoding="utf-8"))

    pytest.skip("No manifest.json found in package or repo.")


def _all_repo_manifests(repo_root: Path) -> List[Path]:
    """Return any manifest.json tracked in the repo (e.g., examples)."""
    return [p for p in repo_root.rglob("manifest.json")]


def test_package_manifest_exists_and_has_tools() -> None:
    """The packaged (or fallback) manifest must exist with a non-empty tools array."""
    path, data = _load_package_manifest()
    assert "tools" in data, f"manifest.tools missing in {path}"
    tools = data["tools"]
    assert isinstance(tools, list) and tools, "manifest.tools must be a non-empty list"


def test_manifest_examples_are_json_serializable() -> None:
    """Each tool example (if present) should be valid JSON objects."""
    _, data = _load_package_manifest()
    tools = data.get("tools", [])
    for t in tools:
        examples = t.get("examples", [])
        assert isinstance(examples, list)
        for ex in examples:
            assert isinstance(ex, dict)
            # Round-trip sanity
            assert isinstance(json.loads(json.dumps(ex)), dict)


def test_manifest_schema_validation_if_available() -> None:
    """
    If the in-package validator is available, validate the canonical manifest.

    This keeps the test resilient if validate_one is renamed/relocated later.
    """
    if validate_one is None:
        pytest.skip("Schema validator unavailable in package.")
    path, _ = _load_package_manifest()
    validate_one(path)
