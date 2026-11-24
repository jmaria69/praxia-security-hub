# Headroom Integration — Praxia Security Hub

Headroom acts as the semantic caching and prompt optimization layer operating on `127.0.0.1:8787`.

## Data Flow
```
Development Agent -> Praxia Privacy Gateway (8888) -> Headroom (8787) -> Upstream Provider
```

1. **Pre-flight Interception:** Praxia Hub detects secrets (fail-closed) and pseudonymizes PII.
2. **Forwarding:** Clean prompt with surrogate tokens is forwarded to Headroom on `http://127.0.0.1:8787/v1/chat/completions`.
3. **Response Restoration:** Praxia Hub intercepts Headroom's response and dynamically restores surrogate tokens back to their original values before returning the response to the agent.
