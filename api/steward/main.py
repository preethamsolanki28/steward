"""steward-api ASGI app.

M0 state: /api/health (minimal; T1.1 adds the full payload), the T0.3 passthrough proxy at /v1
and the T0.3 stub MCP server at /mcp.
"""

import hmac
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send

from steward.routers import mcp_tools, proxy


class McpBearerAuth:
    """Our own ASGI guard for /mcp: Bearer STEWARD_MCP_TOKEN (D20; SDK auth is OAuth-only)."""

    def __init__(self) -> None:
        # Set per lifespan: the SDK's session manager can only run once per app instance.
        self.app: ASGIApp | None = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            expected = os.environ.get("STEWARD_MCP_TOKEN", "")
            supplied = dict(scope.get("headers") or []).get(b"authorization", b"").decode("latin-1")
            if not expected or not hmac.compare_digest(supplied, f"Bearer {expected}"):
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await send({"type": "http.response.body", "body": b'{"detail":"Unauthorized"}'})
                return
        if self.app is None:
            raise RuntimeError("MCP app used outside the steward-api lifespan")
        await self.app(scope, receive, send)


mcp_guard = McpBearerAuth()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    mcp_guard.app = mcp_tools.build_mcp_app()
    async with httpx.AsyncClient() as http, mcp_tools.mcp_server.session_manager.run():
        app.state.http = http
        yield


# No /docs, /redoc or /openapi.json: only the endpoints in docs/02 §6 exist.
app = FastAPI(
    title="steward-api", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
)
app.include_router(proxy.router)


@app.get("/api/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


# Mounted at the root after the FastAPI routes, so the MCP endpoint is exactly /mcp (D20).
app.mount("/", mcp_guard)
