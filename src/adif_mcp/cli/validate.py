"""Validation CLI for adif-mcp manifests.

This module implements the `validate-manifest` subcommand to validate
manifest.json files against the bundled JSON Schema (manifest.v1.json).

Usage:
    adif-mcp validate-manifest [--path <FILE>]

    # With uv:
    uv run adif-mcp validate-manifest
    uv run adif-mcp validate-manifest --path ./my-manifest.json

If --path is not provided, the tool attempts to locate manifest.json in:
    1. The current working directory.
    2. The project source tree (src/adif_mcp/mcp/manifest.json).
    3. The installed package resources.
"""

from __future__ import annotations

import argparse
import json
import sys
from importlib.resources import files
from pathlib import Path
from typing import Optional


def _resolve_manifest_path(arg_path: Optional[str]) -> Path | None:
    """Resolve a manifest path from CLI arg, CWD, project tree, or package resource."""
    # 1) explicit --path
    if arg_path:
        p = Path(arg_path)
        return p if p.exists() else None

    # 2) CWD
    cwd = Path("manifest.json")
    if cwd.exists():
        return cwd

    # 3) project tree: src/adif_mcp/mcp/manifest.json
    #    (per pyproject: manifest = "mcp/manifest.json")
    proj = Path(__file__).resolve().parent.parent / "mcp" / "manifest.json"
    if proj.exists():
        return proj

    # 4) packaged resource (installed package)
    try:
        res = files("adif_mcp.mcp").joinpath("manifest.json")
        # Convert to real path if supported; otherwise return a Path wrapper for open()
        return Path(str(res))
    except Exception:
        return None


def cmd_validate_manifest(args: argparse.Namespace) -> int:
    """Validate a manifest JSON file against the bundled JSON Schema."""
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        print("jsonschema required. Install: uv pip install jsonschema", file=sys.stderr)
        return 1
    import jsonschema

    schema_path = files("adif_mcp.resources.schemas").joinpath("manifest.v1.json")
    manifest_path = _resolve_manifest_path(getattr(args, "path", None))

    if manifest_path is None:
        print(
            "manifest.json not found. Pass --path <FILE> or place manifest.json in CWD "
            "or at src/adif_mcp/manifest.json",
            file=sys.stderr,
        )
        return 2

    with schema_path.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)

    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    jsonschema.validate(manifest, schema)
    print(f"OK: {manifest_path} validates against manifest.v1.json")
    return 0


def register_cli(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register the validate-manifest subcommand."""
    p = subparsers.add_parser(
        "validate-manifest",
        help="Validate manifest.json against the schema",
        description="Validate a manifest JSON file against the bundled schema.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--path",
        metavar="FILE",
        default=None,
        help="Path to manifest JSON to validate (defaults to CWD or bundled copy).",
    )
    p.set_defaults(func=cmd_validate_manifest)
