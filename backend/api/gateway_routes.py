"""API Routes for OpenAI/Anthropic LLM Proxy Gateways."""
from fastapi import APIRouter, Request, Query, Header
from backend.orchestration.proxy_engine import proxy_engine

router = APIRouter(tags=["LLM Privacy Gateway"])

@router.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    x_praxia_project: str = Header(default="default", alias="X-Praxia-Project"),
    x_praxia_session: str = Header(default="session_default", alias="X-Praxia-Session")
):
    """
    OpenAI-compatible chat completion proxy endpoint.
    Scans for secrets, pseudonymizes PII, enforces fail-closed, and proxies to Headroom/OmniRoute.
    """
    return await proxy_engine.forward_request(
        request=request,
        path="v1/chat/completions",
        project_id=x_praxia_project,
        session_id=x_praxia_session
    )

@router.post("/v1/messages")
async def anthropic_messages(
    request: Request,
    x_praxia_project: str = Header(default="default", alias="X-Praxia-Project"),
    x_praxia_session: str = Header(default="session_default", alias="X-Praxia-Session")
):
    """
    Anthropic-compatible messages proxy endpoint.
    """
    return await proxy_engine.forward_request(
        request=request,
        path="v1/messages",
        project_id=x_praxia_project,
        session_id=x_praxia_session
    )

@router.get("/v1/models")
async def list_models(request: Request):
    """List available models from upstream."""
    return await proxy_engine.forward_request(
        request=request,
        path="v1/models",
        project_id="default"
    )
