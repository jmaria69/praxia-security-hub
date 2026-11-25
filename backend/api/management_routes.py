"""API Routes for Project Registry & BLA Protection & Privacy Controls."""
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from backend.core.project_registry import project_registry, ProjectConfig
from backend.protection.bla_adapter.cli_runner import bla_runner
from backend.protection.artifact_manager.store import artifact_manager
from backend.protection.verification.verifier import verifier
from backend.privacy.gateway.processor import privacy_processor
from backend.privacy.token_vault.vault import token_vault
from backend.audit.logger import audit_logger
from backend.security.auth import get_current_user, User, require_role
from backend.security.validators import validate_safe_path

router = APIRouter(prefix="/api", tags=["Praxia Security Hub Management"])

class ScanRequest(BaseModel):
    text: str
    project_id: str = "default"
    session_id: str = "session_001"

class ProtectRequest(BaseModel):
    project_id: str
    target_path: Optional[str] = None
    intensity: str = "balanced"
    seed: str = "praxia-seed-v1"

class RollbackRequest(BaseModel):
    project_id: str
    build_id: str
    destination_path: str

# --- Projects Management ---
class OnboardRequest(BaseModel):
    project_path: str
    name: Optional[str] = None
    domain: Optional[str] = None
    repo_name: Optional[str] = None
    is_private: bool = False
    intensity: str = "balanced"
    skip_git: bool = False
    skip_deploy: bool = False
    dry_run: bool = False

@router.post("/projects/onboard")
async def onboard_project(req: OnboardRequest, user: User = Depends(get_current_user)):
    """Automates end-to-end project onboarding: BLA Hardening, GitHub sync, DNS & Vercel deployment."""
    try:
        from backend.orchestration.onboarder import project_onboarder
        res = project_onboarder.onboard(
            project_path=req.project_path,
            name=req.name,
            domain=req.domain,
            repo_name=req.repo_name,
            is_private=req.is_private,
            intensity=req.intensity,
            skip_git=req.skip_git,
            skip_deploy=req.skip_deploy,
            dry_run=req.dry_run
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_model=list[ProjectConfig])
async def list_projects(user: User = Depends(get_current_user)):
    return project_registry.list_projects()

@router.get("/projects/{project_id}", response_model=ProjectConfig)
async def get_project(project_id: str, user: User = Depends(get_current_user)):
    p = project_registry.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@router.post("/projects", response_model=ProjectConfig)
async def register_project(project: ProjectConfig, user: User = Depends(require_role("admin"))):
    return project_registry.register_or_update_project(project, user=user.username)

# --- BLA Protection ---
@router.get("/protection/doctor")
async def bla_doctor(user: User = Depends(get_current_user)):
    """Check BLA engine health and registered AI clients."""
    return bla_runner.doctor()

@router.post("/protection/audit")
async def bla_audit_target(project_id: str, target_subpath: Optional[str] = None, user: User = Depends(get_current_user)):
    p = project_registry.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    
    target = Path(p.root_path)
    if target_subpath:
        target = target / target_subpath
    
    try:
        report = bla_runner.audit(target)
        audit_logger.log_event(
            event_type="BLA_AUDIT",
            action="AUDIT_EXECUTED",
            severity="INFO",
            project_id=project_id,
            user=user.username,
            details={"target": str(target), "exposureScore": report.get("exposureScore", 0)}
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/protection/protect")
async def bla_protect_artifact(req: ProtectRequest, user: User = Depends(require_role("operator"))):
    """
    Execute BLA protection:
    1. Preserves original into immutable snapshot
    2. Runs BLA protection into isolated build folder
    3. Verifies invariants and runtime equivalence
    """
    p = project_registry.get_project(req.project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    target = Path(req.target_path) if req.target_path else Path(p.root_path) / (p.technology.build_output or "dist")
    if not target.exists():
        raise HTTPException(status_code=400, detail=f"Target path does not exist: {target}")

    # Create safe snapshot
    build_id, orig_backup, prot_target = artifact_manager.create_snapshot(
        project_id=req.project_id,
        source_artifact_path=target,
        intensity=req.intensity
    )

    # Execute protection
    protect_result = bla_runner.protect(
        input_path=orig_backup,
        output_path=prot_target,
        intensity=req.intensity,
        seed=req.seed
    )

    # Verification
    verification_result = verifier.verify_runtime_equivalence(orig_backup, prot_target)

    # Record manifest
    manifest = artifact_manager.record_manifest(
        build_id=build_id,
        project_id=req.project_id,
        original_path=orig_backup,
        protected_path=prot_target,
        intensity=req.intensity,
        verification_result=verification_result
    )

    return {
        "status": "PROTECTED",
        "build_id": build_id,
        "manifest": manifest,
        "verification": verification_result,
        "bla_metrics": protect_result.get("metrics", {})
    }

@router.post("/protection/rollback")
async def bla_rollback(req: RollbackRequest, user: User = Depends(require_role("admin"))):
    dest = Path(req.destination_path)
    success = artifact_manager.rollback(req.project_id, req.build_id, dest)
    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed: snapshot not found")
    return {"status": "SUCCESS", "message": f"Successfully restored {req.build_id} to {dest}"}

# --- Privacy & Token Vault ---
@router.post("/privacy/scan")
async def privacy_scan(req: ScanRequest, user: User = Depends(get_current_user)):
    """Dry-run scan of prompt for PII, secrets, and classification."""
    p = project_registry.get_project(req.project_id)
    policy = p.privacy.model_dump() if p else {}
    result = privacy_processor.process_prompt(
        text=req.text,
        project_id=req.project_id,
        session_id=req.session_id,
        project_policy=policy
    )
    return result

@router.get("/privacy/token-vault/status")
async def token_vault_status(user: User = Depends(get_current_user)):
    return {
        "active_tokens_count": len(token_vault._vault_store),
        "algorithm": "AES-256-GCM",
        "ttl_seconds": 86400,
        "status": "OPERATIONAL"
    }

# --- Audit & Incidents ---
@router.get("/audit/events")
async def list_audit_events(limit: int = 50, project_id: Optional[str] = None, user: User = Depends(get_current_user)):
    return audit_logger.list_events(limit=limit, project_id=project_id)

@router.get("/audit/incidents")
async def list_incidents(limit: int = 50, project_id: Optional[str] = None, user: User = Depends(get_current_user)):
    return audit_logger.list_incidents(limit=limit, project_id=project_id)
