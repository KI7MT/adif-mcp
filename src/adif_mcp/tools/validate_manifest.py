"""Module to validate the MCP manifest file"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def validate_one(path: Path) -> int:
    """Verify path exists

    Args:
        path (Path): `str` expected path
    """
    if not path.exists():
        print(f"Not found: {path}", file=sys.stderr)
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"invalid JSON in {path}: {e}", file=sys.stderr)
        return 1
    tools = data.get("tools")
    if not isinstance(tools, list):
        print(f"{path}: manifest.tools missing or not a list", file=sys.stderr)
        return 1
    print(f"Validating {path}")
    return 0


def main(argv: list[str]) -> int:
    """Start main target"""
    if not argv:
        print(
            "usage: python -m adif_mcp.tools.validate_manifest <manifest.json> [...]",
            file=sys.stderr,
        )
        return 2
    rc = 0
    for arg in argv:
        rc |= validate_one(Path(arg))
    return rc


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
