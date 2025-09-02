# Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard for commit messages.
This makes it easier to understand project history and automatically generate changelogs.

### Format
- **type** → what kind of change this is.
- **scope** (optional) → area of the codebase (e.g., `ui`, `ingest`, `tools`, `docs`).
- **summary** → concise description (imperative, no period).

### Common Types
- **feat** → new feature
  _example_: `feat(ui): add reciprocal heard analysis panel`
- **fix** → bug fix
  _example_: `fix(ingest): correct band_code mapping for MF range`
- **docs** → documentation only
  _example_: `docs(schema): add canonical WSPR spots schema doc`
- **style** → formatting, whitespace, linter (no logic change)
- **refactor** → code restructuring without behavior change
- **perf** → performance improvement
- **test** → add or update tests
- **build** → build system or dependency changes
- **ci** → CI/CD workflows or pipelines
- **chore** → maintenance tasks, version bumps, release prep
  _example_: `chore(release): cut v0.3.6 tag`
- **revert** → undo a previous commit

### Examples
- `feat(tools): add verify --strict and --explain options`
- `fix(ui): handle missing rx_version gracefully`
- `docs: update roadmap for v0.4.0 planning`
- `chore(release): prepare v0.3.6`

---

💡 **Tip:** Keep summaries short (≤72 chars). Add details in a commit body if needed.

This ensures the package builds, installs, ingests, and launches the UI end-to-end.
