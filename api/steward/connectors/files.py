"""Workspace files under WORKSPACE_DIR, always through safe_path (docs/02 §7a, AGENTS.md).

safe_path(rel) rejects absolute paths, NUL bytes, `..` components and symlinks anywhere on the
path, and requires realpath + commonpath to equal WORKSPACE_DIR.
"""

import os
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from steward.config import get_settings

MAX_READ_BYTES = 256 * 1024


class UnsafePath(ValueError):
    pass


def safe_path(rel: str, root: Path | None = None) -> Path:
    base = Path(os.path.realpath(root or get_settings().workspace_dir))
    if "\x00" in rel:
        raise UnsafePath("path contains NUL")
    posix = PurePosixPath(rel.replace("\\", "/"))
    if posix.is_absolute() or rel.startswith(("/", "\\")) or (len(rel) > 1 and rel[1] == ":"):
        raise UnsafePath("absolute paths are not allowed")
    if any(part == ".." for part in posix.parts):
        raise UnsafePath("'..' is not allowed")
    candidate = base
    for part in posix.parts:
        if part in ("", "."):
            continue
        candidate = candidate / part
        if candidate.is_symlink():
            raise UnsafePath("symlinks are not allowed")
    real = Path(os.path.realpath(candidate))
    if os.path.commonpath([real, base]) != str(base):
        raise UnsafePath("path escapes the workspace")
    return real


def _rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def list_files(rel_dir: str = "") -> list[dict[str, Any]]:
    base = Path(os.path.realpath(get_settings().workspace_dir))
    start = safe_path(rel_dir or ".")
    if not start.is_dir():
        raise UnsafePath("not a directory")
    out = []
    for dirpath, dirnames, filenames in os.walk(start, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not (Path(dirpath) / d).is_symlink())
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.is_symlink() or not path.is_file():
                continue
            stat = path.stat()
            out.append(
                {
                    "path": _rel(path, base),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(
                        timespec="seconds"
                    ),
                }
            )
    return out


def read_file(rel: str) -> dict[str, str]:
    path = safe_path(rel)
    if not path.is_file():
        raise UnsafePath("file not found")
    if path.stat().st_size > MAX_READ_BYTES:
        raise UnsafePath("file too large")
    base = Path(os.path.realpath(get_settings().workspace_dir))
    return {"path": _rel(path, base), "content": path.read_text(encoding="utf-8", errors="replace")}
