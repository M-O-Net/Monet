# Build context is the monorepo root (see docker-compose.yml), so paths below are
# relative to there.
#
# ARG before the first FROM that uses it: CI passes --build-arg DEPS_IMAGE=<cache-restored tag>
# to skip rebuilding the deps layer when its cache hit (see .github/workflows/ci.yml); a local
# build with no --build-arg falls back to the `deps` stage defined right below it.
ARG DEPS_IMAGE=deps
ARG TEST_DEPS_IMAGE=test-deps

FROM python:3.14-slim AS deps
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/
WORKDIR /app
ENV UV_LINK_MODE=copy
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

FROM ${DEPS_IMAGE} AS test-deps
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

FROM ${TEST_DEPS_IMAGE} AS test
COPY apps/api/ .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["./tests/docker-entry.sh"]
CMD ["uv", "run", "pytest", "-v"]

FROM ${DEPS_IMAGE} AS final
COPY apps/api/ .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "monet_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
