# Contributors

This project exists thanks to its contributors.

## Contributors

- Gregory Beam (@KI7MT) — Project lead, architecture, packaging, documentation

## Contribution Checklist

When contributing new code, documentation, or other resources, please ensure:

1. **Coding Standards**
   - Follow standard **Java 21 + JavaFX** practices.
   - Add **Javadoc comments** for all public classes, methods, and fields.
   - Ensure code builds with `mvn clean verify` (or Gradle equivalent if adopted).
   - Run all unit tests (`mvn test`) before submitting changes.

2. **Documentation Standards**
   - Use **lowercase filenames** in `docs/` (e.g., `troubleshooting.md`).
   - Update `mkdocs.yml` to include new docs under the correct `nav` section.
   - Verify that all internal links in Markdown files resolve correctly.
   - Copy root-level files (`CHANGELOG.md`, `LICENSE.md`) into `docs/` if you want them visible on GitHub Pages.
   - For developer docs, generate and publish **Javadocs**.

3. **Releases**
   - Update `CHANGELOG.md` with changes.
   - Bump the project version in `pom.xml` (or `build.gradle`).
   - Tag the release (`git tag vX.Y.Z && git push --tags`).
   - Smoke test the built artifact locally before publishing.

4. **General**
   - Keep commits atomic and meaningful.
   - Prefer PRs from feature branches.
   - Be respectful and collaborative.

Thank you for helping improve **ADIF MCP (Java)** 🚀
