from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import delete

from monet_api.comments.models import Comment
from monet_api.core.config import settings
from monet_api.core.db import async_session
from monet_api.editors.models import Change, Editor
from monet_api.events.models import Event
from monet_api.implementations.models import Implementation
from monet_api.main import app
from monet_api.objects.models import (
    Object,
    OperatorDisplay,
    Relation,
    RelationInput,
    RelationOutput,
    TopLevelObject,
)
from monet_api.suggestions.models import Suggestion

OWNER_KEY = "owner-key-for-tests"
settings.admin_key = OWNER_KEY


@pytest_asyncio.fixture(autouse=True)
async def _clean_db() -> AsyncGenerator[None]:
    async with async_session() as session:
        await session.exec(delete(Suggestion))  # type: ignore[call-overload]
        await session.exec(delete(Change))  # type: ignore[call-overload]
        await session.exec(delete(Editor))  # type: ignore[call-overload]
        await session.exec(delete(Event))  # type: ignore[call-overload]
        await session.exec(delete(Comment))  # type: ignore[call-overload]
        await session.exec(delete(Implementation))  # type: ignore[call-overload]
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
    headers = {"X-Editor-Key": OWNER_KEY}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac


async def editor_key(client: AsyncClient, name: str, level: int) -> dict[str, str]:
    email = f"{name.lower()}@example.org"
    resp = await client.post("/editors", json={"name": name, "email": email, "level": level})
    assert resp.status_code == 201, resp.text
    return {"X-Editor-Key": resp.json()["key"]}
