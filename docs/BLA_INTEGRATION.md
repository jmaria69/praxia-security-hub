# Praxia Security Hub — BLA Integration & Counter-REA Shield

## 1. Official BLA Overview
**Blind LLM Agents (BLA)** by `qybaihe/bla` (`bla-agents` on npm) provides adversarial defense against automated reverse-engineering agents (REA).

### Defense Trilogy
1. **Poison:** Injects domain-plausible decoy metadata, honey routes and synthetic telemetry.
2. **Exhaust:** Satures AST parsers and context windows with algorithmic tarpits (>1,200x token amplification).
3. **Hallucinate:** Induces AI agents into incorrect architecture hypotheses while preserving 100% execution equivalence for legitimate users.

## 2. Praxia BLA Adapter Architecture
The adapter resides in `backend/protection/bla_adapter/`:
- **`cli_runner.py`:** Wrapper for `npx -y bla-agents` commands with `--json` output parsing.
- **`artifact_manager/store.py`:** Manages safe staging directories:
  - Original builds are copied to `data/bla_storage/{project}/{build_id}/original/`
  - Hardened artifacts are output to `.../protected/`
  - Originals are NEVER modified in-place during default build pipelines.
- **`verification/verifier.py`:** Automated post-protection runtime test executing original vs protected artifacts in Node.js / Python and verifying identical stdout.

## 3. Rollback Runbook
If an artifact fails post-protection verification:
```bash
praxia-security protection rollback <project_id> <build_id> <destination_path>
```
Or via REST API:
```http
POST /api/protection/rollback
{"project_id": "adminapp", "build_id": "build_adminapp_20261124_210000", "destination_path": "/path/to/dist"}
```
