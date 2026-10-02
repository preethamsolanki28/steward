"""Control-plane guards for /api/* (docs/02 §6 "Guards", §4 rule 7).

- Host allowlist: only 127.0.0.1:8787 and localhost:8787 (plus localhost:3000 when
  STEWARD_DEV=1). Hermes calls with Host steward-api:8787 and DNS-rebinding pages carry their
  own Host, so both are rejected: the agent can never reach the control plane.
- Mutating /api/* routes need `X-Steward-Client: web`. The custom header forces a CORS
  preflight, which fails cross-origin because CORS is never enabled.
"""

import json

from starlette.types import ASGIApp, Receive, Scope, Send

from steward.config import get_settings

ALLOWED_HOSTS = frozenset({"127.0.0.1:8787", "localhost:8787"})
DEV_HOSTS = frozenset({"localhost:3000"})
MUTATING = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def allowed_hosts() -> frozenset[str]:
    return ALLOWED_HOSTS | DEV_HOSTS if get_settings().steward_dev else ALLOWED_HOSTS


async def _deny(send: Send, status: int, detail: str) -> None:
    body = json.dumps({"detail": detail}).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


class ApiGuard:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path", "")
        if scope["type"] == "http" and (path == "/api" or path.startswith("/api/")):
            headers = {
                k.decode("latin-1").lower(): v.decode("latin-1")
                for k, v in scope.get("headers") or []
            }
            if headers.get("host", "").lower() not in allowed_hosts():
                await _deny(send, 403, "Forbidden host")
                return
            if (
                scope.get("method", "GET").upper() in MUTATING
                and headers.get("x-steward-client") != "web"
            ):
                await _deny(send, 403, "Missing X-Steward-Client header")
                return
        await self.app(scope, receive, send)
