"""
Validate MCP manifest files against the local v1 schema.

Usage:
    uv run python scripts/validate_manifest.py mcp/manifest.json
    # or multiple:
    uv run python scripts/validate_manifest.py mcp/manifest.json other/manifest.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Sequence, cast

from jsonschema import validate

SCHEMA_PATH = Path("mcp/schemas/manifest.v1.json")


def _load_json(p: Path) -> Dict[str, Any]:
    """Load a JSON file from *p* and return it as a typed dict.

    Notes:
        `json.load` returns `Any`, so we cast to `Dict[str, Any]` to keep mypy happy.
    """
    with p.open("r", encoding="utf-8") as fh:
        return cast(Dict[str, Any], json.load(fh))


def validate_one(p: Path) -> bool:
    """Validate a single manifest file at *p* against the local MCP v1 schema.

    Returns:
        True if validation succeeds, False otherwise.
    """
    schema = _load_json(SCHEMA_PATH)
    manifest = _load_json(p)

    # quick structural sanity check before full schema validation
    tools = manifest.get("tools")
    if not isinstance(tools, list):
        print(f"{p}: ERROR: manifest.tools missing or not a list", file=sys.stderr)
        return False

    try:
        validate(instance=manifest, schema=schema)  # jsonschema handles deep checks
    except Exception as exc:  # jsonschema.ValidationError or others
        print(f"{p}: INVALID: {exc}", file=sys.stderr)
        return False

    print(f"{p}: OK (jsonschema)")
    return True


def main(argv: Sequence[str]) -> int:
    """CLI entry-point. Validates one or more manifest paths from *argv*.

    Returns:
        0 on success for all files; 1 if any validation fails or no files provided.
    """
    if not argv:
        print(
            "Usage: python scripts/validate_manifest.py <manifest.json> [...]",
            file=sys.stderr,
        )
        return 1

    ok = True
    for arg in argv:
        path = Path(arg)
        if not path.exists():
            print(f"{path}: ERROR: file not found", file=sys.stderr)
            ok = False
            continue
        ok = validate_one(path) and ok

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
