import uuid
from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments.models import Comment


async def get_comment(session: AsyncSession, comment_id: uuid.UUID) -> Comment | None:
    return await session.get(Comment, comment_id)


async def list_comments_for(session: AsyncSession, object_id: uuid.UUID) -> list[Comment]:
    return list(
        (
            await session.exec(
                select(Comment).where(Comment.object_id == object_id).order_by(col(Comment.at))
            )
        ).all()
    )


async def list_comments_by_ids(
    session: AsyncSession, comment_ids: Sequence[uuid.UUID]
) -> list[Comment]:
    if not comment_ids:
        return []
    return list((await session.exec(select(Comment).where(col(Comment.id).in_(comment_ids)))).all())


async def add_comment(
    session: AsyncSession, object_id: uuid.UUID, body: str, contributor: str | None
) -> Comment:
    comment = Comment(object_id=object_id, body=body, contributor=contributor)
    session.add(comment)
    await session.flush()
    return comment


async def delete_comment(session: AsyncSession, comment: Comment) -> None:
    await session.delete(comment)
