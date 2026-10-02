"""steward-api ASGI app.

T0.1: minimal app so the compose healthcheck has something to probe.
T1.1 replaces /api/health with the full payload
{ok, hermes, token_factory, tavily, mail_mode, model_primary}.
"""

from fastapi import FastAPI

# No /docs, /redoc or /openapi.json: only the endpoints in docs/02 §6 exist.
app = FastAPI(title="steward-api", docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/api/health")
async def health() -> dict[str, bool]:
    return {"ok": True}
