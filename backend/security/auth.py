"""Authentication and RBAC security for Praxia Security Hub."""
import hashlib
import hmac
import time
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from backend.core.config import settings

security_bearer = HTTPBearer(auto_error=False)

class User(BaseModel):
    username: str
    role: str  # admin, operator, auditor
    scopes: list[str]

# In-memory user store for Praxia Security Hub administrators
# Passwords hashed with PBKDF2-HMAC-SHA256
def hash_password(password: str, salt: str = "praxia_salt_v1") -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()

USERS_DB = {
    "admin": {
        "username": "admin",
        "password_hash": hash_password("PraxiaAdmin2026!"),
        "role": "admin",
        "scopes": ["*"]
    },
    "operator": {
        "username": "operator",
        "password_hash": hash_password("PraxiaOperator2026!"),
        "role": "operator",
        "scopes": ["projects:read", "projects:audit", "protection:execute", "privacy:scan"]
    },
    "auditor": {
        "username": "auditor",
        "password_hash": hash_password("PraxiaAuditor2026!"),
        "role": "auditor",
        "scopes": ["projects:read", "audit:read", "reports:generate"]
    }
}

def authenticate_user(username: str, password: str) -> Optional[User]:
    user_record = USERS_DB.get(username)
    if not user_record:
        return None
    input_hash = hash_password(password)
    if hmac.compare_digest(user_record["password_hash"], input_hash):
        return User(
            username=user_record["username"],
            role=user_record["role"],
            scopes=user_record["scopes"]
        )
    return None

def create_access_token(user: User, expires_minutes: Optional[int] = None) -> str:
    now = int(time.time())
    expire = now + (expires_minutes or settings.PRAXIA_ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    payload = {
        "sub": user.username,
        "role": user.role,
        "scopes": user.scopes,
        "iat": now,
        "exp": expire,
        "iss": "praxia-security-hub"
    }
    return jwt.encode(payload, settings.PRAXIA_SECRET_KEY, algorithm=settings.PRAXIA_JWT_ALGORITHM)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> User:
    if not credentials:
        # Allow localhost development bypass only if configured
        if settings.PRAXIA_ENV == "development":
            return User(username="admin_local", role="admin", scopes=["*"])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.PRAXIA_SECRET_KEY,
            algorithms=[settings.PRAXIA_JWT_ALGORITHM],
            options={"require": ["exp", "sub"]}
        )
        return User(
            username=payload["sub"],
            role=payload.get("role", "operator"),
            scopes=payload.get("scopes", [])
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")

def require_role(required_role: str):
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role == "admin" or user.role == required_role:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation requires '{required_role}' role"
        )
    return role_checker
