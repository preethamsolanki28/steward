"""Test isolation: every test gets its own DB, workspace and Hermes data dir under tmp_path.

Nothing in the test suite touches ./data, ./workspace or the network.
"""

import smtplib
import threading
import time
from email.message import EmailMessage
from pathlib import Path

import pytest

from steward import health, jobs


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

    async def no_registration(client: object) -> None:
        return None

    monkeypatch.setattr(jobs, "register_on_startup", no_registration)
    return tmp_path


class FakeSMTP:
    """smtplib.SMTP / SMTP_SSL stand-in: records every connection, the TLS contexts it was
    given, every send attempt and every accepted message. `fail` makes send_message raise;
    `delay` makes it slow (for race tests)."""

    sent: list[EmailMessage] = []
    attempts: int = 0
    contexts: list[object] = []
    fail: Exception | None = None
    delay: float = 0.0
    _lock = threading.Lock()

    def __init__(
        self, host: str, port: int, timeout: float | None = None, context: object = None
    ) -> None:
        self.host, self.port, self.timeout = host, port, timeout
        if context is not None:
            FakeSMTP.contexts.append(context)

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def starttls(self, context: object = None) -> None:
        FakeSMTP.contexts.append(context)

    def login(self, user: str, password: str) -> None:
        return None

    def send_message(self, msg: EmailMessage) -> None:
        with FakeSMTP._lock:
            FakeSMTP.attempts += 1
        if FakeSMTP.delay:
            time.sleep(FakeSMTP.delay)
        if FakeSMTP.fail:
            raise FakeSMTP.fail
        with FakeSMTP._lock:
            FakeSMTP.sent.append(msg)

    def quit(self) -> None:
        return None

    def close(self) -> None:
        return None


@pytest.fixture
def fake_smtp(monkeypatch: pytest.MonkeyPatch) -> type[FakeSMTP]:
    FakeSMTP.sent, FakeSMTP.attempts, FakeSMTP.fail, FakeSMTP.delay = [], 0, None, 0.0
    FakeSMTP.contexts = []
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSMTP)
    monkeypatch.setenv("SMTP_HOST", "smtp.example")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "demo@team.example")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password")
    return FakeSMTP
