#!/usr/bin/env bash
# Restore this project's Claude Code memory and planning-chat transcript on a new machine.
# Usage (from anywhere): bash .claude/restore.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="$(printf '%s' "$ROOT" | sed 's/[^a-zA-Z0-9]/-/g')"
DEST="$HOME/.claude/projects/$SLUG"
SESSION_ID="a018bea7-e496-4575-8242-9102e8744761"

mkdir -p "$DEST/memory"

# Never overwrite memory that already exists on this machine.
for f in "$ROOT/.claude/memory/"*.md; do
  target="$DEST/memory/$(basename "$f")"
  if [ -e "$target" ]; then
    echo "skip (exists): $target"
  else
    cp "$f" "$target"
    echo "restored: $target"
  fi
done

if [ -f "$ROOT/.claude/session/$SESSION_ID.jsonl" ]; then
  if [ -e "$DEST/$SESSION_ID.jsonl" ]; then
    echo "skip (exists): $DEST/$SESSION_ID.jsonl"
  else
    cp "$ROOT/.claude/session/$SESSION_ID.jsonl" "$DEST/"
    echo "restored: $DEST/$SESSION_ID.jsonl"
  fi
else
  echo "no session transcript found in .claude/session/ (memory only)"
fi

echo
echo "Done. Start Claude Code in $ROOT."
echo "Optional: claude --resume $SESSION_ID"
