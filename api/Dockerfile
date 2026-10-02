# syntax=docker/dockerfile:1
# steward-api image. Build context is the repo root (docker-compose.yml:
# build: {context: ., dockerfile: api/Dockerfile}).
# TODO(T1.1): add the node:22 stage that runs `corepack enable && pnpm install
# --frozen-lockfile && pnpm build` in web/ (NEXT_TELEMETRY_DISABLED=1) and copy
# web/out to the path steward-api serves.

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

# Same UID/GID as hermes (HERMES_UID/HERMES_GID=10000) so both can write the
# shared memory files under ./data/hermes.
RUN groupadd --gid 10000 steward \
    && useradd --uid 10000 --gid 10000 --no-create-home --shell /usr/sbin/nologin steward
USER 10000:10000

EXPOSE 8787
# One Uvicorn worker (async). Access logs carry method, path and status only, never bodies.
CMD ["uvicorn", "steward.main:app", "--host", "0.0.0.0", "--port", "8787", "--workers", "1", "--log-level", "info"]
