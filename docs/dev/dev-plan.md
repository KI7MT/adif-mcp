# Backend Implementation Plan (Java v0.4.x)

> **Note:** This plan replaces the earlier Python-based development plan.
> It outlines the staged implementation of the new Java backend (v0.4.x),
> focusing on CLI-first services, provider integration, and sync logic.
> The JavaFX UI will only be layered on after the backend is fully stable.

---

## Current Status (0.4.1-SNAPSHOT)
- **Modules in place**: `spi`, `core`, `cli` (all build & run cleanly).
- **CLI**: Provides `--help`, `--version`, `providers`, and `serve` stubs.
- **Persona & Credentials**: Core model present, lint-clean.
- **Javadoc**: Per-module + aggregate (`javadocAll`) staged to `docs/javadoc/`.
- **Docs**: MkDocs integrated, Javadocs embedded via iframe pages in `dev/api/`.
- **Sanity-check workflow**: Runs clean locally (Gradle build, CLI runs, Javadoc).


## Next Steps
1. **Expand Core**:
- Implement persona persistence and validation.
- CredentialStore backends (file/JSON, not only in-memory).

2. **SPI**:
- Finalize `ProviderClient` contract with fetch/sync semantics.
- Lock API versioning before publishing.

3. **Providers**:
- eQSL prototype first, others later.

4. **Sync/Server**:
- Add module stubs for scheduling + MCP server HTTP API.

5. **CI/CD**:
- Publish snapshot artifacts.
- Harden smoke tests with JUnit.

**CLI commands available**
```bash
- `adif-mcp --help` – shows subcommands
- `adif-mcp providers` – lists installed providers (via `ServiceLoader`)
- `adif-mcp ui` – launches JavaFX app (dev: via reflection; packaged: separate launcher)
- `adif-mcp serve` – server stub (prints placeholder)
```

**Provider registration**
```bash
- eQSL provider **registered and discovered**
- Service file: `META-INF/services/com.ki7mt.adifmcp.providers.ProviderFactory`
- Factory: `com.ki7mt.adifmcp.providers.eqsl.EqslProviderFactory`
- Current capability: **pull-only** (stub)
```

**Documentation integrated**
```bash
- Aggregated Javadoc built by `./gradlew javadocAll` → output to `docs/javadoc/`
- MkDocs **strict** build succeeds; nav points to `javadoc/index.html`
- `make docs-serve` serves site with Javadoc included
```

**Sanity-check workflow**
```bash
# Top-level smoke gate (Makefile target: sanity-check)
./gradlew clean build
./gradlew --no-configuration-cache :cli:run --args="--help"
./gradlew --no-configuration-cache :cli:run --args="providers"
./gradlew --no-configuration-cache :ui:run
./gradlew javadocAll
```

### Notes
- Gradle toolchain: Java 21; JavaFX via org.openjfx.javafxplugin.
- During development, :cli depends on :providers:provider-eqsl with implementation(...) for discovery.
- Next feature target: Credentials v1 (core API + cli creds), then eQSL fetch implementation.

## 1. Credentials (OS-native + fallback)
- [ ] Define `Credentials` model (`personaId`, `providerId`, `authType`, fields)
- [ ] Implement `CredentialStore` interface (`put`, `get`, `delete`, `doctor`)
- [ ] macOS: shell out to `security` CLI for Keychain
- [ ] Linux: try `secret-tool` (DBus); fallback to portable
- [ ] Windows: stub for Credential Manager; fallback to portable
- [ ] Portable fallback: AES-GCM encrypted file in `state/creds/`
- [ ] CLI: `creds set|get|delete|list|doctor`
- [ ] Ensure key format is `adif-mcp/<persona>:<provider>`

---

## 2. Providers (registry + enable/disable)
- [ ] Define provider descriptor JSON (`resources/providers/*.json`)
- [ ] Implement `ProviderRegistry` to load descriptors
- [ ] Track enabled/disabled per persona in `state/providers/`
- [ ] Implement `ProviderClient` interface (`ping`, `authCheck`, `fetchActivity`, `pushQso`)
- [ ] CLI: `provider list|enable|disable|doctor`
- [ ] Implement first real clients: **QRZ** and **Clublog**

