"""Unit tests for SIAM Integration & Reverse Engineering Detection tools."""
import pytest
from backend.providers.siam_alert_sink import SiamAlertSink
from backend.mcp.server import call_tool, TOOLS

def test_siam_tools_in_tools_definition():
    tool_names = [t["name"] for t in TOOLS]
    assert "praxia_detect_code_leak" in tool_names
    assert "praxia_check_reverse_engineering" in tool_names
    assert "praxia_forward_alert_to_siam" in tool_names

def test_siam_alert_sink_offline_graceful():
    sink = SiamAlertSink(siam_url="http://127.0.0.1:9999", api_key="test-key")
    res = sink.send_alert(
        event_type="test.event",
        asset_name="AdminApp",
        severity="high",
        summary="Test summary",
        description="Test desc",
        timeout=0.2
    )
    assert res["status"] in ("OFFLINE", "ERROR")

def test_mcp_tool_praxia_detect_code_leak_clean():
    clean_code = "def add(a, b): return a + b"
    result = call_tool("praxia_detect_code_leak", {"code_or_prompt": clean_code})
    assert result["contains_secrets"] is False
    assert result["blocked_by_fail_closed"] is False
    assert result["exfiltration_risk"] == "LOW"

def test_mcp_tool_praxia_detect_code_leak_with_secret():
    leaked_code = "API_KEY = 'sk-ant-api03-abcdef12345678901234567890'\n# proprietary logic for AdminApp"
    result = call_tool("praxia_detect_code_leak", {"code_or_prompt": leaked_code, "suspected_project": "adminapp"})
    assert result["contains_secrets"] is True
    assert result["blocked_by_fail_closed"] is True
    assert result["exfiltration_risk"] == "CRITICAL"
    assert "AdminApp (Onzane)" in result["proprietary_signatures_detected"]

def test_mcp_tool_praxia_check_reverse_engineering():
    result = call_tool("praxia_check_reverse_engineering", {"project_id": "adminapp"})
    assert result["project_id"] == "adminapp"
    assert "status" in result or "rea_exposure_score" in result
