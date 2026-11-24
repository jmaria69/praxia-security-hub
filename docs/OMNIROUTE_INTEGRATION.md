# Praxia Security Hub — OmniRoute & Headroom Integration

## 1. Local Infrastructure Topology
The current WSL2 development environment hosts:
- **Headroom Proxy:** `http://127.0.0.1:8787` (PID 510, `--tpm 50000 --memory --learn`)
- **OmniRoute Router:** `http://127.0.0.1:20128` (PID 508, user systemd service)
- **Praxia Privacy Gateway:** `http://127.0.0.1:8888`

## 2. Request Routing Pipeline
Development agents point their `OPENAI_BASE_URL` or `ANTHROPIC_BASE_URL` to Praxia Privacy Gateway (`127.0.0.1:8888`):
1. **Developer Agent -> Praxia Gateway (`8888`):** Inbound prompt arrives with headers `X-Praxia-Project` and `X-Praxia-Session`.
2. **Privacy Enforcement:** Gateway scans prompt for credentials (aborting if detected), substitutes PII with surrogates via Token Vault.
3. **Praxia Gateway -> Headroom (`8787`):** Sanitized prompt is sent to Headroom for context compaction, caching, and token optimization.
4. **Headroom -> OmniRoute (`20128`):** Headroom forwards to OmniRoute for smart provider routing and rate limiting.
5. **OmniRoute -> Upstream LLM:** Upstream provider (Anthropic Claude, OpenAI, etc.) processes prompt.
6. **Reverse Stream Handling:** As SSE chunks or JSON completions return, the Gateway restores surrogate tokens (`[PERSON_001]`) to original text before returning to the developer agent.

## 3. Fallback Mechanism
If Headroom is stopped for maintenance, the Gateway automatically falls back directly to OmniRoute at `http://127.0.0.1:20128` without dropping active developer sessions.
