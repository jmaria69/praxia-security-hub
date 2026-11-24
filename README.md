# Praxia Security Hub

**Enterprise Security & LLM Privacy Platform for Praxia Labs**

Praxia Security Hub is a centralized security infrastructure engineered for Praxia Labs SaaS products (AdminApp, SIAM, Praxia AgeVerify, Praxia Radar AI, CRM IT, and saludOS). It provides two independent defensive engines:

- **Motor A — Software Protection:** Integration with Blind LLM Agents (BLA) to inject Counter-REA adversarial shields against automated AI decompilers.
- **Motor B — LLM Privacy Gateway:** Pre-flight interception gateway between development agents and upstream routers (Headroom & OmniRoute), performing secret scanning, Presidio PII detection, AES-256-GCM reversible pseudonymization, and fail-closed security enforcement.

## Key Features
- **Project Registry:** Multi-project YAML configuration with granular classification and protection policies.
- **Fail-Closed Policy:** Automatically halts requests attempting to transmit credentials, API keys, or private certificates.
- **Reversible Token Vault:** Replaces personal identities with surrogate tokens (`[PERSON_001]`, `[EMAIL_001]`) and restores them in authorized responses.
- **BLA Integration:** Non-destructive hardening with automated runtime equivalence verification and instant rollback.
- **OmniRoute & Headroom Interceptor:** Sits transparently on `127.0.0.1:8888`, forwarding clean requests to Headroom (`127.0.0.1:8787`) and OmniRoute (`127.0.0.1:20128`).
- **Web Dashboard:** Clean, responsive UI with Praxia Labs brand palette (`#0A66C2`, `#0052CC`, `#F3F6F8`, `#FFFFFF`, `#10B981`).
- **CLI (`praxia-security`):** Command-line utility for status, auditing, scanning, and inspection.

## Quickstart
```bash
cd /home/jmari/proyectosIA/praxia-security-hub
./scripts/praxia-security status
./scripts/praxia-security doctor
```

Run test suite:
```bash
.venv/bin/pytest tests/ -v
```
All 15 tests pass with 100% success.
