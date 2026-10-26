#!/bin/sh
set -e
uv run alembic upgrade head
if [ "$RESEED_ON_DEPLOY" = "true" ]; then
    uv run python scripts/seed.py
else
    uv run python scripts/seed.py --if-empty
fi
