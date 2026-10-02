"""Control plane /api/* (docs/02 §6). Called by the dashboard only; guarded by steward.guards."""

from fastapi import APIRouter, Request

from steward import health as health_probe

router = APIRouter(prefix="/api")


@router.get("/health")
async def health(request: Request) -> dict[str, object]:
    return await health_probe.health(request.app.state.http)
