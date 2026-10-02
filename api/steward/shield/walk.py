"""walk_strings + pseudonymize / re-identify / neutralize (docs/02 §7a steps 4-6 and 9).

walk_strings visits every string leaf of a request EXCEPT the skip-list: the values of `model`,
`role`, `tool_call_id`, `id`, `type`, `function.name`, the whole `tools[]` definitions, and
`response_format` (a JSON schema; T0.4 recorded that it carries no text). Each
`function.arguments` string is JSON-parsed, its leaves processed, and re-serialized with
ensure_ascii=False (falls back to plain-text processing if it is not JSON).

The leak check (leakcheck.py) deliberately does NOT use the skip-list: it scans every leaf.
"""

import json
import re
from collections import Counter
from collections.abc import Callable
from typing import Any

from steward.shield.detectors import AliasIndex, find_spans
from steward.shield.vault import Vault

SKIP_KEYS = frozenset({"model", "role", "tool_call_id", "id", "type", "name"})
SKIP_TOP = frozenset({"tools", "response_format"})
TOLERANT = re.compile(r"\[{1,2}\s*([A-Za-z]+)_(\d+)\s*\]{1,2}")


def _walk(obj: Any, fn: Callable[[str], str], parent_key: str | None, in_function: bool) -> Any:
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, list):
        return [_walk(v, fn, parent_key, in_function) for v in obj]
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        is_function = parent_key == "function"
        for key, value in obj.items():
            if key in SKIP_KEYS and isinstance(value, str):
                # `name` is skipped only as function.name; other `name` fields are text.
                if key != "name" or is_function:
                    out[key] = value
                    continue
            if is_function and key == "arguments" and isinstance(value, str):
                out[key] = _walk_arguments(value, fn)
                continue
            out[key] = _walk(value, fn, key, in_function or is_function)
        return out
    return obj


def _walk_arguments(raw: str, fn: Callable[[str], str]) -> str:
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return fn(raw)
    return json.dumps(_walk(parsed, fn, None, False), ensure_ascii=False)


def walk_strings(request: dict[str, Any], fn: Callable[[str], str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in request.items():
        if key in SKIP_TOP or (key in SKIP_KEYS and key != "name" and isinstance(value, str)):
            out[key] = value
        else:
            out[key] = _walk(value, fn, key, False)
    return out


def neutralize(text: str) -> str:
    """Inbound placeholder syntax can never be re-identified: only proxy-minted ones are."""
    return text.replace("[[", "⟦").replace("]]", "⟧")


class Pseudonymizer:
    def __init__(self, index: AliasIndex, vault: Vault) -> None:
        self.index = index
        self.vault = vault
        self.kinds: Counter[str] = Counter()

    @property
    def masked(self) -> int:
        return sum(self.kinds.values())

    def __call__(self, text: str) -> str:
        text = neutralize(text)
        spans = find_spans(text, self.index)
        if not spans:
            return text
        parts, last = [], 0
        for s in spans:
            parts.append(text[last : s.start])
            parts.append(self.vault.placeholder(s.kind, s.canonical))
            self.kinds[s.kind] += 1
            last = s.end
        parts.append(text[last:])
        return "".join(parts)


def pseudonymize(
    request: dict[str, Any], index: AliasIndex, vault: Vault
) -> tuple[dict[str, Any], Pseudonymizer]:
    p = Pseudonymizer(index, vault)
    return walk_strings(request, p), p


class Reidentifier:
    def __init__(self, vault: Vault) -> None:
        self.vault = vault
        self.restored = 0
        self.unknown = 0

    def __call__(self, text: str) -> str:
        def sub(m: re.Match[str]) -> str:
            placeholder = f"[[{m.group(1).upper()}_{int(m.group(2))}]]"
            value = self.vault.value(placeholder)
            if value is None:
                self.unknown += 1
                return m.group(0)
            self.restored += 1
            return value

        return TOLERANT.sub(sub, text)


def _walk_all(obj: Any, fn: Callable[[str], str], parent_key: str | None = None) -> Any:
    """Every string leaf, parsing function.arguments as JSON (used for responses)."""
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, list):
        return [_walk_all(v, fn, parent_key) for v in obj]
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if parent_key == "function" and key == "arguments" and isinstance(value, str):
                out[key] = _walk_arguments_all(value, fn)
            elif parent_key == "function" and key == "name":
                out[key] = value
            elif key in {
                "id",
                "object",
                "model",
                "role",
                "type",
                "finish_reason",
                "system_fingerprint",
                "tool_call_id",
            } and isinstance(value, str):
                out[key] = value
            else:
                out[key] = _walk_all(value, fn, key)
        return out
    return obj


def _walk_arguments_all(raw: str, fn: Callable[[str], str]) -> str:
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return fn(raw)
    return json.dumps(_walk_all(parsed, fn), ensure_ascii=False)


def reidentify(obj: Any, vault: Vault) -> tuple[Any, Reidentifier]:
    """Restore every proxy-minted placeholder in a response (content, reasoning_content,
    reasoning, tool_calls[].function.arguments, ...). Unknown placeholders stay, counted."""
    r = Reidentifier(vault)
    return _walk_all(obj, r), r
