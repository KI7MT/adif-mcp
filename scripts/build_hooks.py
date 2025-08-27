"""
Custom Hatchling build hook for adif-mcp.

This hook runs at build time and copies the `[tool.adif]` table from
`pyproject.toml` into a generated JSON file at
`src/adif_mcp/adif_meta.json`.

Why:
- Ensures the ADIF spec version and supported features are baked into
  built wheels and sdists (so the runtime does not need to parse
  `pyproject.toml`).
- Keeps `pyproject.toml` as the single source of truth for metadata.
- Provides a consistent fallback mechanism: editable installs read
  directly from `pyproject.toml`, while published artifacts use the
  generated JSON.

The generated file is ignored by version control (`.gitignore`) and
is safe to regenerate on every build.
"""

from __future__ import annotations

import json
import pathlib
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


class BuildHook(BuildHookInterface):
    """
    Copy [tool.adif] from pyproject.toml into src/adif_mcp/adif_meta.json
    during build, so wheels contain the ADIF spec metadata.
    """

    def initialize(self, version: str, build_data: dict) -> None:  # noqa: D401
        """Run at build start; write `adif_meta.json` into the package directory."""
        root = pathlib.Path(self.root)
        pyproject = root / "pyproject.toml"

        meta = {"spec_version": "0", "features": []}

        if tomllib and pyproject.is_file():
            try:
                data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
                adif = (data.get("tool") or {}).get("adif") or {}
                spec = adif.get("spec_version")
                feats = adif.get("features")
                if isinstance(spec, str):
                    meta["spec_version"] = spec
                if isinstance(feats, list):
                    meta["features"] = [str(x) for x in feats]
            except Exception as e:  # pragma: no cover
                print(
                    f"[build-hook] Warning: failed reading [tool.adif]: {e}",
                    file=sys.stderr,
                )

        out = root / "src" / "adif_mcp" / "adif_meta.json"
        out.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        print(f"[build-hook] wrote {out}")
