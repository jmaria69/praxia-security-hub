"""Tests for Praxia Security Hub CLI Commands."""
import json
import pytest
from backend.cli import main
from backend.core.project_registry import project_registry, ProjectConfig

def test_cli_status(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["praxia-security", "--json", "status"])
    main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "OPERATIONAL"
    assert data["registered_projects_count"] >= 6

def test_cli_projects_list(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["praxia-security", "--json", "projects", "list"])
    main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    ids = [p["id"] for p in data]
    assert "adminapp" in ids
    assert "saludos" in ids
    assert "siam" in ids

def test_cli_projects_inspect(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["praxia-security", "--json", "projects", "inspect", "adminapp"])
    main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "adminapp"
    assert data["privacy"]["classification_default"] == "CONFIDENTIAL"

def test_cli_audit(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["praxia-security", "--json", "audit", "adminapp"])
    main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["project_id"] == "adminapp"
    assert "incidents" in data
    assert "events" in data

def test_cli_reports_generate(capsys, monkeypatch, tmp_path):
    report_file = tmp_path / "report.json"
    monkeypatch.setattr("sys.argv", ["praxia-security", "reports", "generate", "--output", str(report_file)])
    main()
    assert report_file.exists()
    content = json.loads(report_file.read_text(encoding="utf-8"))
    assert content["platform_status"] == "OPERATIONAL"
    assert content["total_projects"] >= 6

def test_cli_protection_dry_run(capsys, monkeypatch, tmp_path):
    # Set dummy build output for adminapp
    dummy_dist = tmp_path / "adminapp_dist"
    dummy_dist.mkdir()
    (dummy_dist / "bundle.js").write_text("console.log('test');")
    
    p = project_registry.get_project("adminapp")
    p.root_path = str(tmp_path)
    p.technology.build_output = "adminapp_dist"
    
    monkeypatch.setattr(project_registry, "get_project", lambda pid: p if pid == "adminapp" else None)
    monkeypatch.setattr("backend.cli.project_registry.get_project", lambda pid: p if pid == "adminapp" else None)
    monkeypatch.setattr("sys.argv", ["praxia-security", "--json", "protection", "dry-run", "adminapp"])
    main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["mode"] == "DRY_RUN"
    assert data["project_id"] == "adminapp"
