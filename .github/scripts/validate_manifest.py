#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

MANIFEST = Path("mcp/manifest.json")


def fail(msg: str) -> None:
    print(f"[manifest] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not MANIFEST.exists():
        fail(f"missing {MANIFEST}")

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"invalid JSON: {e}")

    if "tools" not in data or not isinstance(data["tools"], list):
        fail("manifest.tools missing or not a list")

    required_tool_keys = {"name", "description", "input_schema", "output_schema"}
    for i, tool in enumerate(data["tools"], 1):
        if not isinstance(tool, dict):
            fail(f"tool #{i} is not an object")
        missing = required_tool_keys - tool.keys()
        if missing:
            fail(f"tool #{i} missing keys: {sorted(missing)}")

    print("[manifest] OK")


if __name__ == "__main__":
    main()
