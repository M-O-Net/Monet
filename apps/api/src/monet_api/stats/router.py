from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.stats import service
from monet_api.stats.schemas import StorageStatsOut

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/stats/storage", response_model=StorageStatsOut, operation_id="get_storage_stats")
async def get_storage_stats(session: DbSession) -> StorageStatsOut:
    return await service.get_storage_stats(session)
