"""Praxia Security Hub - Main Application Entrypoint."""
import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.core.config import settings
from backend.core.errors import PraxiaException, FailClosedException
from backend.api.gateway_routes import router as gateway_router
from backend.api.management_routes import router as management_router
from backend.security.auth import authenticate_user, create_access_token, User
from pydantic import BaseModel

app = FastAPI(
    title="Praxia Security Hub",
    version="1.0.0",
    description="Enterprise Security & LLM Privacy Platform for Praxia Labs SaaS Ecosystem"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/token", tags=["Authentication"])
async def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid username or password"}
        )
    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "scopes": user.scopes
    }

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "service": "praxia-security-hub",
        "version": "1.0.0",
        "environment": settings.PRAXIA_ENV,
        "upstreams": {
            "headroom": settings.HEADROOM_URL,
            "omniroute": settings.OMNIROUTE_URL
        }
    }

# Mount sub-routers
app.include_router(gateway_router)
app.include_router(management_router)

# Mount static frontend build if present
static_dist = settings.DATA_DIR.parent / "frontend" / "dist"
if static_dist.exists():
    app.mount("/", StaticFiles(directory=str(static_dist), html=True), name="frontend")

@app.exception_handler(FailClosedException)
async def handle_fail_closed(request: Request, exc: FailClosedException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": {
                "message": exc.message,
                "type": "fail_closed_security_violation",
                "details": exc.details
            }
        }
    )

@app.exception_handler(PraxiaException)
async def handle_praxia_exception(request: Request, exc: PraxiaException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details
            }
        }
    )
