# Steward Makefile. Targets: up, down, logs, seed, demo-reset, brief-now,
# egress-check, leak-test, test, lint, typecheck, build.
# `make up` needs only Docker; test/lint/typecheck need uv and pnpm.

SHELL := /bin/sh
COMPOSE := docker compose
RUNTIME_UID_GID := 10000:10000

.PHONY: up down logs seed demo-reset brief-now egress-check leak-test test lint typecheck build \
	init check-docker check-env

## up: init (keys, data dirs, Hermes config), then build and start steward-api + hermes
up: check-docker init
	$(COMPOSE) up -d --build

## down: stop and remove both services; ./data and ./workspace persist
down: check-docker
	$(COMPOSE) down

## logs: follow both services' logs (never contain request or response bodies)
logs: check-docker
	$(COMPOSE) logs -f

## seed: load the synthetic seed from seed/ into steward-api
seed:
	@echo "TODO(T1.1): make seed runs 'python -m steward.seed' in steward-api once steward.seed exists." >&2
	@exit 1

## demo-reset: wipe Hermes state + steward.db, reseed (new reset_nonce), start
demo-reset:
	@echo "TODO(T5.2): make demo-reset is implemented in T5.2 (it needs steward.seed from T1.1)." >&2
	@exit 1

## brief-now: trigger the morning-brief Hermes job now (same path as the 08:00 schedule)
brief-now:
	curl -fsS -X POST -H 'X-Steward-Client: web' http://127.0.0.1:8787/api/skills/morning-brief/run

## egress-check: passes only when the hermes container cannot reach the internet.
## Each target counts only if steward-api (on `egress`) reaches it and hermes does not,
## so an offline Mac or a blocked target can never produce a false PASS.
EGRESS_TARGETS := example.com:80 example.com:443 1.1.1.1:80 1.1.1.1:443
TCP_PROBE := import socket, sys; socket.create_connection((sys.argv[1], int(sys.argv[2])), 8)

egress-check: check-docker
	@$(COMPOSE) exec -T hermes true 2>/dev/null || { echo "egress-check: hermes is not running (run make up first)." >&2; exit 1; }
	@$(COMPOSE) exec -T steward-api true 2>/dev/null || { echo "egress-check: steward-api is not running (run make up first)." >&2; exit 1; }
	@$(COMPOSE) exec -T hermes python3 -c "$(TCP_PROBE)" steward-api 8787 \
		|| { echo "egress-check: ERROR - hermes cannot reach steward-api:8787 on the internal network; the probe proves nothing." >&2; exit 1; }
	@echo "egress-check: control  hermes -> steward-api:8787 connected (internal network)"
	@counted=0; for t in $(EGRESS_TARGETS); do h=$${t%:*}; p=$${t##*:}; \
		if ! $(COMPOSE) exec -T steward-api python -c "$(TCP_PROBE)" "$$h" "$$p" >/dev/null 2>&1; then \
			echo "egress-check: $$t  INCONCLUSIVE - steward-api cannot reach it either; skipped"; continue; fi; \
		if $(COMPOSE) exec -T hermes python3 -c "$(TCP_PROBE)" "$$h" "$$p" >/dev/null 2>&1; then \
			echo "egress-check: FAIL - hermes reached $$t" >&2; exit 1; fi; \
		echo "egress-check: $$t  steward-api: connected  hermes: blocked"; counted=$$((counted + 1)); \
	done; \
	if [ "$$counted" -eq 0 ]; then \
		echo "egress-check: INCONCLUSIVE - no target was reachable from steward-api (offline?); nothing proven." >&2; exit 1; fi; \
	echo "egress-check: PASS - hermes cannot reach the internet; steward-api is its only reachable host."

## leak-test: replay recorded Hermes requests through the Shield + live negative control
leak-test:
	@echo "TODO(T2.5): make leak-test is implemented in T2.5." >&2
	@exit 1

## test / lint / typecheck: backend checks (uv) and web typecheck (pnpm)
test:
	cd api && uv run pytest

lint:
	cd api && uv run ruff check .

typecheck:
	cd api && uv run pyright
	pnpm --dir web exec tsc --noEmit

## build: build the steward-api image (its node:22 stage builds web/out once web/ exists)
build: check-docker
	$(COMPOSE) build

# --- helpers -----------------------------------------------------------------

check-docker:
	@docker info >/dev/null 2>&1 || { \
		echo "Docker Desktop is not running. Start Docker Desktop (VM capped at 6 GB), then re-run make." >&2; \
		exit 1; }

check-env:
	@test -f .env || { \
		echo "No .env file. Run: cp .env.example .env  (then fill in NEBIUS_API_KEY and TAVILY_API_KEY)." >&2; \
		exit 1; }

# Shared init step for `make up` and `make demo-reset`:
# generate missing secrets, create data dirs, render the Hermes config, mark no-bundled-skills.
init: check-env
	@if [ -n "$$(tail -c1 .env)" ]; then echo >> .env; fi
	@for k in STEWARD_PROXY_KEY STEWARD_MCP_TOKEN HERMES_API_KEY; do \
		if ! grep -Eq "^$$k=[[:space:]]*[\"']?[^[:space:]\"']" .env; then \
			v=$$(LC_ALL=C od -An -N32 -tx1 /dev/urandom | tr -d ' \n'); \
			if grep -Eq "^$$k=" .env; then \
				sed -i.bak "s|^$$k=.*|$$k=$$v|" .env && rm -f .env.bak; \
			else printf '%s=%s\n' "$$k" "$$v" >> .env; fi; \
			echo "init: generated $$k in .env"; \
		fi; \
	done
	@mkdir -p data/hermes workspace
	@# Render = copy: Hermes itself expands the ${VAR} placeholders from its container env,
	@# so no secret is written into data/hermes/config.yaml (= /opt/data/config.yaml in hermes).
	@cp hermes/config.yaml.tmpl data/hermes/config.yaml 2>/dev/null \
		|| sudo -n cp hermes/config.yaml.tmpl data/hermes/config.yaml
	@touch data/hermes/.no-bundled-skills 2>/dev/null || sudo -n touch data/hermes/.no-bundled-skills
	@if [ "$$(uname -s)" = Linux ]; then \
		chown -R $(RUNTIME_UID_GID) data workspace 2>/dev/null \
		|| sudo -n chown -R $(RUNTIME_UID_GID) data workspace \
		|| { echo "init: run: sudo chown -R $(RUNTIME_UID_GID) data workspace" >&2; exit 1; }; \
	fi
