#!/usr/bin/env bash
set -euo pipefail

echo "[move] creating resource directories"
mkdir -p src/adif_mcp/resources/providers
mkdir -p src/adif_mcp/resources/spec
mkdir -p src/adif_mcp/resources/schemas

echo "[move] moving provider JSONs"
git mv mcp/providers/*.json src/adif_mcp/resources/providers/

echo "[move] moving spec JSONs"
git mv mcp/spec/*.json src/adif_mcp/resources/spec/

echo "[move] moving schema JSONs"
git mv mcp/schemas/*.json src/adif_mcp/resources/schemas/

echo "[move] done; you can now remove the empty mcp/ folder"
