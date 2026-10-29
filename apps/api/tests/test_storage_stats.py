import datetime

import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.stats import repository, service


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service, "_cached", None)


async def test_categories_add_up_to_the_whole_database(client: AsyncClient) -> None:
    stats = (await client.get("/stats/storage")).json()

    assert stats["database_bytes"] > 0
    assert sum(c["size_bytes"] for c in stats["categories"]) == stats["database_bytes"]
    assert all(c["size_bytes"] > 0 for c in stats["categories"])


async def test_every_table_lands_in_exactly_one_category(client: AsyncClient) -> None:
    stats = (await client.get("/stats/storage")).json()
    named = [
        table
        for c in stats["categories"]
        if c["category"] not in {"other", "overhead"}
        for table in c["tables"]
    ]
    rest = {c["category"]: c["tables"] for c in stats["categories"]}

    assert sorted(named) == sorted(SQLModel.metadata.tables)
    assert rest["other"] == ["alembic_version"]
    assert rest["overhead"] == []


async def test_storage_is_measured_at_most_once_a_minute(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    measured = 0
    list_table_sizes = repository.list_table_sizes

    async def counting(session: AsyncSession) -> list[repository.TableSize]:
        nonlocal measured
        measured += 1
        return await list_table_sizes(session)

    monkeypatch.setattr(repository, "list_table_sizes", counting)

    first = (await client.get("/stats/storage")).json()
    second = (await client.get("/stats/storage")).json()
    assert measured == 1
    assert second["measured_at"] == first["measured_at"]

    monkeypatch.setattr(service, "FRESH_FOR", datetime.timedelta(0))
    await client.get("/stats/storage")
    assert measured == 2
