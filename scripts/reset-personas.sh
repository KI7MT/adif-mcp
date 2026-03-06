#!/usr/bin/env bash
# ============================================================================
#  reset-personas.sh — Recreate KI7MT / KE1HA persona mappings
#
#  This script rebuilds all adif-mcp personas and stores credentials in the
#  OS keyring (macOS Keychain, Windows Credential Manager, or Linux
#  Secret Service / keyrings.alt).
#
#  USAGE:
#    1. Export your credentials as environment variables (ephemeral, never saved):
#
#         export EQSL_USER=KI7MT      EQSL_PASS='...'
#         export LOTW_USER=KI7MT      LOTW_PASS='...'
#         export QRZ_USER=KI7MT       QRZ_PASS='...'   QRZ_KEY='...'
#         export HAMQTH_USER=KI7MT    HAMQTH_PASS='...'
#
#    2. Run this script:
#
#         bash scripts/reset-personas.sh
#
#  DATE RANGES:
#    KE1HA  2001-04-16  →  2009-12-21  (previous call, merged in LoTW/eQSL)
#    KI7MT  2009-12-22  →  present     (vanity call)
#    No overlap — KE1HA ends one day before KI7MT starts.
#
#  SECURITY:
#    - Credentials come from ENV vars only (never hardcoded)
#    - Stored in OS keyring via adif-mcp CLI
#    - This file contains ZERO secrets
# ============================================================================
set -euo pipefail

# --- Resolve adif-mcp CLI ---------------------------------------------------
# Search order: IONIS_VENV, VIRTUAL_ENV, script's repo .venv, global
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${IONIS_VENV:-}" && -x "${IONIS_VENV}/bin/adif-mcp" ]]; then
    CLI="${IONIS_VENV}/bin/adif-mcp"
elif [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/adif-mcp" ]]; then
    CLI="${VIRTUAL_ENV}/bin/adif-mcp"
elif [[ -x "${SCRIPT_DIR}/.venv/bin/adif-mcp" ]]; then
    CLI="${SCRIPT_DIR}/.venv/bin/adif-mcp"
elif command -v adif-mcp &>/dev/null; then
    CLI="adif-mcp"
else
    echo "ERROR: adif-mcp not found. Install with: pip install adif-mcp" >&2
    exit 1
fi
echo "Using: $CLI ($(${CLI} --version 2>/dev/null || echo 'unknown version'))"

# --- Validate required env vars ---------------------------------------------
required_vars=(
    EQSL_USER EQSL_PASS
    LOTW_USER LOTW_PASS
    QRZ_USER QRZ_PASS QRZ_KEY
    HAMQTH_USER HAMQTH_PASS
)
missing=()
for var in "${required_vars[@]}"; do
    [[ -z "${!var:-}" ]] && missing+=("$var")
done
if [[ ${#missing[@]} -gt 0 ]]; then
    echo "ERROR: Missing environment variables:" >&2
    printf '  %s\n' "${missing[@]}" >&2
    echo "" >&2
    echo "Export them before running this script. See header for details." >&2
    exit 1
fi

# --- Clear existing personas -------------------------------------------------
echo ""
echo "=== Clearing all existing personas ==="
${CLI} persona remove-all --yes 2>/dev/null || true

# --- KI7MT personas (2009-12-22 → present) ----------------------------------
echo ""
echo "=== Creating KI7MT personas (2009-12-22 → present) ==="

${CLI} persona add --name MyEQSL    --callsign KI7MT --start 2009-12-22
${CLI} persona add --name MyLOTW    --callsign KI7MT --start 2009-12-22
${CLI} persona add --name MyQRZ     --callsign KI7MT --start 2009-12-22
${CLI} persona add --name MyHAMQTH  --callsign KI7MT --start 2009-12-22
echo "--- Storing KI7MT credentials in OS keyring ---"
${CLI} persona set-credential --persona MyEQSL    --provider eqsl    --username "${EQSL_USER}"    --password "${EQSL_PASS}"
${CLI} persona set-credential --persona MyLOTW    --provider lotw    --username "${LOTW_USER}"    --password "${LOTW_PASS}"
${CLI} persona set-credential --persona MyQRZ     --provider qrz     --username "${QRZ_USER}"     --password "${QRZ_PASS}" --api-key "${QRZ_KEY}"
${CLI} persona set-credential --persona MyHAMQTH  --provider hamqth  --username "${HAMQTH_USER}"  --password "${HAMQTH_PASS}"

# --- KE1HA persona (2001-04-16 → 2009-12-21) --------------------------------
echo ""
echo "=== Creating KE1HA persona (2001-04-16 → 2009-12-21) ==="
echo "    (merged in LoTW/eQSL — uses KI7MT account credentials)"

${CLI} persona add --name KE1HA --callsign KE1HA --start 2001-04-16 --end 2009-12-21
${CLI} persona set-credential --persona KE1HA --provider eqsl    --username "${EQSL_USER}"    --password "${EQSL_PASS}"
${CLI} persona set-credential --persona KE1HA --provider lotw    --username "${LOTW_USER}"    --password "${LOTW_PASS}"
${CLI} persona set-credential --persona KE1HA --provider qrz     --username "${QRZ_USER}"     --password "${QRZ_PASS}" --api-key "${QRZ_KEY}"
${CLI} persona set-credential --persona KE1HA --provider hamqth  --username "${HAMQTH_USER}"  --password "${HAMQTH_PASS}"

# --- Summary -----------------------------------------------------------------
echo ""
echo "=== Persona Setup Complete ==="
${CLI} persona list --verbose
echo ""
echo "Credentials stored in OS keyring. ENV vars can be unset now."
