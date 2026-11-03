import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.editors import service
from monet_api.editors.access import Adder, Owner
from monet_api.editors.schemas import ChangeOut, EditorCreate, EditorCreated, EditorOut

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/editors/me", response_model=EditorOut, operation_id="get_current_editor")
async def get_current_editor(editor: Adder) -> EditorOut:
    return editor


@router.get("/editors", response_model=list[EditorOut], operation_id="list_editors")
async def list_editors(session: DbSession, owner: Owner) -> list[EditorOut]:
    return await service.list_editors(session)


@router.post(
    "/editors", response_model=EditorCreated, operation_id="create_editor", status_code=201
)
async def create_editor(body: EditorCreate, session: DbSession, owner: Owner) -> EditorCreated:
    return await service.create_editor(session, body)


@router.delete("/editors/{editor_id}", status_code=204, operation_id="delete_editor")
async def delete_editor(editor_id: uuid.UUID, session: DbSession, owner: Owner) -> None:
    await service.delete_editor(session, editor_id)


@router.get("/changes", response_model=list[ChangeOut], operation_id="list_changes")
async def list_changes(session: DbSession, owner: Owner) -> list[ChangeOut]:
    return await service.list_changes(session)
