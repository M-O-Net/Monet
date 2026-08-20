#!/bin/sh
set -e
uv run alembic upgrade head
uv run python scripts/seed.py --if-empty
exec uv run uvicorn monet_api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
