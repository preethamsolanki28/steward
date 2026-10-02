"""T0.1: no generated docs routes (the full /api/health payload is tested in test_api_skeleton)."""

from fastapi.testclient import TestClient

from steward.main import app


def test_no_generated_docs_routes() -> None:
    # Unknown paths fall through to the static dashboard (404) or the /mcp guard, never docs.
    with TestClient(app, base_url="http://127.0.0.1:8787") as client:
        for path in ("/docs", "/redoc", "/openapi.json"):
            response = client.get(path)
            assert response.status_code in (401, 404)
            assert "openapi" not in response.text.lower()
