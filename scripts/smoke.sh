#!/usr/bin/env bash
# scripts/smoke.sh
# Full local smoke test for adif-mcp using uv + an isolated install check.

set -euo pipefail

banner() { printf "\n\033[1;36m[smoke]\033[0m %s\n" "$*"; }

# Move to repo root (script is expected in ./scripts/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

banner "env info"
command -v uv >/dev/null || { echo "uv not found. Install with: pip install uv  (or: brew install uv)"; exit 1; }
uv --version || true
uv run python -V || true

banner "sync deps (frozen if lock present)"
uv sync

banner "lint (ruff)"
uv run ruff check .

banner "type-check (mypy)"
uv run mypy src

banner "docstrings (interrogate)"
uv run interrogate -c pyproject.toml

banner "manifest validation"
uv run python scripts/validate_manifest.py mcp/manifest.json

banner "unit tests (pytest)"
uv run pytest -q

banner "build (wheel + sdist)"
rm -rf dist build *.egg-info
uv build
ls -lh dist

banner "install built wheel in a fresh, isolated venv"
VENV=".smoke-venv"
rm -rf "$VENV"
uv venv --seed "$VENV"

PY="$VENV/bin/python"
PIP="$VENV/bin/pip"
BIN="$VENV/bin"

echo "[smoke] python: $($PY -V)"
echo "[smoke] install wheel"
$PIP install --upgrade pip >/dev/null
$PIP install dist/*.whl

echo "[smoke] sanity: CLI reports version"
"$BIN/adif-mcp" version

echo "[smoke] import/package sanity"
"$PY" - <<'PY'
import adif_mcp as m
print("import OK:", getattr(m, "__version__", "?"), "ADIF", getattr(m, "__adif_spec__", "?"))
PY

echo "[smoke] entrypoints"
"$BIN/adif-mcp" --help >/dev/null
"$BIN/adif-mcp" manifest-validate >/dev/null

# Optional: clean up the venv created by this smoke run
rm -rf "$VENV"

banner "OK — full smoke test passed"
