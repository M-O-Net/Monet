import inspect

import asyncpg
import pytest
from sqlalchemy.dialects import registry
from sqlalchemy.engine.url import make_url

from monet_api.core.config import as_asyncpg_url

RENDER = "postgresql://u:p@dpg-abc.oregon-postgres.render.com:5432/monet"
NEON = "postgresql://u:p@ep-x.aws.neon.tech/monet?sslmode=require&channel_binding=require"


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        (RENDER, "postgresql+asyncpg://u:p@dpg-abc.oregon-postgres.render.com:5432/monet"),
        (NEON, "postgresql+asyncpg://u:p@ep-x.aws.neon.tech/monet?ssl=require"),
        ("postgres://u:p@host/monet", "postgresql+asyncpg://u:p@host/monet"),
        ("postgresql+asyncpg://u:p@host/monet", "postgresql+asyncpg://u:p@host/monet"),
    ],
)
def test_managed_postgres_urls_reach_asyncpg(given: str, expected: str) -> None:
    assert as_asyncpg_url(given) == expected


def test_every_argument_asyncpg_is_given_is_one_it_accepts() -> None:
    dialect = registry.load("postgresql.asyncpg")()
    _, kwargs = dialect.create_connect_args(make_url(as_asyncpg_url(NEON)))
    accepted = set(inspect.signature(asyncpg.connect).parameters)
    assert not set(kwargs) - accepted
