# Monet — engineering conventions

Read `README.md` first for what Monet is and why the data model is shaped the way it is. This
file is doctrine: conventions that hold across the whole repo. Each app carries its own AGENTS.md
for what's local to it — `apps/api/AGENTS.md` today; `apps/web/AGENTS.md` if/when the frontend
grows enough local convention to warrant one.

Conventions here are adapted from `~/Developer/Muse`, a sibling project, stripped of everything
specific to Muse being a physical-robot product (no shared-package relock workflow, no
multi-tenancy/RLS, no Redis/Celery, no device app). Where a convention is reused near-verbatim,
that's noted so the reasoning doesn't need re-deriving.

## Writing code

**Keep these docs current, never longer.** A change that makes an AGENTS.md false corrects it in
the same change — that is a fix, not an addition. New guidance IS an addition: propose it at the
end of your work and let Ofek decide. These files shrink, not grow.

**Write no new comments, docstrings, or AGENTS.md text.** Default to zero. The urge to comment
usually means the code should change instead: an explaining variable, an extracted method, a
better name (`width_in_pixels`), an assertion (`check_argument(height > 0)`). If a line genuinely
cannot carry itself without one, write it — then list every such addition at the end of your work,
one by one, for Ofek to approve or cut. Never slip one in silently.

**When you must touch text that already exists, shrink it.** A comment states its reason at the
smallest scope that owns it — naming another module, table, route, or issue number goes stale
_silently_ — and describes the code as it is now, not its history. A docstring is a one-line
imperative summary ending in a period ("Return the pathname.", never "Returns…"), a blank line,
then `Args:`/`Returns:`/`Raises:` only if earned. Ruff's `D205`/`D401`/`D415` hold the shape;
`D1*` is off because most functions need none. A failing docstring is badly written, not badly
formatted — delete it, or cut it back to its summary; a blank line to satisfy the linter changes
nothing. Never longer coming out of an edit than going in, and never break a backticked span
across a line wrap.

**Finish the work. Don't write it down as something to do later, anywhere.**

1. No TODO or work-tracking comments in code.
2. Do NOT open GitHub issues — fix it now, or tell the user and stop. Ofek opens issues; agents
   close them.
3. Never report something done, ready, or landed while a gap remains. "Done, except…" is not done.

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
- Deleting an object deletes its edges: every relation it appears in, plus its contents-page
  entry and its implementation. See `apps/api/AGENTS.md` for why the relation half of that can't
  be a foreign key.
- `position` on the junction tables is the one structural (not bookkeeping) field: it preserves
  operand order for non-commutative operators and distinguishes outputs when a relation produces
  more than one (e.g. quotient vs. remainder).
- **Explicitly out of v0**, deferred to later passes — do not re-add without deciding to: any
  `kind`/type tag, label, canonical hash, timestamps, or soft-delete/versioning on `objects` or
  `relations`; verification badges; agent/method/corroboration columns; an evidence table;
  TTL/budget economy; multi-language operator implementations.

### implementations (added after v0)

The one deliberate departure from the list above: code _does_ now run behind an operator. It is
sympy, written and edited through the GUI rather than living in this repo, and — the load-bearing
part — **it never executes on the server**. `apps/api` stores and serves it as opaque text and has
no sympy dependency; execution happens in the visitor's browser. See "Implementations" below.

An implementation carries nothing but its operator and its code: no name (the operator names it),
no arity (`def compute(*inputs)` answers "how many?" with "any", and arity belongs to neither the
operator nor the object), and no timestamps, author or versioning, same as the rest of v0.

## Stack

- **Backend** (`apps/api`): FastAPI, SQLModel (async, `asyncpg`), Alembic migrations, `uv`
  packaging.
- **Frontend** (`apps/web`): React + Vite + TanStack Query + TanStack Router (file-based routing),
  Tailwind v4, Base UI for interactive primitives (select, etc.) rather than hand-rolled ones.
  TypeScript stays on 6.x via the `npm:@typescript/typescript6` alias — TS 7.0 ships no compiler
  API, which typescript-eslint needs — so the binary is `tsc6`, not `tsc`.
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
`createApiClient<Paths>(basePath)` returns `openapi-react-query`'s client bound against the
generated `paths` type — call sites use `api.useQuery(method, path, init?)` and
`api.useMutation(method, path)`. The app uses no Suspense and no error boundaries — branch on
`isPending`/`isError` the way every existing route does. Monet's version drops Muse's
WebSocket/realtime machinery (device-specific) and its auth-token plumbing (Monet v0 has no auth).
No zod or other runtime validation layer on top — generated types are trusted as-is.

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
  `stylisticTypeChecked`, `eslint-plugin-react-hooks`, `prettier`, `vitest` for tests.
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
  the uv/pnpm package caches. `apps/api/Dockerfile` adds a `test-deps` stage on the same
  principle, and both take a `DEPS_IMAGE`/`TEST_DEPS_IMAGE` build arg so CI can substitute a
  cache-restored image. **`final` must stay the last stage there** — `render.yaml` builds it by
  path and cannot name a target.
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

