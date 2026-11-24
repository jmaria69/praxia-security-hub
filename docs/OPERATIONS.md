# Praxia Security Hub — Operations Runbook

## Daily Operations
### 1. Checking Platform Status
```bash
./scripts/praxia-security status
```
Outputs the active status of the platform, count of registered SaaS products, open security incidents, and health of the BLA protection engine.

### 2. Inspecting Project Security Configuration
```bash
./scripts/praxia-security projects inspect adminapp
```

### 3. Running Pre-Flight Exposure Audits
```bash
./scripts/praxia-security protection check adminapp
```

### 4. Interactive Privacy Scan
```bash
./scripts/praxia-security privacy scan --text "Texto a inspeccionar"
```

## Emergency Procedures
### Fail-Closed Incident Response
When a developer or agent accidentally submits an API key or database credential:
1. Praxia Gateway immediately rejects the request with HTTP 403 `FAIL_CLOSED_TRIGGERED`.
2. An incident is logged to SQLite (`data/praxia_security.db`).
3. View open incidents via CLI or the Audit Center dashboard:
```bash
curl -s http://127.0.0.1:8888/api/audit/incidents
```
