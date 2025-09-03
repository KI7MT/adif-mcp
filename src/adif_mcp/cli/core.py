from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

import click

from adif_mcp import __adif_spec__, __version__
from adif_mcp.tools.validate_manifest import validate_one


def register_core(cli: click.Group) -> None:
    @cli.command("version")
    def version_cmd() -> None:
        click.echo(f"adif-mcp {__version__} (ADIF {__adif_spec__} compatible)")

    @cli.command("validate-manifest")
    def validate_manifest() -> None:
        candidates: list[Path] = []
        try:
            pkg = files("adif_mcp.mcp").joinpath("manifest.json")
            candidates.append(Path(str(pkg)))
        except Exception:
            pass
        repo = Path("mcp/manifest.json")
        if repo.exists():
            candidates.append(repo)
        if not candidates:
            click.echo("No manifest.json found (package or repo).", err=True)
            raise SystemExit(1)

        last_err: Exception | None = None
        for p in candidates:
            try:
                code = validate_one(p)
                if code == 0:
                    click.echo("manifest: OK")
                    return
            except Exception as e:
                last_err = e
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data.get("tools"), list) and data["tools"]:
                    click.echo("manifest: OK")
                    return
            except Exception as e:
                last_err = e
        msg = (
            f"manifest validation failed: {last_err}"
            if last_err
            else "manifest validation failed"
        )
        click.echo(msg, err=True)
        raise SystemExit(1)
