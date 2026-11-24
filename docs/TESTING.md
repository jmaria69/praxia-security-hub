# Praxia Security Hub — Testing Guide

## Test Suite Structure
The test suite is organized into unit, integration, and security tests:
- `tests/unit/test_token_vault.py`: AES-256-GCM authenticated encryption, surrogate token uniqueness, session isolation, and restoration.
- `tests/unit/test_secret_scanner.py`: Shannon entropy calculation, high-precision regex matching for API keys, AWS credentials, and JWTs.
- `tests/unit/test_pii_detector.py`: Microsoft Presidio integration, Spanish DNI/NIE, phones, IBAN, and clinical health keywords.
- `tests/unit/test_project_registry.py`: Dynamic YAML project loader, schema validation, and path traversal defenses.
- `tests/integration/test_bla_adapter.py`: BLA doctor verification, snapshot isolation, protect, verify, and artifact rollback.
- `tests/integration/test_api_endpoints.py`: FastAPI REST API routes (`/health`, `/api/projects`, `/api/privacy/scan`, `/api/audit/events`).
- `tests/security/test_fail_closed.py`: Verification that secret leaks trigger an immediate fail-closed block.

## Running Tests
```bash
cd /home/jmari/proyectosIA/praxia-security-hub
.venv/bin/pytest tests/ -v
```
All 15 automated tests pass with 100% success.
