# ADIF-MCP Project Manifesto (v0.3.7)

## 1. Mission & Philosophy
- **The "Leveler":** This project provides local AI QSO analysis for the "Average" ham, bypassing proprietary "Cathedral" clouds.
- **Sovereignty:** All data processing is local-first. We prioritize privacy and operator control.
- **Legacy:** This is the successor to the JTSDK mindset. We respect the standards of pioneers like Joe Taylor (K1JT) and his team.

## 2. Technical Bedrock
- **Language:** Python 3.11+ (Reverted from Java for high-fidelity AI alignment).
- **Toolchain:** Managed via `uv`. Strict adherence to `mypy` typing and `ruff` formatting.
- **Validation:** 100% docstring coverage and Pydantic-driven ADIF models.
- **Protocol:** Model Context Protocol (MCP) using the `FastMCP` framework.

## 3. The "Sovereign" Guardrails
- **No Hallucinations:** Always refer to the validated Pydantic models in `src/adif_mcp/models/` for ADIF field definitions.
- **No Java:** The Java branch is archived noise. Do not suggest or implement Java logic.
- **Protocol Integrity:** Maintain strict compliance with ADIF 3.1.5+ specifications.
- **Human-in-the-Loop:** Tools are assistants for the Operator (KI7MT), not autonomous replacements.

## 4. Operational Context
- **Primary Node:** Mac Mini (UNIX-native).
- **Field Test Node:** Windows (85% majority ham environment).
- **Environment:** If the "Smoke-All" tests fail, the signal is lost. Fix the bedrock before building the gateway.

## CRITICAL: Type Safety & Formatting
- **Zero Tolerance:** All generated Python must pass `mypy --strict` and `ruff check` and `interrogate`.
- **Type Hints:** Use explicit type hints for all function signatures and variables. No `Any` unless absolutely necessary.
- **Pydantic First:** Always use existing Pydantic models from `src/adif_mcp/models/` for data structures.
- **First-Time Right:** Do not provide "draft" code. Only output code that meets the v0.3.7 smoke-all standards on the first pass.
- **Concrete Signatures:** Write logic to be Pydantic-valid first. Don't get bogged down in complex generic types; keep the signatures simple and concrete.
