# Concepts Overview

- **Core MCP**: declares canonical ADIF types + read/write tools
- **Plugins**: add LoTW/eQSL capabilities via separate MCP servers
- **Safety**: schemas/validators sit at the boundary (no raw access)

Plugins
- Common in developer-first frameworks and ecosystems where you’re extending the core with extra functionality.
- Examples: MkDocs plugins, Pre-commit hooks, pytest plugins.
- Implies that they “hook into” the core and may follow a standardized API.
- Pro: Familiar to devs.
- Con: Sounds very dev-internal, less approachable to end users.

⸻

Integrations
- Common in user-facing platforms and SaaS ecosystems.
- Examples: GitHub Integrations, Slack Integrations, Zapier Integrations.
- Implies “this connects our tool with an external service”.
- Pro: Clear to hams/operators — “this integrates LoTW with MCP”.
- Con: Less precise if you eventually add internal extensions that aren’t really external integrations.

⸻

Modules / Extensions
- Neutral naming used in Python, Node, etc.
- Examples: Django “apps”, VS Code “extensions”.
- Pro: Generic, flexible.
- Con: Ambiguous unless you define it well.

⸻

What the ADIF/MCP ecosystem is closest to
- Since LoTW, eQSL, QRZ, logging apps are all external services that MCP connects to…
- “Plugins” would make sense if you were exposing a developer API for others to build custom code inside MCP.
