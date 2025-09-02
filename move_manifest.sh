#!/usr/bin/env bash
set -euo pipefail

# Move the server manifest into the package so it ships with the server.
# Safe to re-run; no-op if already moved.

if [[ -f "mcp/manifest.json" ]]; then
  echo "[move] creating package manifest directory"
  mkdir -p src/adif_mcp/mcp

  echo "[move] moving mcp/manifest.json -> src/adif_mcp/mcp/manifest.json"
  git mv mcp/manifest.json src/adif_mcp/mcp/manifest.json
else
  echo "[move] src/adif_mcp/mcp/manifest.json already in place or source missing; skipping"
fi

echo "[move] validating manifests found in repo"
make manifest || true
