from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import delete

from monet_api.core.db import async_session
from monet_api.main import app
from monet_api.objects.models import (
    Object,
    OperatorDisplay,
    Relation,
    RelationInput,
    RelationOutput,
    TopLevelObject,
)


@pytest_asyncio.fixture(autouse=True)
async def _clean_db() -> AsyncGenerator[None]:
    async with async_session() as session:
        await session.exec(delete(OperatorDisplay))  # type: ignore[call-overload]
        await session.exec(delete(TopLevelObject))  # type: ignore[call-overload]
        await session.exec(delete(RelationOutput))  # type: ignore[call-overload]
        await session.exec(delete(RelationInput))  # type: ignore[call-overload]
        await session.exec(delete(Relation))  # type: ignore[call-overload]
        await session.exec(delete(Object))  # type: ignore[call-overload]
        await session.commit()
    yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
