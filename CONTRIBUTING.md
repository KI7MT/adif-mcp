# Contributing to ADIF-MCP

Thank you for your interest in contributing! This project is open to contributions from the ham radio and open source community.

## Contributing Philosophy

>"Pretty Code, Pretty Output, Iterative Docs"
>
>An wise old friend and mentor once told me: “We need pretty code and pretty output — and good documentation takes *lots* of iterations.”

It’s a simple rule of thumb:
- **Pretty code** keeps contributors sane.
- **Pretty output** gives users confidence.
- **Pretty docs** bridge the two, but take more work and refinement than once would think.

Following this mindset helps keep the project consistent, approachable, and operator-friendly.

>Contributing Tip: “See [TODO.md]()TODO.md) for backlog ideas. Concrete items should be filed as Issues when ready.”

## Prerequisites

To contribute to **ADIF-MCP (Java)**, you will need:

- A working **Java 21 SDK** (OpenJDK or vendor equivalent).
- **Gradle** (wrapper `./gradlew` is included, so a global install is optional).
- For documentation: **Python ≥3.11** with [UV](https://docs.astral.sh/uv/) for MkDocs builds.

---

## Development Setup

Clone the repository and switch into the project directory:

~~~bash
git clone git@github.com:KI7MT/adif-mcp.git
cd adif-mcp
~~~

## Base Directory Layout
```text
adif-mcp/
├── build.gradle.kts        # Gradle build script (Kotlin DSL)
├── settings.gradle.kts     # Gradle settings (project name, etc.)
├── gradle/                 # Gradle wrapper support files
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew                 # Gradle wrapper script (Unix)
├── gradlew.bat             # Gradle wrapper script (Windows)
├── src/
│   ├── main/
│   │   ├── java/           # All Java source (packages under here)
│   │   │   └── com/ki7mt/adifmcp/...
│   │   ├── resources/      # Non-code resources (icons, configs, schema JSON)
│   │   └── javafx/         # (optional) FXML or UI resources
│   └── test/
│       ├── java/           # Unit + integration tests
│       │   └── com/ki7mt/adifmcp/...
│       └── resources/      # Test resources (fixtures, ADIF samples, etc.)
├── docs/                   # MkDocs source
│   ├── index.md
│   └── ...
├── ROADMAP.md
├── Makefile                # (docs build targets etc.)
└── .gitignore
```




---

### Build & Test with Gradle

The project uses **Gradle** as the build tool. All major checks and tasks are wired into Gradle.

~~~bash
# Clean and build the entire project
./gradlew clean build

# Run unit tests
./gradlew test

# Generate Javadocs
./gradlew javadoc

# Verify code formatting and style (Spotless/Checkstyle if configured)
./gradlew check
~~~

---

### Pre-Commit & PR Checklist

Before submitting a PR, ensure:

- All builds and tests pass (`./gradlew clean build`).
- Javadocs build without errors (`./gradlew javadoc`).
- Docs site builds cleanly (`make docs-build`).
- No unformatted code (`./gradlew spotlessApply` if Spotless is enabled).

Minimal validations:

~~~bash
./gradlew clean build
make docs-build
~~~

---

### CLI Validation Testing

ADIF-MCP for Java will provide CLI entry points via the `application` plugin or custom launchers.
Validate locally with:

~~~bash
./gradlew run --args="--help"
./gradlew run --args="version"
./gradlew run --args="manifest validate"
~~~

---

### Optional but Recommended

~~~bash
# Build an installable distribution (scripts + libs)
./gradlew installDist

# Create a standalone fat/uber JAR
./gradlew shadowJar
~~~

---

## Code Style & Checks

- Code is formatted and linted using Gradle plugins (e.g., **Spotless**, **Checkstyle**, or **PMD**).
- **Javadocs** are required for all public classes and methods.
- Pre-commit hooks (if enabled) should be run with:

~~~bash
pre-commit run --all-files
~~~

---

## Documentation Style Tips

When contributing to the docs (`/docs`):

- Always use `~~~` fences for code/diagram blocks.

Example:

~~~mermaid
graph LR
  A --> B
~~~

- **Mermaid Diagrams**
  - Use `~~~mermaid` fences.
  - Wrap labels with spaces or HTML in quotes:

✅ Correct:

~~~mermaid
flowchart LR
  A["Operator<br/>(Ask in plain English)"] --> B["Agent / LLM<br/>(Chat or Voice)"]
~~~

❌ Incorrect:

~~~mermaid
flowchart LR
  A[Operator<br/>(Ask in plain English)] --> B[Agent / LLM (Chat or Voice)]
~~~

---

## Summary

- **Gradle (`./gradlew`)** is the single source of truth for builds, tests, and checks.
- **MkDocs** continues to power the User Guide (`make docs-build`, `make docs-serve`).
- Keep commits atomic, follow Javadoc conventions, and respect coding standards.

## 👥 Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of people who have helped shape this project.

## 📜 License

By contributing, you agree that your contributions will be licensed under the [LICENSE](LICENSE) of this repository.
