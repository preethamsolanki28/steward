"""Real SMTP send for approved demo mail (docs/02 §7a "Mail", D12).

Used only when DEMO_MAIL_REDIRECT is set. The message always goes to that redirect address,
never to the original recipients, with the subject prefix
"[Steward demo → original@x.example] ". smtplib runs in a worker thread (anyio.to_thread).

TLS always verifies the server certificate and host name (STARTTLS and implicit TLS), so the
SMTP password is never sent to an impostor.

Never retried here. Outcomes:
- the server definitely refused (an SMTP reply code: sender, recipients, data, auth) or the
  connection/TLS/login failed before the message was sent -> SmtpError ('failed');
- any timeout, or the connection broke while the message was being sent (smtplib turns a
  socket timeout into SMTPServerDisconnected) -> DeliveryUnknown: it may or may not have been
  accepted, "delivery unknown — check Sent before retrying";
- an error after the server accepted the message (e.g. on QUIT) is ignored: it was sent.
"""

import contextlib
import smtplib
import ssl
import time
from email.message import EmailMessage
from email.utils import formatdate

import anyio

from steward.config import Settings, get_settings

SMTP_TIMEOUT_S = 30.0
DELIVERY_UNKNOWN = "delivery unknown — check Sent before retrying"

# The server answered with a refusal code: the message was not accepted.
_DEFINITE_REFUSALS = (
    smtplib.SMTPSenderRefused,
    smtplib.SMTPRecipientsRefused,
    smtplib.SMTPDataError,
    smtplib.SMTPAuthenticationError,
    smtplib.SMTPHeloError,
    smtplib.SMTPNotSupportedError,
)


class SmtpNotConfigured(RuntimeError):
    pass


class SmtpError(RuntimeError):
    """Not delivered: the server refused, or the connection failed before sending."""


class DeliveryUnknown(RuntimeError):
    """Timed out or broke mid-send: the message may or may not have been accepted."""


def enabled(settings: Settings | None = None) -> bool:
    return bool((settings or get_settings()).demo_mail_redirect)


def subject_for(to: list[str], subject: str) -> str:
    return f"[Steward demo → {', '.join(to)}] {subject}"


def build_message(
    settings: Settings, to: list[str], subject: str, body: str, message_id: str
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = settings.smtp_user or settings.owner_email
    msg["To"] = settings.demo_mail_redirect
    msg["Subject"] = subject_for(to, subject)
    msg["Message-ID"] = message_id
    msg["Date"] = formatdate(localtime=False)
    msg.set_content(body)
    return msg


def tls_context() -> ssl.SSLContext:
    """Verifies the certificate chain and the host name (unlike smtplib's default)."""
    return ssl.create_default_context()


def _is_timeout(exc: BaseException) -> bool:
    return isinstance(exc, TimeoutError) or (
        isinstance(exc, smtplib.SMTPServerDisconnected) and "timed out" in str(exc)
    )


def _describe(exc: BaseException) -> str:
    # Never include credentials; the text is the server's reply or the OS/TLS error.
    return f"SMTP error: {type(exc).__name__}: {exc}"


def _send_sync(settings: Settings, msg: EmailMessage) -> None:
    host, port = settings.smtp_host, settings.smtp_port or 587
    if not host:
        raise SmtpNotConfigured("SMTP_HOST is not set")
    server: smtplib.SMTP | None = None
    sending = accepted = False
    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=SMTP_TIMEOUT_S, context=tls_context())
        else:
            server = smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT_S)
            server.starttls(context=tls_context())
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        sending = True
        server.send_message(msg)
        accepted = True
    except _DEFINITE_REFUSALS as exc:
        raise SmtpError(_describe(exc)) from exc
    except OSError as exc:  # TimeoutError, ssl errors, SMTPServerDisconnected, other SMTP errors
        if sending or _is_timeout(exc):
            raise DeliveryUnknown(DELIVERY_UNKNOWN) from exc
        raise SmtpError(_describe(exc)) from exc
    finally:
        if server is not None:
            if accepted:
                with contextlib.suppress(OSError):
                    server.quit()
            server.close()


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
