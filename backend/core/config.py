"""Configuration settings for Praxia Security Hub."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PRAXIA_ENV: str = Field(default="development", description="Environment mode")
    PRAXIA_HOST: str = Field(default="127.0.0.1", description="Host to bind")
    PRAXIA_PORT: int = Field(default=8888, description="Port for Praxia Security Hub")
    PRAXIA_SECRET_KEY: str = Field(
        default="praxia-super-secret-key-change-in-production-min-32-chars-long",
        description="Master secret key"
    )
    PRAXIA_JWT_ALGORITHM: str = Field(default="HS256")
    PRAXIA_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=120)

    # LLM Gateway Upstream Services
    HEADROOM_URL: str = Field(default="http://127.0.0.1:8787", description="Headroom proxy URL")
    OMNIROUTE_URL: str = Field(default="http://127.0.0.1:20128", description="OmniRoute router URL")
    GATEWAY_FAIL_CLOSED: bool = Field(default=True, description="Fail-closed when restricted data or secrets leaked")
    GATEWAY_MAX_PAYLOAD_MB: int = Field(default=10)

    # BLA Software Protection Adapter
    BLA_CLI_BIN: str = Field(default="bla", description="BLA executable name or path")
    BLA_DEFAULT_INTENSITY: str = Field(default="balanced", description="Default BLA protection intensity")
    BLA_AUTO_RESTORE_ON_FAILURE: bool = Field(default=True)
    BLA_STORAGE_DIR: Path = Field(default=BASE_DIR / "data" / "bla_storage")

    # Token Vault
    TOKEN_VAULT_KEY: str = Field(
        default="dGhpc2lzYTMyeGJ5dGVzZWNyZXRrZXlmb3J2YXVsdA==",
        description="Base64 32-byte key for AES-256-GCM Token Vault"
    )
    TOKEN_VAULT_TTL_SECONDS: int = Field(default=86400)

    # Directories
    PROJECTS_DIR: Path = Field(default=BASE_DIR / "projects")
    DATA_DIR: Path = Field(default=BASE_DIR / "data")
    AUDIT_LOG_DIR: Path = Field(default=BASE_DIR / "data" / "audit")
    AUDIT_STORAGE_DB: Path = Field(default=BASE_DIR / "data" / "praxia_security.db")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
# Ensure critical directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.AUDIT_LOG_DIR, exist_ok=True)
os.makedirs(settings.BLA_STORAGE_DIR, exist_ok=True)
os.makedirs(settings.PROJECTS_DIR, exist_ok=True)
