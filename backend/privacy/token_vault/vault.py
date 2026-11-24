"""Token Vault: Authenticated AES-256-GCM reversible pseudonymization."""
import base64
import json
import os
import time
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel
from backend.core.config import settings
from backend.core.errors import TokenVaultError

class TokenMapping(BaseModel):
    surrogate_token: str
    entity_type: str
    encrypted_value: str
    nonce: str
    created_at: int
    expires_at: int
    project_id: str
    session_id: str

class TokenVault:
    def __init__(self, master_key_b64: Optional[str] = None):
        key_str = master_key_b64 or settings.TOKEN_VAULT_KEY
        try:
            self.key = base64.b64decode(key_str)
            if len(self.key) != 32:
                # Pad or derive 32-byte key securely
                import hashlib
                self.key = hashlib.sha256(key_str.encode("utf-8")).digest()
        except Exception:
            import hashlib
            self.key = hashlib.sha256((key_str or "fallback_key").encode("utf-8")).digest()
            
        self.aesgcm = AESGCM(self.key)
        # In-memory session store (can be persisted to encrypted SQLite)
        # maps (project_id, session_id, surrogate) -> TokenMapping
        self._vault_store: dict[str, TokenMapping] = {}
        # reverse cache to prevent collision: (project_id, session_id, original_hash) -> surrogate
        self._reverse_index: dict[str, str] = {}
        self._counter: dict[str, int] = {}

    def _encrypt(self, plaintext: str, associated_data: str) -> tuple[str, str]:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), associated_data.encode("utf-8"))
        return base64.b64encode(ciphertext).decode("utf-8"), base64.b64encode(nonce).decode("utf-8")

    def _decrypt(self, ciphertext_b64: str, nonce_b64: str, associated_data: str) -> str:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, associated_data.encode("utf-8"))
        return plaintext.decode("utf-8")

    def get_or_create_surrogate(
        self,
        original_value: str,
        entity_type: str,
        project_id: str,
        session_id: str,
        ttl_seconds: int = 86400
    ) -> str:
        """
        Creates or returns an existing deterministic collision-free surrogate token
        e.g. [PERSON_001], [EMAIL_001], [ES_NIF_001]
        """
        import hashlib
        val_hash = hashlib.sha256(original_value.strip().lower().encode("utf-8")).hexdigest()
        index_key = f"{project_id}:{session_id}:{val_hash}"

        # Check if already pseudonymized in this session
        if index_key in self._reverse_index:
            existing_surrogate = self._reverse_index[index_key]
            vault_key = f"{project_id}:{session_id}:{existing_surrogate}"
            if vault_key in self._vault_store:
                mapping = self._vault_store[vault_key]
                if mapping.expires_at > int(time.time()):
                    return existing_surrogate

        # Generate new sequential surrogate
        counter_key = f"{project_id}:{session_id}:{entity_type}"
        current_seq = self._counter.get(counter_key, 0) + 1
        self._counter[counter_key] = current_seq
        
        # Clean entity type for token format
        clean_type = entity_type.replace(" ", "_").upper()
        surrogate = f"[{clean_type}_{current_seq:03d}]"

        # Encrypt original value with AES-GCM
        aad = f"{project_id}:{session_id}:{surrogate}"
        encrypted_val, nonce = self._encrypt(original_value, aad)

        now = int(time.time())
        mapping = TokenMapping(
            surrogate_token=surrogate,
            entity_type=entity_type,
            encrypted_value=encrypted_val,
            nonce=nonce,
            created_at=now,
            expires_at=now + ttl_seconds,
            project_id=project_id,
            session_id=session_id
        )

        vault_key = f"{project_id}:{session_id}:{surrogate}"
        self._vault_store[vault_key] = mapping
        self._reverse_index[index_key] = surrogate
        return surrogate

    def depseudonymize(self, surrogate_token: str, project_id: str, session_id: str) -> Optional[str]:
        """Decrypts and restores the original value for an authorized session."""
        vault_key = f"{project_id}:{session_id}:{surrogate_token}"
        mapping = self._vault_store.get(vault_key)
        if not mapping:
            return None

        if mapping.expires_at <= int(time.time()):
            raise TokenVaultError("Token has expired")

        aad = f"{project_id}:{session_id}:{surrogate_token}"
        return self._decrypt(mapping.encrypted_value, mapping.nonce, aad)

    def restore_text(self, text: str, project_id: str, session_id: str) -> str:
        """Restores all surrogate tokens found in text back to original values."""
        import re
        surrogate_regex = re.compile(r"\[[A-Z0-9_]+_\d{3}\]")
        
        def replace_match(match):
            surrogate = match.group(0)
            try:
                original = self.depseudonymize(surrogate, project_id, session_id)
                return original if original is not None else surrogate
            except Exception:
                return surrogate
                
        return surrogate_regex.sub(replace_match, text)

token_vault = TokenVault()
