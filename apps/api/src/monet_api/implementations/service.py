"""Business logic for the implementations domain: 404/400 translation and schema assembly.

Orchestrates repository.py calls; owns no SQL of its own. Note that nothing here executes an
implementation's `code` — it is stored and served as opaque text, and only ever runs in the
visitor's browser sandbox.
"""

import uuid

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.implementations import repository
from monet_api.implementations.models import Implementation
from monet_api.implementations.schemas import ImplementationDetailOut, ImplementationWrite
from monet_api.objects import service as objects_service
from monet_api.objects.schemas import ObjectOut


async def get_implementation_or_404(
    session: AsyncSession, implementation_id: uuid.UUID
) -> Implementation:
    implementation = await repository.get_implementation(session, implementation_id)
    if implementation is None:
        raise HTTPException(status_code=404, detail="implementation not found")
    return implementation


async def _load_detail(
    session: AsyncSession, implementation: Implementation
) -> ImplementationDetailOut:
    operator = await objects_service.get_object_or_404(session, implementation.operator_id)
    return ImplementationDetailOut(
        id=implementation.id,
        operator=ObjectOut.model_validate(operator),
        code=implementation.code,
    )


async def list_implementations(session: AsyncSession) -> list[ImplementationDetailOut]:
    implementations = await repository.list_implementations(session)
    return [await _load_detail(session, i) for i in implementations]


async def get_implementation(
    session: AsyncSession, implementation_id: uuid.UUID
) -> ImplementationDetailOut:
    implementation = await get_implementation_or_404(session, implementation_id)
    return await _load_detail(session, implementation)


async def create_implementation(
    session: AsyncSession, body: ImplementationWrite
) -> ImplementationDetailOut:
    await objects_service.get_object_or_404(session, body.operator_id)
    implementation = await repository.create_implementation(
        session, body.operator_id, body.code
    )
    return await _load_detail(session, implementation)


async def update_implementation(
    session: AsyncSession, implementation_id: uuid.UUID, body: ImplementationWrite
) -> ImplementationDetailOut:
    implementation = await get_implementation_or_404(session, implementation_id)
    await objects_service.get_object_or_404(session, body.operator_id)
    updated = await repository.update_implementation(
        session, implementation, body.operator_id, body.code
    )
    return await _load_detail(session, updated)


async def delete_implementation(session: AsyncSession, implementation_id: uuid.UUID) -> None:
    implementation = await get_implementation_or_404(session, implementation_id)
    await repository.delete_implementation(session, implementation)
