from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments import repository as comments
from monet_api.comments.schemas import CommentOut
from monet_api.events import repository
from monet_api.events.schemas import EventOut
from monet_api.objects import repository as objects
from monet_api.objects import service as objects_service
from monet_api.objects.schemas import ObjectOut


async def list_events(session: AsyncSession, contributor: str | None, limit: int) -> list[EventOut]:
    events = await repository.list_events(session, contributor, limit)
    subjects = [event.subject_id for event in events]

    found_objects = {
        obj.id: ObjectOut.model_validate(obj)
        for obj in await objects.list_objects_by_ids(session, subjects)
    }
    found_relations = {
        relation.id: relation
        for relation in await objects_service.load_relations(
            session, await objects.list_relations_by_ids(session, subjects)
        )
    }
    found_comments = {
        comment.id: CommentOut.model_validate(comment)
        for comment in await comments.list_comments_by_ids(session, subjects)
    }

    feed = [
        EventOut(
            id=event.id,
            at=event.at,
            kind=event.kind,
            contributor=event.contributor,
            source=event.source,
            object=found_objects.get(event.subject_id),
            relation=found_relations.get(event.subject_id),
            comment=found_comments.get(event.subject_id),
        )
        for event in events
    ]
    return [entry for entry in feed if entry.object or entry.relation or entry.comment]
