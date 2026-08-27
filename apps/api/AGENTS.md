Backend-local conventions. See root `AGENTS.md` first — this only adds detail specific to
`apps/api`.

## Layout

- `src/monet_api/core/` — cross-cutting: `config.py` (pydantic-settings), `db.py` (async engine +
  `get_session` dependency), `schemas.py` (the shared `ORMModel` base).
- `src/monet_api/implementations/` — the second domain, same split. Stores and serves implementation
  `code` as opaque text: **nothing here ever executes it**, and there is no sympy dependency. It
  runs in the visitor's browser (see root `AGENTS.md` > Implementations).
- `src/monet_api/objects/` — the first domain, split `router.py` → `service.py` → `repository.py`
  the same way Muse's multi-domain backend does even for a single self-contained domain: `router.py`
  is HTTP only (path/status/`response_model`/`operation_id`, no SQL); `service.py` is business
  logic (404/400 translation, assembling a response schema out of several repository calls) and
  owns no SQL of its own; `repository.py` is the only file that touches `select`/`session.exec`.
  Plus `models.py` (SQLModel tables) and `schemas.py` (I/O models).
- `scripts/implementations/*.py` — the seeded implementations. **Seed data, not code**:
  `seed.py` reads each file's text into the `implementations` table. They are written against the
  sympy names the browser sandbox injects, which is why `ruff.toml` exempts the directory from
  F821. Nothing imports them, and nothing on the server executes them.
- `scripts/seed.py` — wipes and reinserts the v0 demo dataset; `scripts/import_atlas.py` then
  adds the KnotInfo and graph-census data from `scripts/data/*.json.gz`, reusing any object that
  is already there. `just seed` runs both. `scripts/fetch_atlas.py` (`just atlas-fetch`)
  regenerates those data files from packaged libraries, reaching no server.
- `alembic/` — migrations. Autogenerate with `just migrate-new "..."`, which runs inside the
  stack: that is the only place a Postgres to diff against is reachable.
- `tests/` — pytest suite, plus `docker-entry.sh` and `reset_test_db.py`, which set up the
  database it runs against.

## Tests

`just test-api`, from the repo root — the suite runs as the dev stack's profile-gated `test`
service, never on the host. Each run drops and recreates a dedicated **`monet_test`** database,
migrates it from empty, runs `alembic check` (so a SQLModel table with no migration fails the
run), then pytest. `docker-entry.sh` and `reset_test_db.py` each independently refuse a
`DATABASE_URL` naming anything but `monet_test`, and that guard is the point: `conftest.py`'s
autouse `_clean_db` DELETEs every row in every table, so a suite pointed at the dev database
wipes the seeded dataset.

`src/`, `tests/` and `alembic/` are bind-mounted, so editing a test needs no rebuild. Appending
pytest args to the underlying `docker compose ... run --rm test` replaces the image's CMD but not
its ENTRYPOINT, so the database is still recreated first.

## Running locally without Docker

Tests, no (above). For a bare uvicorn against a Postgres you supply yourself:

```
uv sync
DATABASE_URL=postgresql+asyncpg://... uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://... uv run uvicorn monet_api.main:app --reload
```

The compose stack publishes no Postgres host port, so that `DATABASE_URL` cannot be the dev
stack's database.

## Gotchas

- The async engine/session is created once at import time (`core/db.py`). Tests therefore need a
  **session-scoped** event loop, not pytest-asyncio's per-test default — asyncpg connections are
  bound to the loop that opened them, and a per-test loop breaks the shared connection pool on the
  second test. See `pyproject.toml`'s `asyncio_default_fixture_loop_scope` /
  `asyncio_default_test_loop_scope`.
- `mypy --strict`'s `disallow_any_explicit` is **not** enabled here — it false-positives against
  SQLModel/Pydantic's own plugin-generated code on essentially every model field, not against
  anything we actually write.
- `objects/service.py`'s `normalize_latex` decides object identity, and is what gets **stored**:
  `pylatexenc` parses, then whitespace outside `\text{...}` is dropped and collapsed inside it —
  except the space terminating a control word, without which `K_{1} \sqcup K_{1}` becomes
  `\sqcupK` and stops rendering. So `x^{2} - 4 x + 3` and `x^{2}-4x+3` are one object, while
  `\text{Is Singular}` stays distinct from `\text{IsSingular}`. `objects.latex` is unique, so a
  second spelling is a conflict rather than a twin. This is spelling, not the canonical form
  (equivalent ways of writing the same matrix) that root `AGENTS.md` still defers.
- Deleting an object deletes its edges. Foreign keys do nearly all of it: `ON DELETE CASCADE`
  carries away its contents-page entry, its implementation, its references, the relations it
  operates, and those relations' slots. The one case a foreign key cannot express is an object used as a relation's
  input or output — cascading `relation_input.object_id` would delete the slot and leave the
  relation with a hole — so `delete_object` issues one statement for that, and those two foreign
  keys stay blocking as a backstop.
