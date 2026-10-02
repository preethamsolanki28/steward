"""Control plane /api/* (docs/02 §6). Called by the dashboard only; guarded by steward.guards."""

import sqlite3
from typing import Any

import anyio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from steward import db, hermes_client, memory_watch
from steward import health as health_probe

router = APIRouter(prefix="/api")

TITLE_CHARS = 60


@router.get("/health")
async def health(request: Request) -> dict[str, object]:
    return await health_probe.health(request.app.state.http)


# --- chat (T1.6) -------------------------------------------------------------------------------


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(min_length=1, max_length=20_000)


@router.post("/chat")
async def chat(body: ChatRequest, request: Request) -> JSONResponse:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message is empty")

    def start_turn(conn: sqlite3.Connection) -> tuple[int, str] | None:
        now = db.now_iso()
        if body.conversation_id is not None:
            row = conn.execute(
                "SELECT id, hermes_session_id FROM conversations WHERE id = ?",
                (body.conversation_id,),
            ).fetchone()
            if row is None:
                return None
            conv_id, session = int(row["id"]), str(row["hermes_session_id"])
        else:
            nonce = db.get_setting(conn, "reset_nonce") or "nononce"
            title = message if len(message) <= TITLE_CHARS else message[: TITLE_CHARS - 1] + "…"
            cur = conn.execute(
                "INSERT INTO conversations (title, hermes_session_id, created_at, updated_at) "
                "VALUES (?, '', ?, ?)",
                (title, now, now),
            )
            conv_id = int(cur.lastrowid or 0)
            session = hermes_client.session_id(nonce, conv_id)
            conn.execute(
                "UPDATE conversations SET hermes_session_id = ? WHERE id = ?", (session, conv_id)
            )
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) "
            "VALUES (?, 'user', ?, ?)",
            (conv_id, message, now),
        )
        conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
        return conv_id, session

    started = await db.run(start_turn)
    if started is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    conv_id, session = started

    before = await anyio.to_thread.run_sync(memory_watch.snapshot)
    try:
        reply = await hermes_client.chat(request.app.state.http, session, message)
        error: tuple[int, str] | None = None
    except hermes_client.ChatTimeout:
        reply, error = "", (504, hermes_client.STILL_WORKING)
    except hermes_client.ChatFailed:
        reply, error = "", (502, hermes_client.MODEL_UNAVAILABLE)
    after = await anyio.to_thread.run_sync(memory_watch.snapshot)

    def finish_turn(conn: sqlite3.Connection) -> int | None:
        if memory_watch.digest(before) != memory_watch.digest(after):
            db.audit(
                conn,
                "memory_edit",
                memory_watch.SUMMARY,
                detail=memory_watch.unified_diff(before, after),
            )
        if error is not None:
            return None
        now = db.now_iso()
        cur = conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) "
            "VALUES (?, 'assistant', ?, ?)",
            (conv_id, reply, now),
        )
        conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
        return int(cur.lastrowid or 0)

    message_id = await db.run(finish_turn)
    if error is not None:
        return JSONResponse(
            status_code=error[0], content={"detail": error[1], "conversation_id": conv_id}
        )
    return JSONResponse({"conversation_id": conv_id, "reply": reply, "message_id": message_id})


@router.get("/conversations")
async def conversations() -> list[dict[str, Any]]:
    return await db.run(
        lambda conn: db.rows(
            conn.execute(
                "SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC, id DESC"
            )
        )
    )


@router.get("/conversations/{conversation_id}")
async def conversation(conversation_id: int) -> dict[str, Any]:
    def load(conn: sqlite3.Connection) -> dict[str, Any] | None:
        row = conn.execute(
            "SELECT id, title FROM conversations WHERE id = ?", (conversation_id,)
        ).fetchone()
        if row is None:
            return None
        msgs = db.rows(
            conn.execute(
                "SELECT id, role, content, created_at FROM messages WHERE conversation_id = ? "
                "ORDER BY id",
                (conversation_id,),
            )
        )
        return {"id": row["id"], "title": row["title"], "messages": msgs}

    result = await db.run(load)
    if result is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return result
