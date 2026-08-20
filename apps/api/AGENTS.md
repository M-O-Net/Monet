Backend-local conventions. See root `AGENTS.md` first — this only adds detail specific to
`apps/api`.

## Layout

- `src/monet_api/core/` — cross-cutting: `config.py` (pydantic-settings), `db.py` (async engine +
  `get_session` dependency), `schemas.py` (the shared `ORMModel` base).
- `src/monet_api/objects/` — the one domain, split `router.py` → `service.py` → `repository.py`
  the same way Muse's multi-domain backend does even for a single self-contained domain: `router.py`
  is HTTP only (path/status/`response_model`/`operation_id`, no SQL); `service.py` is business
  logic (404/400 translation, assembling a response schema out of several repository calls) and
  owns no SQL of its own; `repository.py` is the only file that touches `select`/`session.exec`.
  Plus `models.py` (SQLModel tables) and `schemas.py` (I/O models).
- `scripts/seed.py` — wipes and reinserts the v0 demo dataset. `uv run python scripts/seed.py`
  from this directory, or `just seed` from the repo root.
- `alembic/` — migrations. `uv run alembic revision --autogenerate -m "..."` needs a running
  Postgres to diff against (`just up` starts one).
- `tests/` — pytest suite, plus the two files that set up the database it runs against:
  `docker-entry.sh` (the `test` container's ENTRYPOINT) and `reset_test_db.py`.

## Tests

`just test-api`, from the repo root. There is no supported way to run the suite on the host, and
`cd apps/api && uv run pytest` is not it — see below.

The suite runs as the `test` service of the dev compose stack (`docker-compose.dev.yml`, built
from this Dockerfile's `test` stage, profile-gated so `just up` never starts it). Every run:

1. drops and recreates a dedicated **`monet_test`** database — separate from the dev `monet` one;
2. `alembic upgrade head` against it, from empty, so the run always exercises this branch's own
   migration chain rather than whatever state the last branch left behind;
3. `alembic check`, which fails the run on model↔migration drift — a new SQLModel table without
   a migration cannot pass tests;
4. pytest.

Steps 1–3 are guarded, twice independently (`docker-entry.sh`'s `case` and `reset_test_db.py`'s
own check): if `DATABASE_URL` names anything other than a database called `monet_test`, they skip
rather than drop it. That guard is the point of the whole arrangement. `conftest.py`'s autouse
`_clean_db` fixture DELETEs every row in every table, so a suite pointed at the dev database wipes
the seeded dataset — which is exactly what host-side pytest did, because `apps/api/.env` pointed
`DATABASE_URL` at the dev DB.

`src/`, `tests/` and `alembic/` are bind-mounted into the container, so editing a test needs no
rebuild; `just test-api`'s `--build` covers dependency changes. To narrow a run, append pytest
args — `docker compose --env-file .env --env-file .env.local -f docker-compose.yml -f
docker-compose.dev.yml run --rm test uv run pytest -k something`. That replaces the image's CMD
but not its ENTRYPOINT, so the DB is still recreated and migrated first.

## Running locally without Docker

Don't, for tests (above). For a bare uvicorn against a Postgres you supply yourself:

```
uv sync
DATABASE_URL=postgresql+asyncpg://... uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://... uv run uvicorn monet_api.main:app --reload
```

The compose stack publishes no Postgres host port (see `docker-compose.yml`), so that
`DATABASE_URL` cannot point at the dev stack's database — bring your own, or just use `just up`.

## Gotchas

- The async engine/session is created once at import time (`core/db.py`). Tests therefore need a
  **session-scoped** event loop, not pytest-asyncio's per-test default — asyncpg connections are
  bound to the loop that opened them, and a per-test loop breaks the shared connection pool on the
  second test. See `pyproject.toml`'s `asyncio_default_fixture_loop_scope` /
  `asyncio_default_test_loop_scope`.
- `mypy --strict`'s `disallow_any_explicit` is **not** enabled here — it false-positives against
  SQLModel/Pydantic's own plugin-generated code on essentially every model field, not against
  anything we actually write.
- Deleting an object still referenced as an operator or as a relation input/output is blocked at
  the DB level (`RESTRICT`, the SQLAlchemy/Postgres default) and translated into a clean 400 in
  `delete_object` — relations aren't cascade-deleted just because one of their objects went away.
  Deleting a _relation_, by contrast, cascades to its `relation_input`/`relation_output` rows,
  since those only exist in service of that one relation.
