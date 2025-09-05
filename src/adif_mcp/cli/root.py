"""Root CLI wiring for adif-mcp.

Builds the top-level argument parser and registers all subcommands
(`convert`, `convert-adi`, `validate-manifest`, `persona`, `provider`,
`creds`, `eqsl`). This module is the central dispatcher invoked by the
`adif-mcp` console script.
"""

from __future__ import annotations

import argparse
import sys
from typing import Callable, Protocol, cast

from . import convert_adi, creds, eqsl_stub, persona, provider, validate


class _RegisterCLI(Protocol):
    """Protocol for subcommand registration functions."""

    def __call__(self, sp: argparse._SubParsersAction[argparse.ArgumentParser]) -> None: ...


# ------------------------ parser ------------------------


def build_parser() -> argparse.ArgumentParser:
    """Create and return the root argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(prog="adif-mcp", description="adif-mcp CLI")
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser] = parser.add_subparsers(
        dest="command"
    )

    # convert + alias
    p_conv = subparsers.add_parser(
        "convert",
        help="Convert ADIF to JSON/NDJSON",
        description="Convert ADIF (.adi) to QsoRecord JSON/NDJSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    convert_adi.add_convert_args(p_conv)
    p_conv.set_defaults(func=lambda _args: convert_adi.main(sys.argv[2:]))

    p_conv_alias = subparsers.add_parser(
        "convert-adi",
        help="(alias) Convert ADIF to JSON/NDJSON",
        description="Convert ADIF (.adi) to QsoRecord JSON/NDJSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    convert_adi.add_convert_args(p_conv_alias)
    p_conv_alias.set_defaults(func=lambda _args: convert_adi.main(sys.argv[2:]))

    # persona / provider / creds / eqsl
    if hasattr(persona, "register_cli"):
        cast(_RegisterCLI, getattr(persona, "register_cli"))(subparsers)
    if hasattr(provider, "register_cli"):
        cast(_RegisterCLI, getattr(provider, "register_cli"))(subparsers)
    if hasattr(creds, "register_cli"):
        cast(_RegisterCLI, getattr(creds, "register_cli"))(subparsers)
    if hasattr(eqsl_stub, "register_cli"):
        cast(_RegisterCLI, getattr(eqsl_stub, "register_cli"))(subparsers)
    if hasattr(validate, "register_cli"):
        cast(_RegisterCLI, getattr(validate, "register_cli"))(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the adif-mcp CLI."""
    args_in = sys.argv[1:] if argv is None else argv
    parser = build_parser()

    # Default to `convert` if no subcommand was provided
    if not args_in:
        return convert_adi.main([])

    args = parser.parse_args(args_in)
    func = cast(Callable[[argparse.Namespace], int] | None, getattr(args, "func", None))
    if func is not None:
        return func(args)

    parser.print_help()
    return 2
