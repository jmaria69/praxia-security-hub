"""Project Registry management for Praxia Labs SaaS ecosystem."""
import os
from pathlib import Path
from typing import Any, Optional
import yaml
from pydantic import BaseModel, Field
from backend.core.config import settings
from backend.security.validators import validate_safe_path, sanitize_identifier
from backend.audit.logger import audit_logger

class ProjectTechnology(BaseModel):
    frontend: Optional[str] = None
    backend: Optional[str] = None
    build_output: Optional[str] = None

class ProtectionPolicy(BaseModel):
    enabled: bool = True
    engine: str = "bla"
    intensity: str = "balanced"
    preserve_originals: bool = True
    verify_invariants: bool = True
    auto_rollback_on_failure: bool = True
    exclude_patterns: list[str] = Field(default_factory=list)

class TokenVaultPolicy(BaseModel):
    enabled: bool = True
    session_scoped: bool = True
    ttl_seconds: int = 86400
    allow_depseudonymize: bool = True

class PrivacyPolicy(BaseModel):
    enabled: bool = True
    classification_default: str = "INTERNAL"
    fail_closed: bool = True
    token_vault: TokenVaultPolicy = Field(default_factory=TokenVaultPolicy)

class ProjectConfig(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    root_path: str
    technology: ProjectTechnology = Field(default_factory=ProjectTechnology)
    protection: ProtectionPolicy = Field(default_factory=ProtectionPolicy)
    privacy: PrivacyPolicy = Field(default_factory=PrivacyPolicy)
    allowed_providers: list[str] = Field(
        default_factory=lambda: ["anthropic", "openai", "gemini"]
    )
    last_audit_timestamp: Optional[str] = None
    last_protected_build: Optional[str] = None
    status: str = "REGISTERED"

class ProjectRegistry:
    def __init__(self, projects_dir: Optional[Path] = None):
        self.projects_dir = projects_dir or settings.PROJECTS_DIR
        os.makedirs(self.projects_dir, exist_ok=True)

    def list_projects(self) -> list[ProjectConfig]:
        projects = []
        for file_path in self.projects_dir.glob("*.yaml"):
            if file_path.name == "defaults.yaml":
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict) and "id" in data:
                        projects.append(ProjectConfig(**data))
            except Exception as e:
                # Log invalid yaml silently or record audit event
                continue
        return projects

    def get_project(self, project_id: str) -> Optional[ProjectConfig]:
        clean_id = sanitize_identifier(project_id)
        yaml_file = self.projects_dir / f"{clean_id}.yaml"
        if not yaml_file.exists():
            return None
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return ProjectConfig(**data)

    def register_or_update_project(self, project: ProjectConfig, user: str = "system") -> ProjectConfig:
        clean_id = sanitize_identifier(project.id)
        project.id = clean_id
        
        # Validate that the root path exists and is inside an allowed boundary
        validated_path = validate_safe_path(project.root_path)
        project.root_path = str(validated_path)

        yaml_file = self.projects_dir / f"{clean_id}.yaml"
        action = "UPDATE_PROJECT" if yaml_file.exists() else "REGISTER_PROJECT"

        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(project.model_dump(), f, default_flow_style=False, sort_keys=False)

        audit_logger.log_event(
            event_type="PROJECT_REGISTRY",
            action=action,
            severity="INFO",
            project_id=clean_id,
            user=user,
            details={"name": project.name, "root_path": project.root_path}
        )
        return project

    def delete_project(self, project_id: str, user: str = "system") -> bool:
        clean_id = sanitize_identifier(project_id)
        yaml_file = self.projects_dir / f"{clean_id}.yaml"
        if yaml_file.exists():
            yaml_file.unlink()
            audit_logger.log_event(
                event_type="PROJECT_REGISTRY",
                action="DELETE_PROJECT",
                severity="WARNING",
                project_id=clean_id,
                user=user
            )
            return True
        return False

project_registry = ProjectRegistry()
