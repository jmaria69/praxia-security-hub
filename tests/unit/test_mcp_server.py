"""Unit tests for Praxia Security Hub MCP Server."""
import json
import pytest
from backend.mcp.server import TOOLS, call_tool

def test_mcp_tools_definition_structure():
    tool_names = [t["name"] for t in TOOLS]
    assert "praxia_status" in tool_names
    assert "praxia_list_projects" in tool_names
    assert "praxia_inspect_project" in tool_names
    assert "praxia_scan_prompt" in tool_names
    assert "praxia_audit_artifacts" in tool_names
    assert "praxia_get_audit_events" in tool_names

def test_mcp_tool_praxia_status():
    result = call_tool("praxia_status", {})
    assert result["status"] == "OPERATIONAL"
    assert result["projects_count"] >= 6

def test_mcp_tool_praxia_list_projects():
    result = call_tool("praxia_list_projects", {})
    assert len(result) >= 6
    project_ids = [p["id"] for p in result]
    assert "adminapp" in project_ids
    assert "siam" in project_ids

def test_mcp_tool_praxia_inspect_project():
    result = call_tool("praxia_inspect_project", {"project_id": "adminapp"})
    assert result["id"] == "adminapp"
    assert result["privacy"]["classification_default"] == "CONFIDENTIAL"

def test_mcp_tool_praxia_scan_prompt_pii():
    sample_text = "El usuario Juan Garcia con DNI 12345678Z y email juan@praxia.es solicita acceso."
    result = call_tool("praxia_scan_prompt", {"text": sample_text, "project_id": "adminapp"})
    assert result["pii_entities_count"] >= 1
    assert "12345678Z" not in result["processed_text"]

def test_mcp_tool_praxia_scan_prompt_fail_closed():
    sample_text = "Conéctate usando la API key secreta sk-ant-api03-abcdef12345678901234567890"
    result = call_tool("praxia_scan_prompt", {"text": sample_text, "project_id": "siam"})
    assert result["blocked"] is True
    assert result["status"] == "FAIL_CLOSED_BLOCKED"

def test_mcp_tool_praxia_get_audit_events():
    result = call_tool("praxia_get_audit_events", {"limit": 5})
    assert "events" in result
    assert "incidents" in result

def test_mcp_tool_praxia_onboard_project(tmp_path):
    project_dir = tmp_path / "mcp-saas-project"
    project_dir.mkdir()
    (project_dir / "package.json").write_text(json.dumps({
        "name": "mcp-saas-project",
        "dependencies": {"next": "14.2.0"}
    }), encoding="utf-8")

    result = call_tool("praxia_onboard_project", {
        "project_path": str(project_dir),
        "name": "mcp-saas-project",
        "domain": "mcp-saas.praxialabs.com",
        "dry_run": True
    })

    assert result["success"] is True
    assert result["project_id"] == "mcp-saas-project"
    assert result["domain"] == "mcp-saas.praxialabs.com"
    assert result["bla_hardening"]["hook_created"] is True
    assert (project_dir / "scripts" / "praxia-harden.js").exists()
