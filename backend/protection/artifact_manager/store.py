"""Artifact Manager: Preserves originals, computes SHA-256 and enables rollback."""
import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel
from backend.core.config import settings
from backend.security.validators import validate_safe_path
from backend.audit.logger import audit_logger

class ArtifactManifest(BaseModel):
    build_id: str
    project_id: str
    timestamp: str
    original_path: str
    original_sha256: str
    protected_path: str
    protected_sha256: str
    intensity: str
    verification_passed: bool
    metrics: dict[str, Any]

class ArtifactManager:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or settings.BLA_STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)

    @staticmethod
    def calculate_sha256(path: Path) -> str:
        """Calculate SHA-256 for a single file or recursively for a directory."""
        if path.is_file():
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        elif path.is_dir():
            hasher = hashlib.sha256()
            for root, _, files in sorted(os.walk(path)):
                for file in sorted(files):
                    file_p = Path(root) / file
                    hasher.update(file.encode("utf-8"))
                    with open(file_p, "rb") as f:
                        while chunk := f.read(65536):
                            hasher.update(chunk)
            return hasher.hexdigest()
        return ""

    def create_snapshot(
        self,
        project_id: str,
        source_artifact_path: str | Path,
        intensity: str = "balanced"
    ) -> tuple[str, Path, Path]:
        """
        Creates an immutable snapshot directory for a build.
        Returns (build_id, original_backup_path, protected_target_path).
        """
        safe_source = validate_safe_path(source_artifact_path)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        build_id = f"build_{project_id}_{timestamp}"
        
        build_dir = self.storage_dir / project_id / build_id
        original_backup = build_dir / "original" / safe_source.name
        protected_target = build_dir / "protected" / safe_source.name
        
        os.makedirs(original_backup.parent, exist_ok=True)
        os.makedirs(protected_target.parent, exist_ok=True)
        
        # Copy original safely to immutable backup
        if safe_source.is_file():
            shutil.copy2(safe_source, original_backup)
        else:
            shutil.copytree(safe_source, original_backup, dirs_exist_ok=True)
            
        return build_id, original_backup, protected_target

    def record_manifest(
        self,
        build_id: str,
        project_id: str,
        original_path: Path,
        protected_path: Path,
        intensity: str,
        verification_result: dict[str, Any]
    ) -> ArtifactManifest:
        orig_sha = self.calculate_sha256(original_path)
        prot_sha = self.calculate_sha256(protected_path)
        
        passed = (
            verification_result.get("overallPassed", False) or
            verification_result.get("output_matched", False) or
            verification_result.get("structural_invariants_passed", False)
        )
        manifest = ArtifactManifest(
            build_id=build_id,
            project_id=project_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            original_path=str(original_path),
            original_sha256=orig_sha,
            protected_path=str(protected_path),
            protected_sha256=prot_sha,
            intensity=intensity,
            verification_passed=passed,
            metrics=verification_result.get("metrics", {})
        )
        
        manifest_file = self.storage_dir / project_id / build_id / "manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))
            
        audit_logger.log_event(
            event_type="ARTIFACT_PROTECTION",
            action="MANIFEST_RECORDED",
            severity="INFO",
            project_id=project_id,
            details={
                "build_id": build_id,
                "orig_sha256": orig_sha,
                "prot_sha256": prot_sha,
                "verification_passed": manifest.verification_passed
            }
        )
        return manifest

    def rollback(self, project_id: str, build_id: str, destination_path: Path) -> bool:
        """Safely restore the original build artifact to destination."""
        build_dir = self.storage_dir / project_id / build_id
        original_dir = build_dir / "original"
        if not original_dir.exists():
            return False
        
        safe_dest = validate_safe_path(destination_path)
        # Find item inside original
        items = list(original_dir.iterdir())
        if not items:
            return False
        src = items[0]
        
        if src.is_file():
            shutil.copy2(src, safe_dest)
        else:
            shutil.copytree(src, safe_dest, dirs_exist_ok=True)
            
        audit_logger.log_event(
            event_type="ARTIFACT_ROLLBACK",
            action="ROLLBACK_EXECUTED",
            severity="WARNING",
            project_id=project_id,
            details={"build_id": build_id, "restored_to": str(safe_dest)}
        )
        return True

artifact_manager = ArtifactManager()
