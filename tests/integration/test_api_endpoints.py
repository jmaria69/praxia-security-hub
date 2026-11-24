"""Integration tests for FastAPI application endpoints."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "praxia-security-hub"

def test_list_projects_endpoint():
    res = client.get("/api/projects")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) >= 6

def test_privacy_scan_endpoint_replaces_pii():
    payload = {
        "text": "Contacto del paciente Juan Perez con correo juan@hospital.es",
        "project_id": "saludos",
        "session_id": "test_api_sess"
    }
    res = client.post("/api/privacy/scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["classification"]["level"] in ["CONFIDENTIAL", "RESTRICTED"]
    assert "[PERSON_" in data["processed_text"] or "[EMAIL_ADDRESS_" in data["processed_text"]

def test_audit_events_endpoint():
    res = client.get("/api/audit/events")
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
