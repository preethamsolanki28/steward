"""Control plane /api/* (docs/02 §6). Called by the dashboard only; guarded by steward.guards."""

import re
import sqlite3
from pathlib import Path
from typing import Any, Literal

import anyio
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from steward import db, hermes_client, jobs, memory_watch
from steward import health as health_probe
from steward.config import get_settings
from steward.seed import atomic_write

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


# --- briefs and skills (T1.7) ------------------------------------------------------------------

SKILLS_DIR = Path("/opt/steward-skills")  # ./skills mounted read-only (docker-compose.yml)
RUNNABLE_SKILL = "morning-brief"
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def _skill_meta(path: Path) -> dict[str, str] | None:
    match = _FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        return None
    meta = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() in ("name", "description"):
            meta[key.strip()] = value.strip().strip('"')
    return meta if "name" in meta else None


def _hermes_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_settings().hermes_api_key}"}


@router.get("/skills")
async def skills() -> list[dict[str, Any]]:
    def scan() -> list[dict[str, Any]]:
        out = []
        for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            meta = _skill_meta(skill_file)
            if meta:
                out.append(
                    {
                        "name": meta["name"],
                        "description": meta.get("description", ""),
                        "runnable": meta["name"] == RUNNABLE_SKILL,
                    }
                )
        return out

    return await anyio.to_thread.run_sync(scan)


@router.get("/briefs/latest")
async def briefs_latest(request: Request) -> dict[str, Any]:
    def load(conn: sqlite3.Connection) -> tuple[dict[str, Any] | None, str | None]:
        row = conn.execute(
            "SELECT id, created_at, content_md FROM briefs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return (dict(row) if row else None), db.get_setting(conn, "morning_brief_job_id")

    brief, job_id = await db.run(load)
    job = None
    if job_id:
        try:
            r = await request.app.state.http.get(
                f"{get_settings().hermes_api_url}/api/jobs/{job_id}",
                headers=_hermes_headers(),
                timeout=5.0,
            )
            if r.status_code == 200:
                data = r.json().get("job") or {}
                job = {k: data.get(k) for k in ("last_run_at", "last_status", "next_run_at")}
        except (httpx.HTTPError, ValueError):
            job = None
    return {"brief": brief, "job": job}


@router.post("/skills/morning-brief/run")
async def run_morning_brief(request: Request) -> JSONResponse:
    job_id = await jobs.current_job_id()
    if not job_id:
        return JSONResponse(
            status_code=503, content={"detail": "The morning-brief job is not registered yet"}
        )
    jobs.record_manual_trigger()
    try:
        r = await request.app.state.http.post(
            f"{get_settings().hermes_api_url}/api/jobs/{job_id}/run",
            headers=_hermes_headers(),
            timeout=30.0,
        )
    except httpx.HTTPError:
        return JSONResponse(status_code=502, content={"detail": "Hermes is unreachable"})
    if r.status_code != 200:
        return JSONResponse(
            status_code=502, content={"detail": f"Hermes refused the run (HTTP {r.status_code})"}
        )
    return JSONResponse({"ok": True})


# --- memory (T1.8) -----------------------------------------------------------------------------

MEMORY_FILES = {"memory": ("MEMORY.md", 2200), "user": ("USER.md", 1375)}
ENTRY_DELIMITER = "\n§\n"


def _read_entries(name: str) -> list[str]:
    path = get_settings().memories_dir / name
    raw = path.read_text(encoding="utf-8") if path.exists() else ""
    return [e for e in (x.strip() for x in raw.split(ENTRY_DELIMITER)) if e]


def _joined_chars(entries: list[str]) -> int:
    return len(ENTRY_DELIMITER.join(entries))  # str length = code points, as the UI counts


@router.get("/memory")
async def memory_get() -> dict[str, Any]:
    def read() -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, (name, limit) in MEMORY_FILES.items():
            entries = _read_entries(name)
            out[key] = {"entries": entries, "chars": _joined_chars(entries), "limit": limit}
        return out

    return await anyio.to_thread.run_sync(read)


class MemoryPut(BaseModel):
    file: Literal["memory", "user"]
    entries: list[str]


@router.put("/memory")
async def memory_put(body: MemoryPut) -> JSONResponse:
    name, limit = MEMORY_FILES[body.file]
    entries = [e.strip() for e in body.entries if e.strip()]
    for entry in entries:
        if any(line.strip() == "§" for line in entry.splitlines()):
            return JSONResponse(
                status_code=400, content={"detail": "An entry cannot contain a line that is only §"}
            )
    chars = _joined_chars(entries)
    if chars > limit:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Memory not saved — over the limit ({chars} > {limit})"},
        )
    target = get_settings().memories_dir / name
    # Temp file + os.replace in the same directory; steward-api runs as UID 10000 like Hermes.
    await anyio.to_thread.run_sync(atomic_write, target, ENTRY_DELIMITER.join(entries))
    return JSONResponse({"ok": True})
