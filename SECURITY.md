# Security Policy

## Supported Versions
Only the latest release of **adif-mcp** is actively supported.

## Reporting Vulnerabilities
Please report security issues **privately**:
- [security @ ki7mt.io]

Do **not** open a public GitHub Issue.

Provide:
- Steps to reproduce
- Impact assessment
- Affected versions

We acknowledge within 7 days, patch within 30 days.

## Known Limitations

- `parse_adif` reads arbitrary local file paths provided by the caller.
  Restrict to `.adi`/`.adif` files in v0.8.0.

## Disclosure
Once fixed, we will:
- Publish a patched release
- Update the CHANGELOG
- Credit reporters if desired
