"""Morning-brief Hermes job: startup registration (T1.4) and the manual-trigger record (T1.3).

Registration (docs/02 §7b, D19): on startup steward-api ensures a Hermes cron job named
`morning-brief` exists (GET /api/jobs; if missing, POST /api/jobs with schedule `0 8 * * *`,
the morning-brief skill and local delivery) and stores its id in settings.morning_brief_job_id.
Idempotent: an existing job with that name is reused, so a restart never creates a second one.
It runs as a background task because Hermes starts only after steward-api is healthy.

Manual trigger: brief_save labels its skill_run audit row 'morning-brief · run now' when
POST /api/skills/morning-brief/run (or make brief-now) started a run within the last 10
minutes, else 'morning-brief · scheduled run'. Kept in memory on purpose (docs: "in memory").
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


def record_manual_trigger() -> None:
    global _last_manual_trigger
    _last_manual_trigger = time.monotonic()


def skill_run_summary() -> str:
    recent = (
        _last_manual_trigger is not None
        and time.monotonic() - _last_manual_trigger <= MANUAL_WINDOW_S
    )
    return "morning-brief · run now" if recent else "morning-brief · scheduled run"


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


async def register_on_startup(client: httpx.AsyncClient) -> None:
    """Retry until Hermes answers; then the job id is in settings. Never raises."""
    while True:
        try:
            await ensure_morning_brief_job(client)
            return
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            log.info("Hermes job registration pending (%s); retrying", type(exc).__name__)
        except asyncio.CancelledError:
            raise
        await asyncio.sleep(RETRY_S)


async def current_job_id() -> str | None:
    return await db.run(lambda conn: db.get_setting(conn, "morning_brief_job_id"))
