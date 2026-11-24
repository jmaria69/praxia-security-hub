# Changelog — Praxia Security Hub

## [1.1.0] - 2026-11-24

### Added
- **MCP Server Integration (`scripts/praxia-mcp`, `backend/mcp/server.py`):**
  - Standard JSON-RPC stdio protocol compatible with Claude Code, Cursor, Codex, OpenCode and Gemini CLI.
  - Exposes `praxia_status`, `praxia_list_projects`, `praxia_inspect_project`, `praxia_scan_prompt`, `praxia_audit_artifacts`, and `praxia_get_audit_events`.
- **Complete CLI Operations (`scripts/praxia-security`):**
  - `praxia-security audit <project_id>`: Query incidents and audit trail.
  - `praxia-security protection dry-run <project_id>`: Pre-flight REA simulation without filesystem changes.
  - `praxia-security protection harden <project_id> --confirm`: Safe isolated snapshot copy, BLA protect, equivalence verification, and cryptographic manifest generation.
  - `praxia-security reports generate`: Markdown/JSON global compliance and security reports.
- **CI/CD Hardening Action & Pipeline (`.github/`):**
  - Composite GitHub Action `.github/actions/praxia-secure-publish/action.yml`.
  - Reusable workflow `.github/workflows/praxia-pipeline.yml` enforcing secret scanning, privacy checks, BLA hardening, and manifest generation.
- **Enterprise Security Policies (`policies/`):**
  - `policies/data_classification.yaml` and `policies/fail_closed_rules.yaml`.
- **Integrations Documentation & Configs (`integrations/`):**
  - Setups for Claude Code, Codex, OpenCode, Gemini, Headroom, and OmniRoute.
- **Docker Deployment:**
  - `docker/Dockerfile.backend` with Python 3.10 and Node.js 20 LTS for BLA execution.
- **Unit & Integration Tests:**
  - Expanded test suite from 15 to 28 tests (100% passing).

## [1.0.0] - 2026-11-24

### Added
- **Phase 0 Audit:** Initial environment discovery in WSL2 Ubuntu 22.04 LTS, RTX 5080, OmniRoute (port 20128), and Headroom (port 8787).
- **Core Architecture:**
  - Project Registry supporting YAML configuration per project (`projects/*.yaml`).
  - Cryptographic and structured audit logging engine in SQLite.
  - Strict filesystem path traversal and command injection defenses.
- **Motor A (Software Protection):**
  - BLA Adapter wrapping `npx bla-agents` CLI with JSON output parsing.
  - Artifact Manager preserving originals with immutable SHA-256 hashing.
  - Runtime equivalence verifier and rollback engine.
- **Motor B (LLM Privacy Gateway):**
  - Microsoft Presidio PII Analyzer with custom Spanish regex recognizers (DNI/NIE, IBAN, phones, medical).
  - Secret Scanner detecting API keys (Anthropic, OpenAI, AWS, GitHub) and Shannon entropy thresholds.
  - Reversible Token Vault with authenticated AES-256-GCM encryption.
  - Fail-Closed policy enforcement blocking unauthorized credential transmissions.
- **Integrations:**
  - Reverse proxy engine forwarding to Headroom (8787) and OmniRoute (20128).
  - Server-Sent Events (SSE) streaming support with de-pseudonymization.
- **Web Dashboard:**
  - React 18 + TypeScript + Tailwind CSS dashboard with Praxia Labs brand palette.
  - Overview, Project Security, BLA Manager, Privacy Center, Audit Center, and Settings views.
- **CLI (`praxia-security`):**
  - `status`, `projects list`, `projects inspect`, `doctor`, `privacy scan`, `protection check`.
- **Documentation:** Full technical reference in `docs/`.
