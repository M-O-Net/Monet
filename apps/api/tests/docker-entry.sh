#!/bin/sh
# ENTRYPOINT of the `test` compose service (see apps/api/Dockerfile's `test` stage and
# docker-compose.dev.yml's `test` service): recreate + migrate the dedicated monet_test database,
# then exec whatever command was given (pytest, by default).
#
# The `case` is a safety guard, not a convenience: everything below this line is destructive
# (DROP DATABASE, then `alembic upgrade head` against whatever it just created). If DATABASE_URL
# ever points somewhere other than a database literally named `monet_test` — a mistyped compose
# override, someone reusing this image to run the suite against the dev stack — we skip the whole
# block and run the command as-is rather than migrating or wiping a database that isn't ours.
# reset_test_db.py repeats the same check independently, so neither one is the only thing standing
# between a typo and the dev data.
set -e
case "$DATABASE_URL" in
  */monet_test)
    # The test DB is a per-run artifact, rebuilt from empty every time. That's what makes
    # `upgrade head` below run this branch's own migration chain end to end, instead of meeting a
    # half-applied state or an alembic stamp left behind by whichever branch ran here last.
    uv run python -m tests.reset_test_db
    uv run alembic upgrade head
    # Model↔migration drift gate: fails the run (and therefore CI) when a SQLModel table
    # describes a column/constraint/index differently than the migrations that actually built it.
    # Running it here means a new model without a migration can never pass tests — which used to
    # be possible, since host-side pytest ran against whatever schema the dev DB happened to have.
    # `just migrate-check` is the same check pointed at the dev DB.
    uv run alembic check
    ;;
  *)
    echo "docker-entry.sh: DATABASE_URL is not monet_test — skipping recreate + migrate." \
      "Not touching this database. (Dev DB schema out of date? Run 'just migrate'.)" >&2
    ;;
esac
exec "$@"
