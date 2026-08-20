#!/bin/sh
set -e
case "$DATABASE_URL" in
  */monet_test)
    uv run python -m tests.reset_test_db
    uv run alembic upgrade head
    uv run alembic check
    ;;
  *)
    echo "docker-entry.sh: DATABASE_URL is not monet_test — skipping recreate + migrate." \
      "Not touching this database. (Dev DB schema out of date? Run 'just migrate'.)" >&2
    ;;
esac
exec "$@"
