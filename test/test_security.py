"""Security audit tests for adif-mcp — MCP Security Framework compliance."""

import ast
import os
import re

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "adif_mcp")


def _all_py_sources():
    """Yield all Python source files under SRC_DIR."""
    for root, _, files in os.walk(SRC_DIR):
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(root, f)


def test_no_print_credentials():
    """No print() calls with credential keywords."""
    pattern = re.compile(
        r'print\s*\(.*?(password|passwd|secret|api_key|token)',
        re.IGNORECASE,
    )
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"Credential print in {path}"


def test_no_logging_credentials():
    """No logging calls with credential keywords."""
    pattern = re.compile(
        r'log(?:ging)?\.\w+\s*\(.*?(password|passwd|secret|api_key)',
        re.IGNORECASE,
    )
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"Credential logging in {path}"


def test_no_subprocess():
    """No subprocess or shell=True usage."""
    pattern = re.compile(r'\bsubprocess\b|shell\s*=\s*True')
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"subprocess/shell in {path}"


def test_all_urls_https():
    """All hardcoded URLs use HTTPS."""
    pattern = re.compile(r'http://(?!localhost|127\.0\.0\.1)')
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"Non-HTTPS URL in {path}"


def test_error_messages_safe():
    """Verify http_probe.py has credential redaction machinery."""
    probe_path = os.path.join(SRC_DIR, "probes", "http_probe.py")
    with open(probe_path) as fh:
        src = fh.read()
    assert "_redact_text" in src, "http_probe.py missing _redact_text() usage"
    assert "_endpoint_for_print" in src, (
        "http_probe.py missing _endpoint_for_print()"
    )


def test_no_eval_exec():
    """No eval() or exec() in source."""
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
                    raise AssertionError(f"eval/exec found in {path}")
