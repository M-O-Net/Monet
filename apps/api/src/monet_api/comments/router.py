import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments import service
from monet_api.comments.models import Comment
from monet_api.comments.schemas import CommentCreate, CommentOut
from monet_api.core.db import get_session

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    "/objects/{object_id}/comments",
    response_model=list[CommentOut],
    operation_id="list_comments",
)
async def list_comments(object_id: uuid.UUID, session: DbSession) -> list[Comment]:
    return await service.list_comments(session, object_id)


@router.post(
    "/objects/{object_id}/comments",
    response_model=CommentOut,
    operation_id="create_comment",
    status_code=201,
)
async def create_comment(object_id: uuid.UUID, body: CommentCreate, session: DbSession) -> Comment:
    return await service.create_comment(session, object_id, body)


@router.delete("/comments/{comment_id}", status_code=204, operation_id="delete_comment")
async def delete_comment(comment_id: uuid.UUID, session: DbSession) -> None:
    await service.delete_comment(session, comment_id)
