from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.events import service
from monet_api.events.schemas import EventOut

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/events", response_model=list[EventOut], operation_id="list_events")
async def list_events(
    session: DbSession,
    contributor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[EventOut]:
    return await service.list_events(session, contributor, limit)
