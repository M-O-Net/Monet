import uuid

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments import repository
from monet_api.comments.models import Comment
from monet_api.comments.schemas import CommentCreate
from monet_api.events import repository as events
from monet_api.objects import service as objects_service


async def list_comments(session: AsyncSession, object_id: uuid.UUID) -> list[Comment]:
    await objects_service.get_object_or_404(session, object_id)
    return await repository.list_comments_for(session, object_id)


async def create_comment(
    session: AsyncSession, object_id: uuid.UUID, body: CommentCreate
) -> Comment:
    await objects_service.get_object_or_404(session, object_id)
    text = body.body.strip()
    if not text:
        raise HTTPException(status_code=400, detail="a comment needs a body")
    comment = await repository.add_comment(session, object_id, text, body.contributor)
    events.add_event(session, "comment_created", comment.id, body.contributor, None)
    await session.commit()
    await session.refresh(comment)
    return comment


async def delete_comment(session: AsyncSession, comment_id: uuid.UUID) -> None:
    comment = await repository.get_comment(session, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="comment not found")
    await repository.delete_comment(session, comment)
    await events.delete_events_for(session, [comment_id])
    await session.commit()