## Implementations

Anyone can write Python against an operator and have it run — which means running code authored by
a stranger, since Monet has no auth. Two decisions follow from that, and neither should be softened
without re-deciding both:

**Execution is client-side, always.** Pyodide (CPython compiled to WebAssembly) runs inside
`<iframe sandbox="allow-scripts">` in `apps/web/src/sandbox/`, deliberately **without**
`allow-same-origin`. That gives the frame an opaque origin: no access to the app's `localStorage`
or DOM, and every request to the API is cross-origin, so the `CORS_ORIGINS` allowlist keeps it
from reading any response. The server therefore needs no sandbox, no subprocess, and no sympy.
Language-level sandboxes (RestrictedPython, `safe_eval`) were rejected outright — they leak, and
sympy is full of `eval` anyway.

That boundary is about confidentiality, not integrity. Implementation code runs with unrestricted
builtins, so `import js` reaches `parent.postMessage`, and `probe()` evaluates every
implementation's `accepts` in one interpreter — one hostile implementation can therefore forge
another's result, which the visitor is then invited to add to the network. Closing that needs a
Worker per implementation, which an opaque origin cannot have (below). Nothing it forges is more
than the visitor could assert by hand.

Consequences worth knowing before touching this code:

- **Pyodide runs on the frame's own thread, not in a Worker.** An opaque origin cannot load a
  worker script at all: Chrome refuses to construct a module worker from one, and `importScripts`
  on a `blob:null` worker is blocked regardless of CORS. The time limit a Worker's `terminate()`
  would have given is enforced from inside Python instead, by the trace-function deadline guard in
  `sandbox/runner.py`. Everything a deadline must cover — loading the code, parsing, computing —
  has to be called _inside_ `_with_line_deadline`, never evaluated as an argument to it. It cannot
  stop a single long call inside sympy's own internals.
- **Every asset the frame loads needs `Access-Control-Allow-Origin`**, including its own bundled
  module script — opaque-origin subresource loads are cross-origin, and `type="module"` scripts are
  always CORS-checked. Set in three places that must stay in step: `apps/web/vite.config.ts` (dev),
  `apps/web/nginx.conf` (Docker), `render.yaml` (deploy); `scripts/fetch-pyodide.mjs` asserts all
  three. Omitting one fails only in that environment, and fails silently. `nginx.conf` also has to
  name `.mjs` as JavaScript — nginx's bundled `mime.types` doesn't, and a browser won't execute a
  module served as `application/octet-stream` (unverified on Render's static host).
- **`render()` in `sandbox/prelude.py` is the single source of truth for Monet's LaTeX.**
  `scripts/seed.py` is aligned to what it emits, so running an implementation over the seeded
  dataset lands on the objects already there instead of minting near-duplicates.
- Objects still carry no type tag, so **an implementation declares its own domain** via
  `accepts(x) -> bool`, evaluated in the sandbox. That is what decides which buttons an object
  page shows.
- **Implementations deal in sympy, not strings.** `runner.py` parses each input's LaTeX before
  calling `accepts`/`compute` and renders what `compute` returns; `parse`/`render` stay in scope
  for one that needs them.
- **An implementation is edited on its operator's own object page**, not in an index of its own —
  operators are objects, so a separate list would be a second taxonomy.

**The server trusts arithmetic it did not perform.** `POST /relations/assert` records whatever the
browser computed. This is no weaker than `POST /relations`, which already lets anyone assert
anything by hand — but it does mean a client-computed result can never honestly carry a "verified
by exact computation" badge when that lands. Implementations are plain text against a fixed contract,
so a server-side runner can be added later as a second execution site with no data-model change.

## GUI pages

Object list (rendered LaTeX per row), object detail page (its LaTeX + relations it participates
in, grouped as input/output, each showing the operator and the other objects involved),
add/edit-object form (a LaTeX field), add/edit-relation form (pick operator, pick ordered input
objects, pick ordered output objects — the operator picker is just an object picker, since
operators aren't a distinct type).

Plus, from the implementations pass: an **Operations** section on the object detail page (a button per
implementation that accepts this object; running one previews the result and whether it already exists
before anything is written), an implementation list, and an implementation editor with a scratch panel that
runs the unsaved code against a sample input.

## Local dev

Full Docker: `docker-compose.yml` (api + web + postgres) plus `docker-compose.dev.yml` (bind
mounts, hot reload). `just wt-add <name>` creates a git worktree with its own isolated stack.
The same Dockerfiles are what Render builds from at deploy time. No service publishes a Postgres
host port — nothing outside the compose network needs one.

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
