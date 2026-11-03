import hashlib
import secrets
import uuid

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.config import settings
from monet_api.editors import repository
from monet_api.editors.schemas import ChangeOut, EditorCreate, EditorCreated, EditorOut

RECENT_CHANGES = 200


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


async def identify(session: AsyncSession, key: str | None) -> EditorOut | None:
    if not key:
        return None
    owner_key = settings.admin_key
    if owner_key and secrets.compare_digest(key.encode(), owner_key.encode()):
        return EditorOut(id=None, name=settings.admin_name, email=settings.admin_email, level=3)
    editor = await repository.find_editor_by_key_hash(session, _hash(key))
    return None if editor is None else EditorOut.model_validate(editor)


def check_level(editor: EditorOut, level: int) -> None:
    if editor.level < level:
        raise HTTPException(
            status_code=403,
            detail=f"this needs an editor key of level {level}; yours is level {editor.level}",
        )


async def require(session: AsyncSession, key: str | None) -> EditorOut:
    editor = await identify(session, key)
    if editor is None:
        detail = "this editor key is not valid" if key else "this needs an editor key"
        raise HTTPException(status_code=401, detail=detail)
    return editor


async def list_editors(session: AsyncSession) -> list[EditorOut]:
    return [EditorOut.model_validate(editor) for editor in await repository.list_editors(session)]


async def create_editor(session: AsyncSession, body: EditorCreate) -> EditorCreated:
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="an editor needs a name")
    key = secrets.token_urlsafe(24)
    editor = repository.add_editor(session, name, body.email, body.level, _hash(key))
    await session.commit()
    return EditorCreated(
        id=editor.id, name=editor.name, email=editor.email, level=editor.level, key=key
    )


async def delete_editor(session: AsyncSession, editor_id: uuid.UUID) -> None:
    editor = await repository.get_editor(session, editor_id)
    if editor is None:
        raise HTTPException(status_code=404, detail="editor not found")
    await repository.delete_editor(session, editor)
    await session.commit()


async def record_change(
    session: AsyncSession, editor: str, method: str, path: str, status: int
) -> None:
    repository.add_change(session, editor, method, path, status)
    await session.commit()


async def list_changes(session: AsyncSession) -> list[ChangeOut]:
    changes = await repository.list_changes(session, RECENT_CHANGES)
    return [ChangeOut.model_validate(change) for change in changes]
