# Backend Implementation Plan (Java v0.4.x)

> **Note:** This plan replaces the earlier Python-based development plan.
> It outlines the staged implementation of the new Java backend (v0.4.x),
> focusing on CLI-first services, provider integration, and sync logic.
> The JavaFX UI will only be layered on after the backend is fully stable.
---

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
