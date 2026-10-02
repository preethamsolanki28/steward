"""`python -m steward.seed`: load the synthetic seed (docs/03 §11) into steward-api state.

- contacts: from seed/contacts.json; `trusted` comes only from here (source 'seed').
- demo_mail: seed/inbox.json into folder 'inbox'; `received_hours_ago` -> ISO timestamp.
- workspace: seed/workspace copied to WORKSPACE_DIR; `{{SEED_DATE±Nd}}` -> ISO date.
- memories: seed/memories/*.md -> HERMES_DATA_DIR/memories (temp file + os.replace).
- settings: seeded from env, with a new reset_nonce (fresh Hermes session ids).

Relative dates and times use India Standard Time (UTC+05:30, no DST), the persona's zone.
`make demo-reset` deletes steward.db first; run on an existing DB, this reloads the seed-owned
tables and keeps conversations, the ledger, actions, audit rows and morning_brief_job_id.
"""

import json
import os
import re
import shutil
import tempfile
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from steward import db
from steward.config import Settings, get_settings

IST = timezone(timedelta(hours=5, minutes=30), "IST")
SEED_DIR = Path(__file__).resolve().parents[2] / "seed"
DATE_TOKEN = re.compile(r"\{\{SEED_DATE([+-]\d+)d\}\}")


def resolve_dates(text: str, today: date) -> str:
    return DATE_TOKEN.sub(lambda m: (today + timedelta(days=int(m.group(1)))).isoformat(), text)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _clear_dir(root: Path) -> None:
    """Empty WORKSPACE_DIR without following symlinks out of it."""
    root.mkdir(parents=True, exist_ok=True)
    for child in root.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink()
        else:
            shutil.rmtree(child)


def seed_workspace(settings: Settings, today: date, seed_dir: Path = SEED_DIR) -> int:
    src = seed_dir / "workspace"
    dst = settings.workspace_dir
    _clear_dir(dst)
    count = 0
    for file in sorted(src.rglob("*")):
        if file.is_symlink() or not file.is_file():
            continue
        target = dst / file.relative_to(src)
        atomic_write(target, resolve_dates(file.read_text(encoding="utf-8"), today))
        count += 1
    return count


def seed_memories(settings: Settings, seed_dir: Path = SEED_DIR) -> None:
    for name in ("MEMORY.md", "USER.md"):
        text = (seed_dir / "memories" / name).read_text(encoding="utf-8")
        atomic_write(settings.memories_dir / name, text)


def seed_db(settings: Settings, now: datetime, seed_dir: Path = SEED_DIR) -> dict[str, int]:
    contacts = json.loads((seed_dir / "contacts.json").read_text(encoding="utf-8"))
    inbox = json.loads((seed_dir / "inbox.json").read_text(encoding="utf-8"))
    created = now.astimezone(IST).isoformat(timespec="seconds")
    db.init_schema(settings.db_path)
    conn = db.connect(settings.db_path)
    try:
        with conn:
            conn.execute("DELETE FROM contacts")
            conn.executemany(
                "INSERT INTO contacts (name, email, org, trusted, source, created_at) "
                "VALUES (?, ?, ?, ?, 'seed', ?)",
                [
                    (c["name"], c["email"].lower(), c["org"], int(c["trusted"]), created)
                    for c in contacts
                ],
            )
            conn.execute("DELETE FROM demo_mail WHERE folder = 'inbox'")
            conn.executemany(
                "INSERT INTO demo_mail (folder, from_name, from_email, to_emails, subject, body, "
                "ts, is_read) VALUES ('inbox', ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        m["from_name"],
                        m["from_email"].lower(),
                        json.dumps(m["to_emails"]),
                        m["subject"],
                        m["body"],
                        (now - timedelta(hours=int(m["received_hours_ago"])))
                        .astimezone(IST)
                        .isoformat(timespec="seconds"),
                        int(m["is_read"]),
                    )
                    for m in inbox
                ],
            )
            for key, value in {
                "model_primary": settings.model_primary,
                "model_fallback": settings.model_fallback,
                "reasoning_effort": settings.reasoning_effort,
                "owner_email": settings.owner_email,
                "mail_mode": settings.mail_mode,
                "reset_nonce": uuid.uuid4().hex[:12],
            }.items():
                db.set_setting(conn, key, value)
    finally:
        conn.close()
    return {"contacts": len(contacts), "inbox": len(inbox)}


def main() -> None:
    settings = get_settings()
    now = datetime.now(IST)
    counts = seed_db(settings, now)
    files = seed_workspace(settings, now.date())
    seed_memories(settings)
    print(
        f"seeded {counts['contacts']} contacts, {counts['inbox']} inbox emails, "
        f"{files} workspace files, 2 memory files; new reset_nonce"
    )


if __name__ == "__main__":
    main()
