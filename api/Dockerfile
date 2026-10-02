# syntax=docker/dockerfile:1
# steward-api image. Build context is the repo root (docker-compose.yml:
# build: {context: ., dockerfile: api/Dockerfile}).

# --- web: Next.js static export (web/out), served by steward-api at / -------------------------
FROM node:22-slim AS web
ENV NEXT_TELEMETRY_DISABLED=1 COREPACK_ENABLE_DOWNLOAD_PROMPT=0
WORKDIR /web
COPY web/package.json web/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY web/ ./
RUN pnpm build

# --- api -----------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:0.12.10 AS uv

FROM python:3.12.15-slim-bookworm
COPY --from=uv /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY api/steward ./steward
# Synthetic seed for `python -m steward.seed` (steward/seed.py resolves it as /seed).
COPY seed /seed
# Static dashboard (steward/static.py serves /app/web_out).
COPY --from=web /web/out ./web_out

# Same UID/GID as hermes (HERMES_UID/HERMES_GID=10000) so both can write the
# shared memory files under ./data/hermes.
RUN groupadd --gid 10000 steward \
    && useradd --uid 10000 --gid 10000 --no-create-home --shell /usr/sbin/nologin steward
USER 10000:10000

EXPOSE 8787
# One Uvicorn worker (async). Access logs carry method, path and status only, never bodies.
CMD ["uvicorn", "steward.main:app", "--host", "0.0.0.0", "--port", "8787", "--workers", "1", "--log-level", "info"]
