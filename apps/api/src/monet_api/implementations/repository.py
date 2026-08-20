"""Raw SQLModel queries for the implementations domain.

No business logic, no 404s — see service.py.
"""

import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.implementations.models import Implementation


async def get_implementation(
    session: AsyncSession, implementation_id: uuid.UUID
) -> Implementation | None:
    return await session.get(Implementation, implementation_id)


async def list_implementations(session: AsyncSession) -> list[Implementation]:
    return list((await session.exec(select(Implementation))).all())


async def create_implementation(
    session: AsyncSession, operator_id: uuid.UUID, code: str
) -> Implementation:
    implementation = Implementation(operator_id=operator_id, code=code)
    session.add(implementation)
    await session.commit()
    await session.refresh(implementation)
    return implementation


async def update_implementation(
    session: AsyncSession, implementation: Implementation, operator_id: uuid.UUID, code: str
) -> Implementation:
    implementation.operator_id = operator_id
    implementation.code = code
    session.add(implementation)
    await session.commit()
    await session.refresh(implementation)
    return implementation


async def delete_implementation(session: AsyncSession, implementation: Implementation) -> None:
    await session.delete(implementation)
    await session.commit()
