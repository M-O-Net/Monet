# Monet — engineering conventions

Read `README.md` first for what Monet is and why the data model is shaped the way it is. This
file is doctrine: conventions that hold across the whole repo. Each app carries its own AGENTS.md
for what's local to it — `apps/api/AGENTS.md` today; `apps/web/AGENTS.md` if/when the frontend
grows enough local convention to warrant one.

Conventions here are adapted from `~/Developer/Muse`, a sibling project, stripped of everything
specific to Muse being a physical-robot product (no shared-package relock workflow, no
multi-tenancy/RLS, no Redis/Celery, no device app). Where a convention is reused near-verbatim,
that's noted so the reasoning doesn't need re-deriving.

## v0 schema

Deliberately bare — four tables, no bookkeeping columns:

```
objects(id uuid pk, latex text)
relations(id uuid pk, operator_id uuid fk -> objects)
relation_input(id uuid pk, relation_id uuid fk -> relations, object_id uuid fk -> objects, position int)
relation_output(id uuid pk, relation_id uuid fk -> relations, object_id uuid fk -> objects, position int)
```

- `objects` has no type/kind tag, no label, no canonical hash, no timestamps. An object's `latex`
  field is both its storage and its display form — nothing about it is machine-structured in v0.
- An object is an "operator" purely by being referenced as some relation's `operator_id` — no
  separate flag, no separate table.
- `position` on the junction tables is the one structural (not bookkeeping) field: it preserves
  operand order for non-commutative operators and distinguishes outputs when a relation produces
  more than one (e.g. quotient vs. remainder).
- **Explicitly out of v0**, deferred to later passes — do not re-add without deciding to: any
  `kind`/type tag, label, canonical hash, timestamps, or soft-delete/versioning on `objects` or
  `relations`; verification badges; agent/method/corroboration columns; an evidence table;
  TTL/budget economy; multi-language operator implementations; any code actually running behind
  an operator.

## Stack

- **Backend** (`apps/api`): FastAPI, SQLModel (async, `asyncpg`), Alembic migrations, `uv`
  packaging.
- **Frontend** (`apps/web`): React + Vite + TanStack Query + TanStack Router (file-based routing),
  Tailwind v4, Base UI for interactive primitives (select, etc.) rather than hand-rolled ones.
- **Type boundary**: FastAPI generates `openapi.json` → `openapi-typescript` generates
  `apps/web/src/client/schema.d.ts` (committed, so CI/local dev works without a live API) →
  `packages/api-client` wraps it into typed React Query hooks. No hand-written duplicate types.

### Pydantic / schema conventions (from Muse, near-verbatim)

- One shared `ORMModel(BaseModel)` base in `apps/api/src/monet_api/core/schemas.py`, setting only
  `ConfigDict(from_attributes=True)`. No global `strict=True`, no `extra="forbid"`.
- Each endpoint gets its own flat, hand-written I/O schema inheriting `ORMModel` — kept separate
  from the SQLModel table class. No generic `Create`/`Update`/`Read` base; not needed at this size.
- No casing alias-generator. The API serves snake_case JSON; the frontend consumes snake_case
  as-is.
- No enums in v0's schema (objects carry no `kind` tag), so no `StrEnum`-to-TS-union concern yet.
- IDs are UUID everywhere (`uuid4` default, `sa.UUID` column), never surrogate int/str keys.
- Errors stay ad hoc: FastAPI's default `{"detail": "..."}` shape, plus one catch-all
  `@app.exception_handler(Exception)`. No shared `ErrorResponse` schema at this scale.
- Every route declares explicit `response_model=` **and** explicit `operation_id="snake_case_name"`
  — the latter is what keeps generated TS hook names stable/readable instead of FastAPI's
  auto-generated ids.

### Backend domain modules (from Muse, applied even to a single domain)

Every domain — `apps/api/src/monet_api/objects/` today, whatever's added later — splits
`router.py` → `service.py` → `repository.py`: routers are HTTP only (path/status/response
schema, no SQL); a service owns business logic (404/400 translation, assembling a response out of
several repository calls) and no SQL of its own; a repository is the only file that runs
`select`/`session.exec`. Muse enforces the boundary mechanically with `.importlinter`, which
polices _cross_-domain reach — Monet skips that tool since v0 has one domain and nothing to police
between domains, but the file-layer split itself isn't conditional on having the tool; Muse
applies it even to its own single-concern modules, and so does Monet.

### Frontend consumption (from Muse, near-verbatim)

`packages/api-client` is a **generic factory**, not one hand-written hook per endpoint:
`createApiClient<Paths>(basePath)` returns typed `useSuspenseApiQuery`/`useApiMutation` hooks
bound against the generated `paths` type. Monet's version drops Muse's WebSocket/realtime
machinery (device-specific) and its auth-token plumbing (Monet v0 has no auth). No zod or other
runtime validation layer on top — generated types are trusted as-is.

A file under `apps/web/src/routes/` stays a thin route: wire up `Route` and a page component that
lays the page out, nothing else. A piece of UI reused by more than the one route it was written
for goes in `apps/web/src/components/`; a component that exists only to help one route render
(and would never be imported from a second route) goes in a `-components/` folder next to that
route instead — TanStack Router's generator ignores anything under a `-`-prefixed path, so it
never becomes a route of its own.

### Linting & type strictness (from Muse, as-is)

