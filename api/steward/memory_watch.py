"""Agent memory-change audit (docs/02 §7a "After the final reply").

steward-api hashes memories/MEMORY.md and USER.md before and after each chat turn; on a change it
writes audit_events(kind='memory_edit') with a unified diff in `detail` ("Memory changed by
Steward — review" in the Activity rail). Memory poisoning is a documented attack on Hermes, so
every agent-made change is shown to the user.
"""

import difflib
import hashlib
from pathlib import Path

from steward.config import get_settings

FILES = ("MEMORY.md", "USER.md")
SUMMARY = "Memory changed by Steward"


def snapshot(memories_dir: Path | None = None) -> dict[str, str]:
    base = memories_dir or get_settings().memories_dir
    out = {}
    for name in FILES:
        path = base / name
        out[name] = path.read_text(encoding="utf-8") if path.exists() else ""
    return out


def digest(snap: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name in FILES:
        h.update(name.encode() + b"\0" + snap.get(name, "").encode() + b"\0")
    return h.hexdigest()


def unified_diff(before: dict[str, str], after: dict[str, str]) -> str:
    parts = []
    for name in FILES:
        a, b = before.get(name, ""), after.get(name, "")
        if a != b:
            lines = difflib.unified_diff(
                a.splitlines(), b.splitlines(), f"a/{name}", f"b/{name}", lineterm=""
            )
            parts.append("\n".join(lines))
    return "\n".join(parts) + "\n" if parts else ""
