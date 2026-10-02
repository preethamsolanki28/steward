"""Test isolation: every test gets its own DB, workspace and Hermes data dir under tmp_path.

Nothing in the test suite touches ./data, ./workspace or the network.
"""

from pathlib import Path

import pytest

from steward import health


@pytest.fixture(autouse=True)
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for name in (
        "NEBIUS_API_KEY",
        "TAVILY_API_KEY",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "DEMO_MAIL_REDIRECT",
        "STEWARD_DEV",
        "REASONING_EFFORT",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("STEWARD_DB_PATH", str(tmp_path / "data" / "steward.db"))
    monkeypatch.setenv("HERMES_DATA_DIR", str(tmp_path / "hermes-data"))
    monkeypatch.setenv("WORKSPACE_DIR", str(tmp_path / "workspace"))
    monkeypatch.setenv("HERMES_API_URL", "http://hermes:8642")
    monkeypatch.setenv("HERMES_API_KEY", "test-hermes-key")
    monkeypatch.setenv("STEWARD_PROXY_KEY", "test-proxy-key")
    monkeypatch.setenv("STEWARD_MCP_TOKEN", "test-mcp-token")
    health._cache.clear()
    return tmp_path
