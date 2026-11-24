"""Integration tests for BLA protection adapter and artifact preservation."""
import pytest
from pathlib import Path
from backend.protection.bla_adapter.cli_runner import bla_runner
from backend.protection.artifact_manager.store import artifact_manager
from backend.protection.verification.verifier import verifier

def test_bla_doctor_check():
    doc = bla_runner.doctor()
    assert doc.get("healthy") is True
    assert "javascriptAstShield" in doc.get("engines", {})

def test_isolated_protect_verify_and_rollback(tmp_path):
    # 1. Create a synthetic JS artifact in tmp_path
    sample_js = tmp_path / "bundle.js"
    sample_js.write_text("function add(a, b) { return a + b; }\nconsole.log(add(5, 7));\n")
    
    # 2. Snapshot
    build_id, orig_backup, prot_target = artifact_manager.create_snapshot(
        project_id="test_bla",
        source_artifact_path=sample_js,
        intensity="stealth"
    )
    assert orig_backup.exists()
    
    # 3. Protect
    protect_res = bla_runner.protect(
        input_path=orig_backup,
        output_path=prot_target,
        intensity="stealth"
    )
    assert prot_target.exists()
    assert prot_target.stat().st_size > sample_js.stat().st_size
    
    # 4. Verify runtime equivalence
    verif = verifier.verify_runtime_equivalence(orig_backup, prot_target)
    assert verif["runtime_execution_passed"] is True
    assert verif["output_matched"] is True
    assert verif["details"]["protected_output"] == "12"
    
    # 5. Manifest
    manifest = artifact_manager.record_manifest(
        build_id=build_id,
        project_id="test_bla",
        original_path=orig_backup,
        protected_path=prot_target,
        intensity="stealth",
        verification_result=verif
    )
    assert manifest.verification_passed is True
    
    # 6. Test Rollback to restored file
    restored_dest = tmp_path / "restored.js"
    success = artifact_manager.rollback("test_bla", build_id, restored_dest)
    assert success is True
    assert restored_dest.exists()
    assert restored_dest.read_text() == sample_js.read_text()
