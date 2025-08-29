# Concepts Overview

- **Core MCP**: declares canonical ADIF types + read/write tools
- **Integrations**: add LoTW/eQSL/QRZ/Club Log via separate MCP servers
- **Safety**: schemas/validators sit at the boundary (no raw access)

> Looking for the “why”? See **[Why ADIF-MCP Matters](why-matters.md)**.

---

~~~mermaid
flowchart LR
  A["Operator<br/>(Ask in plain English)"] --> B["Agent / LLM<br/>(Chat or Voice)"]
  B --> C["ADIF-MCP<br/>Spec-compliant Backbone"]
  C --> D[LoTW]
  C --> E[eQSL]
  C --> F[QRZ]
  C --> G[Club Log]

  classDef service fill:#eef,stroke:#36c,stroke-width:1px;
  class D,E,F,G service;
~~~