---

## 3. Personas (multi-callsign, configs)
- [ ] Define `Persona` model (`id`, `callsigns`, `defaultStation`)
- [ ] Persist as `config/personas/<persona>.yaml`
- [ ] Implement `PersonaService` for CRUD
- [ ] CLI: `persona add|list|show|remove|set-active|doctor`

---

## 4. ADI → JSON
- [ ] Implement `AdifReader` to parse `.adi` into normalized records
- [ ] Define `AdifRecord` POJO (strict but logs unknowns)
- [ ] Implement `AdifWriter` later for export
- [ ] CLI: `convert --in … --out …`
- [ ] Validate with sample ADI logs

---

## 5. Sync Core (MCP plumbing)
- [ ] Define `SyncState` under `state/sync/<persona>/<provider>.json`
- [ ] Implement dedupe by hash/time
- [ ] Implement `sync pull` (dry-run + real)
- [ ] Implement `sync push` (dry-run + real)
- [ ] CLI: `sync now|pull|push|status`
- [ ] Use `resources/mapping/usage.json` for transforms

---

## 6. JavaFX UI (thin shell over backend)
- [ ] Status pane: persona, providers, last sync, “Sync Now”
- [ ] Credential management dialogs → reuse `CredentialStore`
- [ ] Log viewer tailing `logs/`
- [ ] No new logic — strictly a frontend to CLI services

---

## Sequencing (2–3 day slices)
1. CredentialStore (macOS + portable fallback)
2. ProviderRegistry + enable/disable + doctor
3. PersonaService + CRUD + active persona
4. ADI Reader + normalized JSON + CLI converter
5. SyncState + pull/push (dry-run first)
6. Real provider integration (QRZ, Clublog)
7. Wire JavaFX status + creds screen

---

## Testing Strategy
- Unit: POJOs and services without network
- Integration: provider stubs for offline tests
- Doctor: every `doctor` command checks creds, provider reachability, state


## Current Task — Credentials v1 (Java backend)

First milestone: implement secure credential storage and CLI surfaces.
Focus on macOS Keychain + portable encrypted fallback. Windows/Linux native stores will come later.

### Scope
- `com.ki7mt.adifmcp.credentials` (models, interfaces, adapters)
- `com.ki7mt.adifmcp.cli.creds` (picocli subcommands)

### Checklist

- [ ] **Models**
    - [ ] `Credentials` POJO (`personaId`, `providerId`, `authType`, fields map)
    - [ ] `AuthType` enum (`USERPASS`, `API_KEY`)

- [ ] **Service API**
    - [ ] `CredentialStore` interface: `put`, `get`, `delete`, `list`, `doctor`
    - [ ] `DoctorReport` and `CredentialRef` helper models

- [ ] **Adapters**
    - [ ] macOS Keychain adapter via `security` CLI
    - [ ] Portable encrypted file store under `state/creds/` (AES-GCM + PBKDF2)
    - [ ] Stubs for Windows Credential Manager / Linux Secret Service

- [ ] **Selection logic**
    - [ ] Store resolver: explicit `--store`, else OS default, else fallback to portable
    - [ ] Log which backend is used

- [ ] **CLI commands**
    - [ ] `adif-mcp creds set`
    - [ ] `adif-mcp creds get`
    - [ ] `adif-mcp creds delete`
    - [ ] `adif-mcp creds list`
    - [ ] `adif-mcp creds doctor`

- [ ] **Testing**
    - [ ] Unit: in-memory fake for `CredentialStore`
    - [ ] Integration: portable store round-trip, bad passphrase, tamper detection
    - [ ] Integration: macOS Keychain add/get/delete with JSON payload
    - [ ] CLI: end-to-end set/get/delete/list/doctor (with redaction verified)
    - [ ] Security: grep logs/artifacts for secrets (must be redacted)

### Acceptance
- macOS: Keychain round-trip works with JSON payload
- Portable: encrypt/decrypt works, wrong passphrase rejected
- CLI: list shows refs only (no secrets), doctor prints a clear checklist
- Logs: never contain secrets
- Exit codes: non-zero on failure
