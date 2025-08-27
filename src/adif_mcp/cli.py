import click
import json
import pathlib

@click.group()
def cli():
    "ADIF MCP core CLI"
    pass

@cli.command()
def version():
    from adif_mcp import __version__
    click.echo(f"adif-mcp {__version__}")

@cli.command("manifest-validate")
def manifest_validate():
    p = pathlib.Path("mcp/manifest.json")
    d = json.loads(p.read_text())
    assert "tools" in d and isinstance(d["tools"], list), "manifest.tools missing"
    click.echo("manifest: OK")
