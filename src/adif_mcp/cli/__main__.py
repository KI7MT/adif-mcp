# src/adif_mcp/cli/__main__.py
"""CLI entry point (tombstone mode)."""

from __future__ import annotations

import sys

from adif_mcp import __version__  # for the banner text

# ✅ Add these two imports:
from .root import build_parser  # for the help path


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    # If user asked for help anywhere (top-level or subcommand), use the parser path
    if any(a in ("-h", "--help") for a in argv) or not argv:
        parser = build_parser()
        args = parser.parse_args(argv)
        if hasattr(args, "func"):
            return args.func(args)
        parser.print_help()
        return 0

    # Tombstone banner for all other invocations (keeps tests that call --help happy)
    print(f"adif-mcp {__version__}\n")
    print(
        "adif-mcp (Python) is deprecated. Future development is moving to Java 21.\n"
        "See the repository README for migration details.\n"
    )
    return 0
