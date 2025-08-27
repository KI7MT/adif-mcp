#!/usr/bin/env python3

"""Validate MCP manifest files against a minimal v1 schema.

Usage:
    uv run python scripts/validate_manifest.py mcp/manifest.json
    uv run python scripts/validate_manifest.py
        # defaults to mcp/manifest.json if present
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from jsonschema import validate  # type: ignore[import-untyped]

SCHEMA_PATH = Path("mcp/schemas/manifest.v1.json")


def load_json(path: Path) -> dict:
    """Read and parse a JSON file into a Python dict."""
    return json.loads(path.read_text(encoding="utf-8"))


def validate_one(path: Path, schema_path: Path = SCHEMA_PATH) -> bool:
    """Validate a single manifest file against the schema and print a short OK line."""
    manifest = load_json(path)
    schema = load_json(schema_path)
    validate(instance=manifest, schema=schema)
    print(f"{path}: OK (jsonschema)")
    return True


def main(argv: Sequence[str]) -> int:
    """CLI entrypoint. Validate one or more manifest paths.

    If no paths are provided, defaults to `mcp/manifest.json` if present.
    """
    files = (
        [Path(a) for a in argv]
        if argv
        else ([Path("mcp/manifest.json")] if Path("mcp/manifest.json").exists() else [])
    )
    if not files:
        print("No manifest paths provided and default not found.", file=sys.stderr)
        return 2

    failures = 0
    for p in files:
        try:
            validate_one(p)
        except Exception as e:
            print(f"{p}: INVALID: {e}", file=sys.stderr)
            failures += 1

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
