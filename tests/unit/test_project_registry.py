"""Unit tests for Project Registry loading, validation and management."""
import pytest
from backend.core.project_registry import project_registry, ProjectConfig

def test_list_projects_contains_initial_saas():
    projects = project_registry.list_projects()
    assert len(projects) >= 6
    ids = {p.id for p in projects}
    assert "adminapp" in ids
    assert "siam" in ids
    assert "ageverify" in ids
    assert "radar-ai" in ids
    assert "crm-it" in ids
    assert "saludos" in ids

def test_get_individual_project():
    siam = project_registry.get_project("siam")
    assert siam is not None
    assert siam.name == "SIAM / SIEM"
    assert siam.privacy.classification_default == "RESTRICTED"
    assert siam.protection.intensity == "maximum"
