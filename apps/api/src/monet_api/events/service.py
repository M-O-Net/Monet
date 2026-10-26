from pydantic import TypeAdapter
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments import repository as comments
from monet_api.comments.schemas import CommentOut
from monet_api.events import repository
from monet_api.events.schemas import EventKind, EventOut
from monet_api.objects import repository as objects
from monet_api.objects import service as objects_service
from monet_api.objects.schemas import ObjectOut

_KIND: TypeAdapter[EventKind] = TypeAdapter(EventKind)


async def list_events(
    session: AsyncSession, contributor: str | None, kind: EventKind | None, limit: int
) -> list[EventOut]:
    events = await repository.list_events(session, contributor, kind, limit)
    subjects = [event.subject_id for event in events]

    found_comments = {
        comment.id: CommentOut.model_validate(comment)
        for comment in await comments.list_comments_by_ids(session, subjects)
    }
    commented = [comment.object_id for comment in found_comments.values()]
    found_objects = {
        obj.id: ObjectOut.model_validate(obj)
        for obj in await objects.list_objects_by_ids(session, [*subjects, *commented])
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
