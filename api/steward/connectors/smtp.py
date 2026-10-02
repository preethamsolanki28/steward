"""Real SMTP send for approved demo mail (docs/02 §7a "Mail", D12).

Used only when DEMO_MAIL_REDIRECT is set. The message always goes to that redirect address,
never to the original recipients, with the subject prefix
"[Steward demo → original@x.example] ". smtplib runs in a worker thread (anyio.to_thread).
Never retried here: an SMTP timeout means "delivery unknown" and the caller records it.
"""

import smtplib
import time
from email.message import EmailMessage
from email.utils import formatdate

import anyio

from steward.config import Settings, get_settings

SMTP_TIMEOUT_S = 30.0
DELIVERY_UNKNOWN = "delivery unknown — check Sent before retrying"


class SmtpNotConfigured(RuntimeError):
    pass


class SmtpError(RuntimeError):
    """The server refused the message (auth, recipient, connection refused...)."""


class DeliveryUnknown(RuntimeError):
    """Timed out mid-conversation: the message may or may not have been accepted."""


def enabled(settings: Settings | None = None) -> bool:
    return bool((settings or get_settings()).demo_mail_redirect)


def build_message(
    settings: Settings, to: list[str], subject: str, body: str, message_id: str
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = settings.smtp_user or settings.owner_email
    msg["To"] = settings.demo_mail_redirect
    msg["Subject"] = f"[Steward demo → {', '.join(to)}] {subject}"
    msg["Message-ID"] = message_id
    msg["Date"] = formatdate(localtime=False)
    msg.set_content(body)
    return msg


def _send_sync(settings: Settings, msg: EmailMessage) -> None:
    host, port = settings.smtp_host, settings.smtp_port or 587
    if not host:
        raise SmtpNotConfigured("SMTP_HOST is not set")
    try:
        if port == 465:
            server: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=SMTP_TIMEOUT_S)
        else:
            server = smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT_S)
            server.starttls()
        with server:
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except TimeoutError as exc:
        raise DeliveryUnknown(DELIVERY_UNKNOWN) from exc
    except (smtplib.SMTPException, OSError) as exc:
        # Never include credentials; the exception text is the server's reply or the OS error.
        raise SmtpError(f"SMTP error: {type(exc).__name__}: {exc}") from exc


async def send(to: list[str], subject: str, body: str, message_id: str) -> int:
    """Send via the redirect address. Returns latency in ms. Raises SmtpNotConfigured,
    SmtpError or DeliveryUnknown. Callers check enabled() first."""
    settings = get_settings()
    if not settings.demo_mail_redirect:
        raise SmtpNotConfigured("DEMO_MAIL_REDIRECT is not set")
    msg = build_message(settings, to, subject, body, message_id)
    started = time.monotonic()
    await anyio.to_thread.run_sync(_send_sync, settings, msg)
    return int((time.monotonic() - started) * 1000)
