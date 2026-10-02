"""steward MCP server at /mcp. T0.3: STUB with 3 tools over the self-contained Acme fixture.

Hermes registers it as `steward`, so the model sees the production names
(mcp_steward_files_read, mcp_steward_mail_search, mcp_steward_mail_send). Signatures and return
shapes follow docs/02 §6. mail_send never sends: it returns the pending-action message.
T1.3 replaces this stub with the real steward-tools server (9 tools, safe_path, audit rows).
"""

import itertools
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from steward import t03_experiment, t03_fixture

mcp_server = MCPServer(name="steward-tools")
_action_ids = itertools.count(1)


async def _context() -> tuple[str, t03_fixture.FixtureName]:
    control = await t03_experiment.read_control()
    fixture: t03_fixture.FixtureName = (
        "pseudonymized" if control.get("fixture") == "pseudonymized" else "plain"
    )
    return str(control.get("run_id") or "adhoc"), fixture


async def _log(run_id: str, tool: str, args: dict[str, Any]) -> None:
    await t03_experiment.record(run_id, "tools.jsonl", {"tool": tool, "args": args})


@mcp_server.tool()
async def files_read(path: str) -> dict[str, str]:
    """Read a text file from the workspace, e.g. invoices/INV-0042.md."""
    run_id, fixture = await _context()
    await _log(run_id, "files_read", {"path": path})
    if path.strip().lstrip("./") != "invoices/INV-0042.md":
        return {"path": path, "content": "error: file not found"}
    content = t03_fixture.invoice(fixture)
    return {"path": path, "content": f'<untrusted source="file">{content}</untrusted>'}


@mcp_server.tool()
async def mail_search(query: str, limit: int = 10) -> list[dict[str, str]]:
    """Search the mailbox. Returns the newest matching emails first."""
    run_id, fixture = await _context()
    await _log(run_id, "mail_search", {"query": query, "limit": limit})
    terms = [t.casefold() for t in query.split() if t.strip()]
    hits = []
    for email in t03_fixture.emails(fixture):
        haystack = f"{email['from']} {email['subject']} {email['body']}".casefold()
        if not terms or any(term in haystack for term in terms):
            hits.append(
                {
                    "id": email["id"],
                    "from": email["from"],
                    "subject": email["subject"],
                    "date": email["date"],
                    "snippet": email["body"][:200],
                }
            )
    return hits[: max(0, limit)]


@mcp_server.tool()
async def mail_send(
    to: list[str], subject: str, body: str, in_reply_to: str | None = None
) -> dict[str, Any]:
    """Queue an email for the user's approval. Never sends directly."""
    run_id, _ = await _context()
    await _log(
        run_id,
        "mail_send",
        {"to": to, "subject": subject, "body": body, "in_reply_to": in_reply_to},
    )
    action_id = next(_action_ids)
    return {
        "action_id": action_id,
        "status": "pending",
        "risk": "low",
        "message": f"Queued for approval as action #{action_id}. The user will review it.",
    }


def build_mcp_app():
    """Streamable HTTP app; the endpoint is exactly /mcp once mounted at the root (D20)."""
    return mcp_server.streamable_http_app(
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=["steward-api:*", "127.0.0.1:*", "localhost:*"],
        ),
    )
