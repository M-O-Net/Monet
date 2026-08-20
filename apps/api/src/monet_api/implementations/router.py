import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.implementations import service
from monet_api.implementations.schemas import ImplementationDetailOut, ImplementationWrite

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    "/implementations",
    response_model=list[ImplementationDetailOut],
    operation_id="list_implementations",
)
async def list_implementations(session: DbSession) -> list[ImplementationDetailOut]:
    return await service.list_implementations(session)


@router.post(
    "/implementations",
    response_model=ImplementationDetailOut,
    operation_id="create_implementation",
    status_code=201,
)
async def create_implementation(
    body: ImplementationWrite, session: DbSession
) -> ImplementationDetailOut:
    return await service.create_implementation(session, body)


@router.get(
    "/implementations/{implementation_id}",
    response_model=ImplementationDetailOut,
    operation_id="get_implementation",
)
async def get_implementation(
    implementation_id: uuid.UUID, session: DbSession
) -> ImplementationDetailOut:
    return await service.get_implementation(session, implementation_id)


@router.patch(
    "/implementations/{implementation_id}",
    response_model=ImplementationDetailOut,
    operation_id="update_implementation",
)
async def update_implementation(
    implementation_id: uuid.UUID, body: ImplementationWrite, session: DbSession
) -> ImplementationDetailOut:
    return await service.update_implementation(session, implementation_id, body)


@router.delete(
    "/implementations/{implementation_id}",
    operation_id="delete_implementation",
    status_code=204,
)
async def delete_implementation(implementation_id: uuid.UUID, session: DbSession) -> None:
    await service.delete_implementation(session, implementation_id)
