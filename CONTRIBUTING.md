# Contributing to wspr-ai-lite

Thank you for your interest in contributing!
This project is open to contributions from the ham radio and open source community.

## Development Setup

1. Clone the repo:
   ```bash
   git clone git@github.com:KI7MT/adif-mcp.git
   cd adif-mcpe
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install development dependencies:
   ```bash
   make setup-dev
   ```

4. Run tests:
   ```bash
   make test
   ```

## Contribution Workflow

1. **Fork** the repository.
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Commit your changes**:
   - Follow conventional commits when possible (`fix:`, `feat:`, `docs:`, etc.).
   - Ensure pre-commit hooks and tests pass:
     ```bash
     pre-commit run --all-files
     make test
     ```
4. **Push your branch** and open a **Pull Request**.

## Code Style & Checks

- Code is formatted with **black** and **isort**.
- **Docstrings** are required (enforced with `interrogate`).
- Pre-commit hooks run automatically:
  - Trailing whitespace
  - EOF fixes
  - YAML/JSON/TOML validation
  - Docstring coverage
  - Artifact blocking (no `site/`, DuckDB, etc. in commits)

## Smoke Tests

Before tagging a release, please run:

```bash
make smoke-test
```

## Commit Message Guidelines

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

## 👥 Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of people who have helped shape this project.

## 📜 License

By contributing, you agree that your contributions will be licensed under the [LICENSE](LICENSE) of this repository.
