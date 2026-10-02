"""Morning-brief job helpers.

T1.3: in-memory record of the last manual trigger, so brief_save can label its skill_run audit
row 'morning-brief · run now' (manual run within the last 10 minutes) or
'morning-brief · scheduled run' (docs/02 §7b). Not persisted on purpose (docs: "in memory").
"""

import time

MANUAL_WINDOW_S = 600.0
_last_manual_trigger: float | None = None


def record_manual_trigger() -> None:
    global _last_manual_trigger
    _last_manual_trigger = time.monotonic()


def skill_run_summary() -> str:
    recent = (
        _last_manual_trigger is not None
        and time.monotonic() - _last_manual_trigger <= MANUAL_WINDOW_S
    )
    return "morning-brief · run now" if recent else "morning-brief · scheduled run"
