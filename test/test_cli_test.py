"""CLI smoke tests for `adif-mcp`."""

# test/test_cli_test.py
from cli_test_helpers import shell


def test_entrypoint_help() -> None:
    r = shell("adif-mcp --help")
    assert r.exit_code == 0
    assert "adif-mcp CLI" in r.stdout


def test_validate_help() -> None:
    r = shell("adif-mcp validate-manifest --help")
    assert r.exit_code == 0
    assert "manifest" in r.stdout.lower()


def test_convert_help() -> None:
    r1 = shell("adif-mcp convert --help")
    r2 = shell("adif-mcp convert-adi --help")
    assert r1.exit_code == 0
    assert r2.exit_code == 0
