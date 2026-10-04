"""Morning-brief Hermes job: startup registration (T1.4) and the manual-trigger record (T1.3).

Registration (docs/02 §7b, D19): on startup steward-api ensures a Hermes cron job named
`morning-brief` exists (GET /api/jobs; if missing, POST /api/jobs with schedule `0 8 * * *`,
the morning-brief skill and local delivery) and stores its id in settings.morning_brief_job_id.
Idempotent: an existing job with that name is reused, so a restart never creates a second one.
It runs as a background task because Hermes starts only after steward-api is healthy.

Manual trigger: brief_save labels its skill_run audit row 'morning-brief · run now' when
POST /api/skills/morning-brief/run (or make brief-now) started a run within the last 10
minutes, else 'morning-brief · scheduled run'. Kept in memory on purpose (docs: "in memory").

Demo one-shot (T5.2): with STEWARD_DEMO=1, startup also registers a one-shot Hermes job
`morning-brief-demo` (same skill, same path as the 08:00 run) due 2 minutes later, so the
scheduled-run beat can be recorded without waiting for 08:00. Its brief is labelled
'morning-brief · scheduled run (demo one-shot)' so it is never mistaken for the 08:00 run.
"""

import asyncio
import logging
import time
from typing import Any

import httpx

from steward import db
from steward.config import get_settings

log = logging.getLogger("steward.jobs")

JOB_NAME = "morning-brief"
JOB_SCHEDULE = "0 8 * * *"
JOB_SKILL = "morning-brief"
JOB_PROMPT = "Run the morning-brief skill."
RETRY_S = 5.0

MANUAL_WINDOW_S = 600.0
_last_manual_trigger: float | None = None

DEMO_JOB_NAME = "morning-brief-demo"
DEMO_SCHEDULE = "in 2m"  # Hermes one-shot syntax (docs/02 §12 "Jobs API")
# Registration -> brief_save: ~2 min until due, up to a minute of ticker lag, then the run itself.
DEMO_WINDOW_S = 900.0
_demo_registered_at: float | None = None


def record_manual_trigger() -> None:
    global _last_manual_trigger
    _last_manual_trigger = time.monotonic()


def skill_run_summary() -> str:
    now = time.monotonic()
    if _last_manual_trigger is not None and now - _last_manual_trigger <= MANUAL_WINDOW_S:
        return "morning-brief · run now"
    if _demo_registered_at is not None and now - _demo_registered_at <= DEMO_WINDOW_S:
        return "morning-brief · scheduled run (demo one-shot)"
    return "morning-brief · scheduled run"


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_settings().hermes_api_key}"}


async def ensure_morning_brief_job(client: httpx.AsyncClient) -> str:
    """One registration attempt. Returns the job id; raises httpx errors if Hermes is down."""
    base = get_settings().hermes_api_url
    r = await client.get(f"{base}/api/jobs", headers=_headers(), timeout=10.0)
    r.raise_for_status()
    jobs: list[dict[str, Any]] = r.json().get("jobs") or []
    existing = [j for j in jobs if j.get("name") == JOB_NAME]
    if existing:
        job_id = str(existing[0]["id"])
    else:
        r = await client.post(
            f"{base}/api/jobs",
            headers=_headers(),
            timeout=10.0,
            json={
                "name": JOB_NAME,
                "schedule": JOB_SCHEDULE,
                "skills": [JOB_SKILL],
                "prompt": JOB_PROMPT,
                "deliver": "local",
            },
        )
        r.raise_for_status()
        job_id = str(r.json()["job"]["id"])
        log.info("registered Hermes job %s (%s)", JOB_NAME, job_id)
    await db.run(lambda conn: db.set_setting(conn, "morning_brief_job_id", job_id))
    return job_id


async def register_demo_job(client: httpx.AsyncClient) -> str:
    """STEWARD_DEMO=1: one-shot run of the same skill 2 minutes from now. Returns its id."""
    global _demo_registered_at
    base = get_settings().hermes_api_url
    r = await client.post(
        f"{base}/api/jobs",
        headers=_headers(),
        timeout=10.0,
        json={
            "name": DEMO_JOB_NAME,
            "schedule": DEMO_SCHEDULE,
            "skills": [JOB_SKILL],
            "prompt": JOB_PROMPT,
            "deliver": "local",
        },
    )
    r.raise_for_status()
    job_id = str(r.json()["job"]["id"])
    _demo_registered_at = time.monotonic()
    log.info("registered one-shot Hermes job %s (%s), due %s", DEMO_JOB_NAME, job_id, DEMO_SCHEDULE)
    return job_id


async def register_on_startup(client: httpx.AsyncClient) -> None:
    """Retry until Hermes answers; then the job id is in settings. Never raises."""
    demo_pending = get_settings().steward_demo
    while True:
        try:
            await ensure_morning_brief_job(client)
            if demo_pending:
                await register_demo_job(client)
                demo_pending = False
            return
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            log.info("Hermes job registration pending (%s); retrying", type(exc).__name__)
        except asyncio.CancelledError:
            raise
        await asyncio.sleep(RETRY_S)


async def current_job_id() -> str | None:
    return await db.run(lambda conn: db.get_setting(conn, "morning_brief_job_id"))
