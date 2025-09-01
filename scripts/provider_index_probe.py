#!/usr/bin/env python3
"""
Provider index probe (no network).

Purpose
-------
Sanity-check that a persona has a configured provider and a secret present in
the OS keyring (via PersonaManager). This is CI-safe and avoids direct keyring
imports in the script.

Usage
-----
    uv run python scripts/provider_index_probe.py --persona MyEQSL --provider eqsl
    uv run python scripts/provider_index_probe.py --persona MyLoTW --provider lotw
    uv run python scripts/provider_index_probe.py --persona MyQRZ  --provider qrz
    uv run python scripts/provider_index_probe.py --persona MyClub --provider clublog

Exit codes
----------
0  OK
2  persona not found
3  provider not configured for persona
4  username missing/empty
5  secret missing or keyring unavailable
"""

from __future__ import annotations

import argparse
from typing import NoReturn

from adif_mcp.persona_manager import PersonaManager

SUPPORTED = {"eqsl", "lotw", "qrz", "clublog"}


def _die(code: int, msg: str) -> NoReturn:
    """Common mesage print statment and raise error"""
    print(f"[error] {msg}")
    raise SystemExit(code)


def main() -> int:
    """
    Main entry point for verifying the presence of credentials for aspecified
    persona and provider.

    This function sets up an argument parser to accept command-line arguments for
    the persona and provider. It checks if the specified persona exists, retrieves
    the associated username, and verifies the presence of the secret in the keyring.
    If any checks fail, the function will terminate the program with an appropriate
    exit code and error message.

    Command-line Arguments:
        --persona (str): The name of the persona to verify (required).
        --provider (str): The provider to check against the persona (required).
                          Must be one of the supported providers.

    Returns:
        int: Exit code indicating the result of the operation.
             Returns 0 on success, or a non-zero exit code on failure.
    """
    ap = argparse.ArgumentParser(
        description="Verify persona/provider credential presence (no network)."
    )
    ap.add_argument("--persona", required=True, help="Persona name, e.g. MyEQSL")
    ap.add_argument(
        "--provider",
        required=True,
        choices=sorted(SUPPORTED),
        help="Provider to check",
    )
    args = ap.parse_args()

    pm = PersonaManager()

    persona = pm.get_persona(args.persona)
    if persona is None:
        _die(2, f"No such persona: {args.persona}")

    username = pm.get_provider_username(args.persona, args.provider)
    if username is None or username.strip() == "":
        _die(3, f"No provider '{args.provider}' configured for '{args.persona}'")

    # secret present?
    secret = pm.get_secret(args.persona, args.provider)
    if secret is None or secret == "":
        _die(5, "Secret not found in keyring (or keyring unavailable).")

    f"[OK] creds present for {args.persona}/{args.provider} "
    f"(username={username})"

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
