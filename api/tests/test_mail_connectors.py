"""T1.2: demo mailbox (demo_mail) and the SMTP redirect connector. No real mail is ever sent."""

import smtplib
from datetime import datetime

import anyio
import pytest

from steward import db, seed
from steward.config import get_settings
from steward.connectors import mail_demo, smtp
from tests.conftest import FakeSMTP


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


# --- real smtplib against a loopback server (M3 review): timeouts are classified by phase ----

import socket  # noqa: E402
import ssl  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from email.message import EmailMessage  # noqa: E402


class LoopbackSMTP(threading.Thread):
    """A tiny plaintext SMTP server on 127.0.0.1 with one scripted misbehaviour."""

    def __init__(self, mode: str) -> None:
        super().__init__(daemon=True)
        self.mode, self.received = mode, False
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]

    def run(self) -> None:
        conn, _ = self.sock.accept()
        f = conn.makefile("rwb")

        def say(line: str) -> None:
            f.write(line.encode() + b"\r\n")
            f.flush()

        say("220 loopback ESMTP")
        while True:
            line = f.readline()
            if not line:
                break
            cmd = line.decode().strip().upper()
            if cmd.startswith(("EHLO", "HELO")):
                say("250 loopback")
            elif cmd.startswith("RCPT"):
                say("550 no such user" if self.mode == "refuse_rcpt" else "250 ok")
            elif cmd == "DATA":
                say("354 go ahead")
                while f.readline() not in (b".\r\n", b""):
                    pass
                self.received = True
                if self.mode == "hang_after_data":
                    time.sleep(3)
                    break
                if self.mode == "drop_after_data":
                    break
                say("250 queued")
            elif cmd == "QUIT":
                say("500 confused" if self.mode == "bad_quit" else "221 bye")
                break
            else:
                say("250 ok")
        conn.close()
        self.sock.close()


def _real_send(port: int, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_HOST", "127.0.0.1")
    monkeypatch.setenv("SMTP_PORT", str(port))
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")
    monkeypatch.setattr(smtp, "SMTP_TIMEOUT_S", 1.0)
    # The loopback server speaks plaintext; everything else is the real smtplib.
    monkeypatch.setattr(smtplib.SMTP, "starttls", lambda self, context=None: (220, b"ok"))
    settings = get_settings()
    msg = smtp.build_message(settings, ["rahul.verma@acme-logistics.example"], "s", "b", "<m@x>")
    smtp._send_sync(settings, msg)


@pytest.mark.parametrize("mode", ["hang_after_data", "drop_after_data"])
def test_real_smtplib_failure_mid_send_is_delivery_unknown(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server = LoopbackSMTP(mode)
    server.start()
    with pytest.raises(smtp.DeliveryUnknown) as exc:
        _real_send(server.port, monkeypatch)
    assert str(exc.value) == "delivery unknown — check Sent before retrying"
    assert server.received  # the server had the whole message: it may have been delivered


def test_real_smtplib_refusal_is_a_plain_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    server = LoopbackSMTP("refuse_rcpt")
    server.start()
    with pytest.raises(smtp.SmtpError, match="SMTPRecipientsRefused"):
        _real_send(server.port, monkeypatch)


def test_real_smtplib_connection_refused_is_a_plain_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]  # closed again: nothing listens there
    with pytest.raises(smtp.SmtpError, match="ConnectionRefusedError"):
        _real_send(port, monkeypatch)


def test_real_smtplib_error_after_acceptance_still_counts_as_sent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = LoopbackSMTP("bad_quit")
    server.start()
    _real_send(server.port, monkeypatch)  # no exception: the 250 after DATA was received
    assert server.received


@pytest.mark.parametrize("port", ["587", "465"])
def test_tls_verifies_certificate_and_host_name(
    port: str, fake_smtp: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SMTP_PORT", port)
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")
    settings = get_settings()
    msg: EmailMessage = smtp.build_message(settings, ["a@b.example"], "s", "b", "<m@x>")
    smtp._send_sync(settings, msg)
    (context,) = fake_smtp.contexts
    assert isinstance(context, ssl.SSLContext)
    assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
