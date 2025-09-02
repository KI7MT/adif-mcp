"""HTTP GET probe engine with robust redaction, used by provider probes."""

# (rest of your current file unchanged)
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Any, List, Mapping, Optional, Tuple

EXIT_OK = 0
EXIT_HTTP_ERROR = 3
EXIT_NET = 4
EXIT_USAGE = 2


def _redact_text(s: str) -> str:
    """Final-pass redactor for any printed text."""
    secret_kvs = re.compile(
        r"(?i)\b("
        r"api(?:_key)?|apikey|api|key|"
        r"token|access_token|id_token|refresh_token|"
        r"password|passwd|pwd|secret|authorization"
        r")\s*=\s*([^&\s]+)"
    )
    return secret_kvs.sub(lambda m: f"{m.group(1)}=<redacted>", s)


def _endpoint_for_print(full_url: str) -> str:
    """Return path + ?query for printing; redact sensitive query values."""
    sensitive = {
        "password",
        "passwd",
        "pass",
        "pwd",
        "token",
        "access_token",
        "id_token",
        "refresh_token",
        "apikey",
        "api_key",
        "api",
        "key",
        "secret",
        "authorization",
    }
    p = urllib.parse.urlparse(full_url)
    endpoint = p.path or "/"
    if not p.query:
        return endpoint
    pairs = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    redacted = []
    for k, v in pairs:
        kl = k.lower()
        if kl in sensitive or any(
            x in kl for x in ("token", "secret", "passwd", "api", "key")
        ):
            redacted.append((k, "<redacted>"))
        else:
            redacted.append((k, v))
    return f"{endpoint}?{urllib.parse.urlencode(redacted)}"


def _build_url(base: str, query: Mapping[str, Any]) -> str:
    """Map Baee URL to target provider"""
    qs = urllib.parse.urlencode({k: str(v) for k, v in query.items()})
    sep = "&" if urllib.parse.urlparse(base).query else "?"
    return f"{base}{sep}{qs}" if qs else base


def _fetch(url: str, headers: Mapping[str, str], timeout: float) -> Tuple[int, bytes]:
    """Fetch contest from provider"""
    req = urllib.request.Request(url, headers=dict(headers), method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - outbound GET
        body = resp.read()
        return int(getattr(resp, "status", 200)), body


def execute(
    *,
    provider: str,
    url: str,
    headers: Mapping[str, str],
    query: Mapping[str, Any],
    timeout: float,
    verbose: bool = False,
) -> int:
    """Run a single GET probe and print the one-line result; return exit code."""
    full_url = _build_url(url, query)
    endpoint = _endpoint_for_print(full_url)
    try:
        status, body = _fetch(full_url, headers, timeout)
        if 200 <= status < 300:
            msg = f"[OK] {provider} GET {endpoint} http={status} bytes={len(body)}"
            print(_redact_text(msg))
            return EXIT_OK
        else:
            msg = f"[error] {provider} GET {endpoint} http={status} bytes={len(body)}"
            if verbose and len(body) <= 512:
                frag = body.decode(errors="replace")
                msg += f" body={frag!r}"
            print(_redact_text(msg), file=sys.stderr)
            return EXIT_HTTP_ERROR
    except Exception as e:
        msg = f"[error] {provider} GET {endpoint} net={type(e).__name__}: {e}"
        print(_redact_text(msg), file=sys.stderr)
        return EXIT_NET


def main(argv: Optional[List[str]] = None) -> int:
    """Compat CLI entry (useful for unit tests or -m invocation)."""
    p = argparse.ArgumentParser(description="GET-only probe (with redaction).")
    p.add_argument("--provider", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--headers-json", default="{}")
    p.add_argument("--query-json", default="{}")
    p.add_argument("--timeout", type=float, default=10.0)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    try:
        headers = json.loads(args.headers_json)
        query = json.loads(args.query_json)
        if not isinstance(headers, dict) or not isinstance(query, dict):
            raise ValueError("headers-json and query-json must be objects")
    except Exception as e:
        print(f"[error] bad JSON: {e}", file=sys.stderr)
        return EXIT_USAGE

    return execute(
        provider=args.provider,
        url=args.url,
        headers=headers,
        query=query,
        timeout=args.timeout,
        verbose=args.verbose,
    )
