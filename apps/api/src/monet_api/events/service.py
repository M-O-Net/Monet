import uuid

from fastapi import HTTPException
from pydantic import TypeAdapter
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments import repository as comments
from monet_api.comments.schemas import CommentOut
from monet_api.events import repository
from monet_api.events.schemas import EventKind, EventOut
from monet_api.objects import repository as objects
from monet_api.objects import service as objects_service

_KIND: TypeAdapter[EventKind] = TypeAdapter(EventKind)


async def list_events(
    session: AsyncSession,
    contributor: str | None,
    kind: EventKind | None,
    before: uuid.UUID | None,
    limit: int,
) -> list[EventOut]:
    anchor = None if before is None else await repository.get_event(session, before)
    if before is not None and anchor is None:
        raise HTTPException(status_code=404, detail="event not found")
    events = await repository.list_events(session, contributor, kind, anchor, limit)
    subjects = [event.subject_id for event in events]

    found_comments = {
        comment.id: CommentOut.model_validate(comment)
        for comment in await comments.list_comments_by_ids(session, subjects)
    }
    commented = [comment.object_id for comment in found_comments.values()]
    found_objects = {
        obj.id: obj
        for obj in await objects_service.objects_out(
            session, await objects.list_objects_by_ids(session, [*subjects, *commented])
        )
    }
    found_relations = {
        relation.id: relation
        for relation in await objects_service.load_relations(
            session, await objects.list_relations_by_ids(session, subjects)
        )
    }

    feed: list[EventOut] = []
    for event in events:
        comment = found_comments.get(event.subject_id)
        about = event.subject_id if comment is None else comment.object_id
        entry = EventOut(
            id=event.id,
            at=event.at,
            kind=_KIND.validate_python(event.kind),
            contributor=event.contributor,
            source=event.source,
            object=found_objects.get(about),
            relation=found_relations.get(event.subject_id),
            comment=comment,
        )
        if entry.object or entry.relation:
            feed.append(entry)
    return feed
