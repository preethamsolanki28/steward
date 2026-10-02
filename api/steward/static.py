"""Root dispatcher: /mcp -> the bearer-guarded MCP app, everything else -> the static dashboard.

The dashboard is the Next.js static export (web/out), copied into the image at WEB_OUT_DIR by
the api Dockerfile's node:22 stage. Next.js exports /chat as chat.html, so an extensionless path
falls back to <path>.html; unknown paths get 404.html.
"""

from pathlib import Path

from starlette.responses import FileResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

WEB_OUT_DIR = Path(__file__).resolve().parents[1] / "web_out"


class Dashboard:
    def __init__(self, directory: Path = WEB_OUT_DIR) -> None:
        self.directory = directory
        self.files = StaticFiles(directory=directory, html=True, check_dir=False)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.directory.is_dir():
            await PlainTextResponse("Not Found", status_code=404)(scope, receive, send)
            return
        path = scope.get("path", "/")
        rel = path.lstrip("/")
        if rel and "." not in rel.rsplit("/", 1)[-1]:
            candidate = (self.directory / f"{rel.rstrip('/')}.html").resolve()
            if candidate.is_file() and candidate.is_relative_to(self.directory.resolve()):
                await FileResponse(candidate)(scope, receive, send)
                return
        await self.files(scope, receive, send)


class RootDispatcher:
    def __init__(self, mcp: ASGIApp, dashboard: ASGIApp) -> None:
        self.mcp = mcp
        self.dashboard = dashboard

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path", "")
        if path == "/mcp" or path.startswith("/mcp/"):
            await self.mcp(scope, receive, send)
        else:
            await self.dashboard(scope, receive, send)
