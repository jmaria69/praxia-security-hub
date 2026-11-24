"""Unit tests for Secret Scanner and Shannon Entropy."""
import pytest
from backend.privacy.secret_scanner.scanner import SecretScanner, calculate_shannon_entropy

def test_shannon_entropy():
    # Low entropy plain word
    assert calculate_shannon_entropy("aaaaaaaa") == 0.0
    # High entropy random string
    high_ent = calculate_shannon_entropy("q9X#zL8!pM2$kR7@")
    assert high_ent > 3.5

def test_secret_scanner_detects_keys():
    scanner = SecretScanner()
    
    text = "Aquí está mi OpenAI key: sk-abcdef1234567890abcdef123456789012 y AWS: AKIAIOSFODNN7EXAMPLE"
    findings = scanner.scan(text)
    
    assert len(findings) >= 2
    rule_ids = {f.rule_id for f in findings}
    assert "OPENAI_KEY" in rule_ids
    assert "AWS_ACCESS_KEY" in rule_ids

def test_secret_scanner_clean_text():
    scanner = SecretScanner()
    clean_text = "Esta es una consulta normal sobre cómo ordenar una lista en Python."
    assert len(scanner.scan(clean_text)) == 0
