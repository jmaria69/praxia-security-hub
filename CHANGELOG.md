# Changelog — Praxia Security Hub

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
