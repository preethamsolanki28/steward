"""T1.6: the single Uvicorn worker never blocks its event loop while /api/chat waits on Hermes.

A real Uvicorn server runs in a thread. The fake Hermes behind /api/chat calls BACK into the same
steward-api over HTTP (the /v1 proxy and a DB-backed /api route) before it answers, exactly like
Hermes calling /v1 and /mcp mid-turn. If /api/chat blocked the loop, those callbacks could never
be served and the turn would deadlock until the timeout.
"""

import socket
import threading
import time

import httpx
import uvicorn

from steward import db
from steward.main import app

LOCAL_HOST = {"Host": "127.0.0.1:8787"}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_hermes_can_call_back_while_chat_is_waiting() -> None:
    db.init_schema()
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, workers=1, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started

    callbacks: list[int] = []

    async def fake_hermes(request: httpx.Request) -> httpx.Response:
        async with httpx.AsyncClient(timeout=5.0) as back:
            models = await back.get(
                f"{base}/v1/models", headers={"Authorization": "Bearer test-proxy-key"}
            )
            convs = await back.get(f"{base}/api/conversations", headers=LOCAL_HOST)
        callbacks.extend([models.status_code, convs.status_code])
        return httpx.Response(200, json={"choices": [{"message": {"content": "done"}}]})

    try:
        # Swap Hermes for the fake once the server's lifespan has created the shared client.
        app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(fake_hermes))
        started = time.monotonic()
        r = httpx.post(
            f"{base}/api/chat",
            json={"message": "hi"},
            timeout=20.0,
            headers={**LOCAL_HOST, "X-Steward-Client": "web"},
        )
        elapsed = time.monotonic() - started
    finally:
        server.should_exit = True
        thread.join(timeout=10)

    assert r.status_code == 200 and r.json()["reply"] == "done"
    assert callbacks == [200, 200]
    assert elapsed < 5.0
