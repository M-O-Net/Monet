set dotenv-load

# Compose reads .env automatically (dotenv-load above); .env.local (a worktree's own port/project
# overrides, see wt-add) needs an explicit second --env-file so it can override .env's values.
_env_flags := "--env-file .env" + (if path_exists(".env.local") == "true" { " --env-file .env.local" } else { "" })
_dc := "docker compose " + _env_flags + " -f docker-compose.yml"
_dc_dev := _dc + " -f docker-compose.dev.yml"

# Show available commands
default:
    @just --list

# ── First-time setup ─────────────────────────────────────────────────────────

install:
    cd apps/api && uv sync
    pnpm install

hooks:
    git config extensions.worktreeConfig true
    git config --worktree core.hooksPath .githooks
    chmod +x .githooks/pre-commit .githooks/pre-push .githooks/land
    @echo "✓ git hooks active (.githooks/)"

# ── PRs: draft while iterating, `just land` to finish ────────────────────────
# Every PR is born a draft (cheap to push to, CI's `changes` job is gated on
# `draft == false`). `just land` is the only path a PR should reach `main` through: full local
# suite, flip ready, wait for CI, merge on green or revert to draft on red. See root AGENTS.md.

pr *ARGS:
    gh pr create --draft {{ARGS}}

check:
    .githooks/pre-commit --manual

land:
    .githooks/land

# ── Full stack (Docker) ───────────────────────────────────────────────────────

# Pre-create the anonymous-volume mountpoints (Docker can't mkdir one inside an already
# read-only bind if the host directory doesn't exist yet — see docker-compose.dev.yml).
# `-V`/`--renew-anon-volumes` makes those volumes recreate from what the fresh build just
# installed, instead of carrying over a previous container's (possibly stale) node_modules.
up:
    mkdir -p apps/web/node_modules packages/api-client/node_modules
    {{_dc_dev}} up -d --build -V

up-prod:
    {{_dc}} up --build

down:
    {{_dc_dev}} down

down-clean:
    {{_dc_dev}} down -v --rmi local --remove-orphans

logs:
    {{_dc_dev}} logs -f

# ── Worktrees ──────────────────────────────────────────────────────────────
# Gives a git worktree its own isolated Docker stack (own project name, own host ports) so
# several agents can work in parallel checkouts without colliding on ports or DB state. See
# root AGENTS.md > Merge gate for why this matters.

wt-add name api_port="" web_port="":
    #!/usr/bin/env bash
    set -euo pipefail
    main_checkout=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
    target="$main_checkout/.claude/worktrees/{{name}}"

    if git -C "$main_checkout" worktree list --porcelain | grep -qx "worktree $target"; then
        echo "✖ A worktree named '{{name}}' already exists at $target" >&2
        exit 1
    fi

    declare -A claimed=()
    for f in "$main_checkout"/.claude/worktrees/*/.env.local; do
        [ -f "$f" ] || continue
        while IFS='=' read -r key val; do
            case "$key" in API_PORT|WEB_PORT) claimed["$val"]="$f" ;; esac
        done < <(grep -E '^(API_PORT|WEB_PORT)=' "$f")
    done

    pick_port() {
        local candidate="$1"
        while [ -n "${claimed[$candidate]:-}" ]; do candidate=$((candidate + 1)); done
        echo "$candidate"
    }

    api_port="{{api_port}}"
    web_port="{{web_port}}"
    [ -z "$api_port" ] && api_port=$(pick_port 8301)
    claimed["$api_port"]="(this worktree)"
    [ -z "$web_port" ] && web_port=$(pick_port 5274)

    if [ "$api_port" = "$web_port" ]; then
        echo "✖ API_PORT and WEB_PORT must differ (both $api_port)" >&2
        exit 1
    fi

    git worktree add "$target" -b "{{name}}"

    env_local_content=$(printf 'COMPOSE_PROJECT_NAME=monet-%s\nAPI_PORT=%s\nWEB_PORT=%s\n' \
        "{{name}}" "$api_port" "$web_port")
    strip_regex=$(printf '%s\n' "$env_local_content" | sed -nE 's/^([A-Z_]+)=.*/\1/p' | paste -sd '|' -)

    if [ -f "$main_checkout/.env" ]; then
        grep -vE "^(${strip_regex})=" "$main_checkout/.env" > "$target/.env" || true
    else
        echo "⚠ $main_checkout/.env does not exist — run 'cp .env.example .env' there first." >&2
        : > "$target/.env"
    fi
    printf '%s' "$env_local_content" > "$target/.env.local"

    (cd "$target" && just install && just hooks)

    echo ""
    echo "✓ worktree '{{name}}' ready: $target"
    echo "  API_PORT=$api_port  WEB_PORT=$web_port  COMPOSE_PROJECT_NAME=monet-{{name}}"
    echo "  cd $target && just up && just migrate"

