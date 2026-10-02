"""steward-api ASGI app: one async process for the /v1 proxy, /mcp, /api and the dashboard.

Routing: /api/* (control plane, guarded) and /v1/* (proxy) are FastAPI routes; everything else
falls through to the root dispatcher, which sends exactly /mcp to the bearer-guarded MCP app
(D20) and every other path to the static dashboard (web/out).
"""

import hmac
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import anyio
import httpx
from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send

from steward import db
from steward.config import get_settings
from steward.guards import ApiGuard
from steward.routers import api, mcp_tools, proxy
from steward.static import Dashboard, RootDispatcher


class McpBearerAuth:
    """Our own ASGI guard for /mcp: Bearer STEWARD_MCP_TOKEN (D20; SDK auth is OAuth-only)."""

    def __init__(self) -> None:
        # Set per lifespan: the SDK's session manager can only run once per app instance.
        self.app: ASGIApp | None = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            expected = get_settings().steward_mcp_token
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
    await anyio.to_thread.run_sync(db.init_schema)
    mcp_guard.app = mcp_tools.build_mcp_app()
    async with httpx.AsyncClient() as http, mcp_tools.mcp_server.session_manager.run():
        app.state.http = http
        mcp_tools.set_http_client(http)
        yield


# No /docs, /redoc or /openapi.json: only the endpoints in docs/02 §6 exist.
app = FastAPI(
    title="steward-api", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
)
app.add_middleware(ApiGuard)
app.include_router(api.router)
app.include_router(proxy.router)
app.mount("/", RootDispatcher(mcp=mcp_guard, dashboard=Dashboard()))
