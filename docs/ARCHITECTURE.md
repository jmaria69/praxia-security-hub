# Praxia Security Hub — Architecture Specification

## 1. Executive Summary
**Praxia Security Hub** is the centralized software protection and LLM privacy enforcement platform for Praxia Labs. It operates as a dual-engine security system:
1. **Motor A — Software Protection (BLA Adapter):** Defensive adversarial shield against AI-assisted reverse-engineering agents (REA), preserving build outputs and verifying runtime execution equivalence.
2. **Motor B — LLM Privacy Gateway:** High-performance proxy intercepting prompts before upstream LLM forwarders (Headroom & OmniRoute), detecting PII and secrets, and executing AES-256-GCM reversible pseudonymization.

```
                              +-------------------------+
                              |   AI Development Agent  |
                              |  (Claude Code / Cursor) |
                              +------------+------------+
                                           |
                                           v
                              +-------------------------+
                              |  Praxia Privacy Gateway |
                              |     (127.0.0.1:8888)    |
                              |  - Secret Scanner       |
                              |  - Presidio PII Engine  |
                              |  - Token Vault AES-GCM  |
                              +------------+------------+
                                           |
                                           v
                              +-------------------------+
                              |     Headroom Proxy      |
                              |     (127.0.0.1:8787)    |
                              +------------+------------+
                                           |
                                           v
                              +-------------------------+
                              |    OmniRoute Router     |
                              |    (127.0.0.1:20128)    |
                              +------------+------------+
                                           |
                                           v
                              +-------------------------+
                              |      LLM Providers      |
                              | Anthropic/OpenAI/Gemini |
                              +-------------------------+
```

## 2. Core Components
- **Project Registry (`backend/core/project_registry.py`):** Multi-tenant SaaS configuration with per-project isolation and granular policies.
- **BLA Adapter (`backend/protection/bla_adapter/`):** Wrapper for Blind LLM Agents CLI (`bla-agents`), executing audit, protect, and verify pipelines without source modification.
- **Artifact Manager (`backend/protection/artifact_manager/`):** Immutable snapshot storage maintaining SHA-256 integrity trees and instant rollback capabilities.
- **Token Vault (`backend/privacy/token_vault/`):** Authenticated AES-256-GCM encrypted mapping store providing surrogate tokens (`[PERSON_001]`, `[EMAIL_001]`) with session-scoped isolation.
- **Orchestration Engine (`backend/orchestration/proxy_engine.py`):** Real-time SSE streaming transformer and de-pseudonymization engine.
