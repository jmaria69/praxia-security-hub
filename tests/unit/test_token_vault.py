"""Unit tests for Token Vault reversible pseudonymization and AES-256-GCM encryption."""
import pytest
from backend.privacy.token_vault.vault import TokenVault

def test_token_vault_pseudonymization_and_restoration():
    vault = TokenVault()
    project_id = "test_proj"
    session_id = "test_sess_01"
    
    original_name = "Carlos Morales"
    surrogate = vault.get_or_create_surrogate(
        original_value=original_name,
        entity_type="PERSON",
        project_id=project_id,
        session_id=session_id
    )
    
    assert surrogate.startswith("[PERSON_")
    
    # Deterministic in same session
    surrogate_repeat = vault.get_or_create_surrogate(
        original_value=original_name,
        entity_type="PERSON",
        project_id=project_id,
        session_id=session_id
    )
    assert surrogate == surrogate_repeat
    
    # Authorized reverse de-pseudonymization
    restored = vault.depseudonymize(surrogate, project_id, session_id)
    assert restored == original_name

def test_token_vault_text_replacement():
    vault = TokenVault()
    project_id = "test_proj"
    session_id = "test_sess_02"
    
    email = "carlos@praxialabs.com"
    surrogate = vault.get_or_create_surrogate(email, "EMAIL", project_id, session_id)
    
    llm_output = f"Hemos enviado las instrucciones a {surrogate} correctamente."
    restored_text = vault.restore_text(llm_output, project_id, session_id)
    
    assert email in restored_text
    assert surrogate not in restored_text
