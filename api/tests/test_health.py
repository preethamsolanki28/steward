"""T0.1: the minimal app answers the compose healthcheck and exposes no extra routes."""

from fastapi.testclient import TestClient

from steward.main import app

client = TestClient(app, base_url="http://127.0.0.1:8787")


def test_health_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_no_generated_docs_routes() -> None:
    # Unknown paths fall through to the root-mounted /mcp guard (D20), so they get 401, never docs.
    for path in ("/docs", "/redoc", "/openapi.json"):
        response = client.get(path)
        assert response.status_code in (401, 404)
        assert "openapi" not in response.text.lower()
