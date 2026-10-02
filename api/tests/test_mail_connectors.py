"""T1.2: demo mailbox (demo_mail) and the SMTP redirect connector. No real mail is ever sent."""

import smtplib
from datetime import datetime
from email.message import EmailMessage

import anyio
import pytest

from steward import db, seed
from steward.config import get_settings
from steward.connectors import mail_demo, smtp


@pytest.fixture
def seeded() -> None:
    seed.seed_db(get_settings(), datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST))


def test_search_newest_first_and_any_term(seeded: None) -> None:
    with db.connect() as conn:
        acme = mail_demo.search(conn, "acme INV-0042")
        assert acme[0]["from_email"] == "billing@acme-logistics-payments.example"  # newest
        assert {"rahul.verma@acme-logistics.example"} <= {m["from_email"] for m in acme}
        assert len(mail_demo.search(conn, "", limit=50)) == 14
        assert len(mail_demo.search(conn, "", limit=3)) == 3
        assert mail_demo.search(conn, "no-such-term-xyz") == []


def test_read_marks_read_and_store_sent(seeded: None) -> None:
    with db.connect() as conn:
        unread = conn.execute("SELECT id FROM demo_mail WHERE is_read = 0").fetchone()["id"]
        mail = mail_demo.read(conn, unread)
        assert mail is not None and mail["to_emails"] == ["maya@rao-consulting.example"]
        assert conn.execute("SELECT is_read FROM demo_mail WHERE id=?", (unread,)).fetchone()[0]
        assert mail_demo.read(conn, 99999) is None
        sid = mail_demo.store_sent(
            conn,
            "Maya Rao",
            "maya@rao-consulting.example",
            ["rahul.verma@acme-logistics.example"],
            "s",
            "b",
        )
        assert mail_demo.search(conn, "", folder="sent")[0]["id"] == sid


class FakeSMTP:
    sent: list[EmailMessage] = []
    fail: Exception | None = None

    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.host, self.port, self.timeout = host, port, timeout

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def starttls(self) -> None:
        return None

    def login(self, user: str, password: str) -> None:
        return None

    def send_message(self, msg: EmailMessage) -> None:
        if FakeSMTP.fail:
            raise FakeSMTP.fail
        FakeSMTP.sent.append(msg)


@pytest.fixture
def fake_smtp(monkeypatch: pytest.MonkeyPatch) -> type[FakeSMTP]:
    FakeSMTP.sent, FakeSMTP.fail = [], None
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setenv("SMTP_HOST", "smtp.example")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "demo@team.example")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password")
    return FakeSMTP


def _send() -> int:
    return anyio.run(
        smtp.send,
        ["rahul.verma@acme-logistics.example"],
        "INV-0042",
        "body",
        "<steward-action-1@rao-consulting.example>",
    )


def test_disabled_without_redirect(fake_smtp: type[FakeSMTP]) -> None:
    assert smtp.enabled() is False
    with pytest.raises(smtp.SmtpNotConfigured):
        _send()
    assert fake_smtp.sent == []


def test_sends_only_to_redirect_with_prefix(
    fake_smtp: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")
    assert smtp.enabled() is True
    _send()
    (msg,) = fake_smtp.sent
    assert msg["To"] == "team-inbox@team.example"
    assert msg["Subject"] == "[Steward demo → rahul.verma@acme-logistics.example] INV-0042"
    assert msg["Message-ID"] == "<steward-action-1@rao-consulting.example>"
    assert "app-password" not in msg.as_string()


def test_timeout_is_delivery_unknown(
    fake_smtp: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")
    fake_smtp.fail = TimeoutError("timed out")
    with pytest.raises(smtp.DeliveryUnknown, match="delivery unknown"):
        _send()


def test_refusal_is_smtp_error(fake_smtp: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")
    fake_smtp.fail = smtplib.SMTPAuthenticationError(535, b"auth failed")
    with pytest.raises(smtp.SmtpError) as err:
        _send()
    assert "app-password" not in str(err.value)
