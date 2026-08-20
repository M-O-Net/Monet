# Build context is the monorepo root (see docker-compose.yml), so paths below are
# relative to there.
#
# ARG before the first FROM that uses it: CI passes --build-arg DEPS_IMAGE=<cache-restored tag>
# to skip rebuilding the deps layer when its cache hit (see .github/workflows/ci.yml); a local
# build with no --build-arg falls back to the `deps` stage defined right below it.
# TEST_DEPS_IMAGE is the same idiom for the `test-deps` stage below.
ARG DEPS_IMAGE=deps
ARG TEST_DEPS_IMAGE=test-deps

FROM python:3.14-slim AS deps
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/
WORKDIR /app
ENV UV_LINK_MODE=copy
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ── Test deps: the dev dependency group on top of `deps` — still no source ────────────────────
# A stage of its own rather than folding `uv sync --frozen` (dev included) into `test` below:
# that sync would then sit AFTER `COPY apps/api/ .`, so every source edit would invalidate it and
# reinstall ruff/mypy/pytest from scratch. In local dev the `--mount=type=cache` hides most of
# that cost, but CI has no persistent BuildKit cache mount — this layer is what CI caches as a
# tarball keyed purely on the lockfiles (see ci.yml), exactly like `deps`.
FROM ${DEPS_IMAGE} AS test-deps
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# ── Test: source + the suite, run inside the compose network (`just test-api`) ────────────────
FROM ${TEST_DEPS_IMAGE} AS test
COPY apps/api/ .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
ENV PYTHONUNBUFFERED=1
# The entrypoint recreates + migrates the dedicated monet_test DB before handing off to the CMD;
# it refuses to touch any other database (see tests/docker-entry.sh). Passing custom pytest args
# to `docker compose run test` REPLACES this CMD rather than appending to it — the entrypoint
# still runs either way, so `... run --rm test uv run pytest -k foo` is a safe way to narrow a run.
ENTRYPOINT ["./tests/docker-entry.sh"]
CMD ["uv", "run", "pytest", "-v"]

# ── Runtime image. MUST STAY THE LAST STAGE IN THIS FILE ──────────────────────────────────────
# `render.yaml` builds this Dockerfile by path with no way to name a target, so Render gets
# whichever stage happens to be last — put anything after this and production silently starts
# shipping the test image. The compose `api` service and CI's full-image build both name
# `final` explicitly, so this file's ordering is the only unguarded consumer.
FROM ${DEPS_IMAGE} AS final
COPY apps/api/ .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "monet_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
