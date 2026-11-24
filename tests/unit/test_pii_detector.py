"""Unit tests for PII detection with Presidio and Spanish entities."""
import pytest
from backend.privacy.pii_detector.detector import PIIDetector

def test_pii_spanish_dni_and_email():
    detector = PIIDetector()
    text = "El cliente Juan Pérez con DNI 12345678Z y correo juan.perez@empresa.es solicita presupuesto."
    results = detector.detect(text)
    
    types = {r.entity_type for r in results}
    assert "ES_NIF_NIE" in types
    assert "EMAIL_ADDRESS" in types
    assert any("12345678Z" in r.text for r in results)
