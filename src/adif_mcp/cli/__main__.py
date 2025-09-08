"""CLI entrypoint that only displays a deprecation message and exits."""

from __future__ import annotations

from adif_mcp import DEPRECATION_MSG, __version__


def main(argv: list[str] | None = None) -> int:
    print(f"adif-mcp {__version__}\n")
    print(DEPRECATION_MSG)
    return 0  # non-zero would break some automation; keep 0


if __name__ == "__main__":
    raise SystemExit(main())

# Original before tombstone
# """
# Executable entrypoint for the adif-mcp CLI.

# This module allows `python -m adif_mcp.cli` to run the CLI directly.
# It delegates to `main()` in `root.py` to construct the argument parser
# and dispatch subcommands.
# """

# from __future__ import annotations

# import argparse
# import sys
# from typing import Callable, cast

# from .root import build_parser


# def main(argv: list[str] | None = None) -> int:
#     """Entry point for the adif-mcp CLI; delegates to root.build_parser()."""
#     parser = build_parser()
#     args = parser.parse_args(sys.argv[1:] if argv is None else argv)

#     # mypy: argparse injects .func dynamically; tell the type checker what it is
#     func = cast(Callable[[argparse.Namespace], int] | None, getattr(args, "func", None))
#     if func is not None:
#         return func(args)

#     parser.print_help()
#     return 0


# if __name__ == "__main__":
#     raise SystemExit(main())
