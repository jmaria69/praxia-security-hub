"""Reverse Proxy & Stream Engine connecting to Headroom (8787) and OmniRoute (20128)."""
import json
from typing import AsyncGenerator, Optional
import httpx
from fastapi import Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from backend.core.config import settings
from backend.core.errors import FailClosedException
from backend.privacy.gateway.processor import privacy_processor
from backend.core.project_registry import project_registry
from backend.audit.logger import audit_logger

class ProxyEngine:
    def __init__(self, upstream_url: Optional[str] = None):
        self.upstream_url = upstream_url or settings.HEADROOM_URL
        self.fallback_url = settings.OMNIROUTE_URL

    async def forward_request(
        self,
        request: Request,
        path: str,
        project_id: str = "default",
        session_id: str = "session_001"
    ) -> StreamingResponse | JSONResponse:
        """
        Intercepts request body, scans and protects PII/Secrets, and forwards to upstream.
        """
        # 1. Read and parse incoming JSON payload
        try:
            body_bytes = await request.body()
            body_json = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON request body: {str(e)}")

        # 2. Extract Project Policy
        project_cfg = project_registry.get_project(project_id)
        project_policy = project_cfg.privacy.model_dump() if project_cfg else {}

        # 3. Intercept & process messages
        messages = body_json.get("messages", [])
        is_streaming = body_json.get("stream", False)

        for msg in messages:
            content = msg.get("content")
            if isinstance(content, str):
                try:
                    res = privacy_processor.process_prompt(
                        text=content,
                        project_id=project_id,
                        session_id=session_id,
                        project_policy=project_policy
                    )
                    msg["content"] = res.processed_text
                except FailClosedException as fce:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={
                            "error": {
                                "message": fce.message,
                                "type": "praxia_security_violation",
                                "code": "FAIL_CLOSED_TRIGGERED",
                                "details": fce.details
                            }
                        }
                    )
            elif isinstance(content, list):
                # Multimodal or block messages
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        sub_text = block.get("text", "")
                        try:
                            res = privacy_processor.process_prompt(
                                text=sub_text,
                                project_id=project_id,
                                session_id=session_id,
                                project_policy=project_policy
                            )
                            block["text"] = res.processed_text
                        except FailClosedException as fce:
                            return JSONResponse(
                                status_code=status.HTTP_403_FORBIDDEN,
                                content={
                                    "error": {
                                        "message": fce.message,
                                        "type": "praxia_security_violation",
                                        "code": "FAIL_CLOSED_TRIGGERED"
                                    }
                                }
                            )

        # 4. Prepare forward headers
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        upstream_target = f"{self.upstream_url.rstrip('/')}/{path.lstrip('/')}"
        
        # 5. Execute HTTP forward with fallback
        client = httpx.AsyncClient(timeout=120.0)
        try:
            if is_streaming:
                async def stream_generator() -> AsyncGenerator[bytes, None]:
                    try:
                        async with client.stream(
                            method=request.method,
                            url=upstream_target,
                            headers=headers,
                            json=body_json
                        ) as resp:
                            async for chunk in resp.aiter_bytes():
                                # Check if chunk contains completed text to restore
                                decoded = chunk.decode("utf-8", errors="replace")
                                if "data: " in decoded:
                                    restored = privacy_processor.restore_response(
                                        llm_response_text=decoded,
                                        project_id=project_id,
                                        session_id=session_id
                                    )
                                    yield restored.encode("utf-8")
                                else:
                                    yield chunk
                    finally:
                        await client.aclose()

                return StreamingResponse(stream_generator(), media_type="text/event-stream")
            else:
                try:
                    resp = await client.request(
                        method=request.method,
                        url=upstream_target,
                        headers=headers,
                        json=body_json
                    )
                except httpx.ConnectError:
                    # Fallback directly to OmniRoute if Headroom is temporarily bypassed
                    upstream_target = f"{self.fallback_url.rstrip('/')}/{path.lstrip('/')}"
                    resp = await client.request(
                        method=request.method,
                        url=upstream_target,
                        headers=headers,
                        json=body_json
                    )

                response_content = resp.content
                await client.aclose()

                # Reverse restore pseudonymized tokens in response choices
                try:
                    resp_json = resp.json()
                    choices = resp_json.get("choices", [])
                    for choice in choices:
                        msg = choice.get("message", {})
                        if "content" in msg and isinstance(msg["content"], str):
                            msg["content"] = privacy_processor.restore_response(
                                msg["content"], project_id=project_id, session_id=session_id
                            )
                    return JSONResponse(status_code=resp.status_code, content=resp_json)
                except Exception:
                    return JSONResponse(status_code=resp.status_code, content={"raw": response_content.decode("utf-8", errors="replace")})

        except Exception as e:
            await client.aclose()
            raise HTTPException(status_code=502, detail=f"Error communicating with LLM upstream: {str(e)}")

proxy_engine = ProxyEngine()