- Python: `ruff` (curated rule set) + `mypy --strict` (`pydantic.mypy` plugin — note:
  `disallow_any_explicit` was tried and dropped, it false-positives against SQLModel/Pydantic's
  own generated code, not real issues in our code), config in native files (`ruff.toml`,
  `mypy.ini` — **not** `pyproject.toml`, see caching note below), `pytest` for tests.
- TypeScript: `eslint` flat config with `typescript-eslint`'s `strictTypeChecked` +
  `stylisticTypeChecked`, `eslint-plugin-react-hooks`, `prettier`, `vitest` +
  `@testing-library/react` + `msw` for tests.
- Skip Muse's `.importlinter` import-boundary enforcement — it polices boundaries between
  multiple internal domains, and Monet v0 has effectively one (see "Backend domain modules"
  above for the part of that convention Monet keeps anyway).

### Monorepo

pnpm workspace + a `Justfile` as the single command surface across Python and JS (`just up`,
`just migrate`, `just migrate-new`, `just test`, `just lint`, `just gen-client`,
`just wt-add`/`just wt-rm`, `just check`, `just land`). Keep Muse's Docker-worktree workflow —
`just wt-add <name>` gives a git worktree its own isolated compose stack (ports/network/volumes)
so multiple agents can work in parallel without colliding. Drop Muse's Redis/Celery, RLS/tenancy,
and multi-app split.

## Build/CI caching (from Muse's core pattern, minus what's 4-app-specific)

- Dockerfiles: a `deps` stage copies only lockfiles and runs
  `uv sync --frozen --no-install-project` / `pnpm install --frozen-lockfile` _before_ any source
  is copied, so the expensive layer is keyed purely on dependencies. `RUN --mount=type=cache` for
  the uv/pnpm package caches.
- CI's `changes` job (`dorny/paths-filter`) gates backend/frontend jobs independently. Frontend
  Docker build uses `cache-from/to: type=gha`; the **backend must use the manual
  build+`docker save`+`actions/cache` tarball technique instead** — BuildKit's GHA cache backend
  doesn't export `--mount=type=cache` contents, so `type=gha` would silently fail to cache the uv
  layer.
- Keep lint/type-checker config in native files, not `pyproject.toml` — Muse hit a real bug where
  a pure lint-config edit busted the whole dependency cache key because it lived in a file the
  Dockerfile's `deps` stage copies.
- **Deferred, don't build yet**: `cache-seed-*.yml` proactive cache-warming workflows and the
  composite actions that keep a cache-key string identical across files — both exist in Muse only
  because it has 4 apps sharing cache namespaces. Muse's own comments frame cache-seeding as an
  optimization, not a correctness requirement (CI self-heals on a miss); not worth it yet at
  Monet's scale. No relock-on-dependabot-PR workflow either — Monet has no shared Python package.

## Merge gate (from Muse, near-verbatim, simplified to a 2-area `want()`: `api`, `web`)

The mechanism that matters most once several agents work in parallel worktrees — no path, human
or agent, reaches `main` unverified:

- `.githooks/pre-commit` — fast, area-aware lint/lockfile check per commit, parallelized, defaults
  to running everything when it can't tell what's affected. Also runnable via `just check`.
- `.githooks/pre-push` — blocks pushing directly to an already-"ready" (non-draft) PR; drafts push
  freely. Forces every PR through `just land` to actually merge.
- `.githooks/land` (`just land`) — refuses a dirty tree or a local HEAD that doesn't match what
  was pushed, runs the full local suite concurrently per affected area, flips the PR ready, waits
  for CI, merges on green or flips back to draft on red.
- `.claude/hooks/require-draft-pr.py` — blocks an agent from running `gh pr ready`/`gh pr merge`
  directly, closing the one loophole `land` can't close on its own.
- `.claude/hooks/block-main-branch.py` — blocks edits, commits, and mutating shell commands
  targeting the main checkout itself. Feature work happens in a `just wt-add` worktree, always —
  this is what makes that a mechanical guarantee rather than a habit.

## GUI pages (v0)

Object list (rendered LaTeX per row), object detail page (its LaTeX + relations it participates
in, grouped as input/output, each showing the operator and the other objects involved),
add/edit-object form (a LaTeX field), add/edit-relation form (pick operator, pick ordered input
objects, pick ordered output objects — the operator picker is just an object picker, since
operators aren't a distinct type).

## Local dev

Full Docker: `docker-compose.yml` (api + web + postgres) plus `docker-compose.dev.yml` (bind
mounts, hot reload). `just wt-add <name>` creates a git worktree with its own isolated stack.
The same Dockerfiles are what Render builds from at deploy time.

`just up`'s api container always runs migrations, then seeds **only if the objects table is
empty** (`scripts/seed.py --if-empty`) — so a brand-new worktree/dev env always has the demo
dataset on its first run, without silently wiping anything added by hand through the GUI on
every later restart. Run `just seed` directly to force a hard reset back to the canonical
dataset; the dataset itself is documented where it's defined, in `scripts/seed.py`, not here.

## Deployment

Single Render account/dashboard for everything: a Render web service (API), a Render static site
(the Vite build), and a **paid** Render Postgres instance (Basic-256MB, $6/month — Render's free
Postgres expires and gets deleted, so the DB tier is the one piece that can't stay free). API tier
(free-with-cold-start vs. $7/month always-on Starter) is a deploy-time dashboard choice. A
`render.yaml` blueprint defines all three services together. Alembic migrations run as a
pre-deploy/release step on Render, not manually.