wt-rm name:
    #!/usr/bin/env bash
    set -euo pipefail
    main_checkout=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
    target="$main_checkout/.claude/worktrees/{{name}}"
    if ! git -C "$main_checkout" worktree list --porcelain | grep -qx "worktree $target"; then
        echo "✖ No worktree named '{{name}}' registered at $target" >&2
        exit 1
    fi
    (cd "$target" && just down-clean) || true
    git -C "$main_checkout" worktree remove "$target" --force
    echo "✓ worktree '{{name}}' removed"

# ── Database ───────────────────────────────────────────────────────────────

migrate:
    {{_dc_dev}} exec api uv run alembic upgrade head

migrate-down:
    {{_dc_dev}} exec api uv run alembic downgrade -1

# Autogenerate proposes, not decides — alembic assigns the revision id and writes a first
# draft; read the result before committing it (see the `sqlmodel.sql.sqltypes.AutoString()`
# import bug in this repo's own migration history for why that's not optional).
migrate-new name:
    {{_dc_dev}} exec api uv run alembic revision --autogenerate -m "{{name}}"

migrate-status:
    {{_dc_dev}} exec api uv run alembic current

# Model↔migration drift gate: fails if a SQLModel table has no matching migration, or a
# migration doesn't match the models, so drift is caught here rather than as a runtime
# schema mismatch.
#
# Not made redundant by `just test-api` also running `alembic check` (see
# apps/api/tests/docker-entry.sh): that one checks a freshly-migrated monet_test, which answers
# "do the models match the migration chain?". This one checks the DEV database, which additionally
# answers "is the schema my running stack is actually using still in step?" — the case where a
# branch switch or a hand-run migration left the dev DB somewhere the migration chain didn't put it.
migrate-check:
    {{_dc_dev}} exec api uv run alembic check

seed:
    {{_dc_dev}} exec api uv run python scripts/seed.py

# ── Code generation ──────────────────────────────────────────────────────────
# Sources .env.local first so API_PORT is always THIS worktree's own value, never a silent
# fallback onto a different worktree's stack.

gen-client:
    #!/usr/bin/env bash
    set -euo pipefail
    [ -f .env.local ] && { set -a; . ./.env.local; set +a; }
    curl -sf "http://localhost:${API_PORT:-8300}/openapi.json" -o apps/web/openapi.json
    cd apps/web && pnpm generate-client

# ── Test / build / lint / format ──────────────────────────────────────────────
# Static analysis (lint-*) is what pre-commit runs, per-commit. Tests/builds (test-api,
# build-web) are what `land` runs, once per PR — see root AGENTS.md > Merge gate for why
# they're split this way.

test: test-api build-web

# Runs the backend suite inside the Docker stack, against a dedicated `monet_test` database that
# the `test` service's entrypoint drops, recreates, migrates and drift-checks (`alembic check`)
# on every run — see apps/api/tests/docker-entry.sh. Never the dev DB: the suite's autouse
# `_clean_db` fixture DELETEs every row, so the old host-side `uv run pytest` (pointed at the dev
# DB by apps/api/.env) wiped the seeded dataset every time it ran.
#
# Running in the stack is also what removes the need for a hand-written apps/api/.env per
# worktree, and what let docker-compose.yml stop publishing a Postgres host port (which every
# worktree collided on).
#
# `--build` keeps the image in step with the lockfile; src/tests/alembic are bind-mounted, so a
# code edit needs no rebuild — but editing them mid-run invalidates the run in progress, so
# discard the result rather than trust it if you do.
test-api:
    {{_dc_dev}} run --rm --build test

build-web:
    cd apps/web && pnpm run build

lint: lint-api lint-web lint-config

lint-api:
    cd apps/api && uv run ruff check . && uv run mypy src

lint-web:
    cd apps/web && pnpm exec eslint . && pnpm exec tsc6 -b

lint-config:
    pnpm exec prettier --check .

fmt:
    cd apps/api && uv run ruff format .
    pnpm exec prettier --write .

# ── Housekeeping ───────────────────────────────────────────────────────────

docker-gc:
    docker container prune -f
    docker image prune -f
    docker volume prune -a -f
    docker builder prune -f
    docker network prune -f
