import uuid
from collections.abc import Sequence

from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.events.models import Event


def add_event(
    session: AsyncSession,
    kind: str,
    subject_id: uuid.UUID,
    contributor: str | None,
    source: str | None,
) -> None:
    session.add(Event(kind=kind, subject_id=subject_id, contributor=contributor, source=source))


async def list_events(session: AsyncSession, contributor: str | None, limit: int) -> list[Event]:
    query = select(Event)
    if contributor is not None:
        query = query.where(Event.contributor == contributor)
    return list((await session.exec(query.order_by(col(Event.at).desc()).limit(limit))).all())


async def list_events_for(
    session: AsyncSession, kind: str, subject_ids: Sequence[uuid.UUID]
) -> list[Event]:
    if not subject_ids:
        return []
    return list(
        (
            await session.exec(
                select(Event)
                .where(Event.kind == kind)
                .where(col(Event.subject_id).in_(subject_ids))
            )
        ).all()
    )


async def delete_events_for(session: AsyncSession, subject_ids: Sequence[uuid.UUID]) -> None:
    if subject_ids:
        await session.exec(delete(Event).where(col(Event.subject_id).in_(subject_ids)))
