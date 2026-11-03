import uuid

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.editors.models import Change, Editor


async def find_editor_by_key_hash(session: AsyncSession, key_hash: str) -> Editor | None:
    return (await session.exec(select(Editor).where(Editor.key_hash == key_hash))).first()


async def list_editors(session: AsyncSession) -> list[Editor]:
    return list((await session.exec(select(Editor).order_by(col(Editor.name)))).all())


def add_editor(session: AsyncSession, name: str, email: str, level: int, key_hash: str) -> Editor:
    editor = Editor(name=name, email=email, level=level, key_hash=key_hash)
    session.add(editor)
    return editor


async def get_editor(session: AsyncSession, editor_id: uuid.UUID) -> Editor | None:
    return await session.get(Editor, editor_id)


async def delete_editor(session: AsyncSession, editor: Editor) -> None:
    await session.delete(editor)


def add_change(session: AsyncSession, editor: str, method: str, path: str, status: int) -> None:
    session.add(Change(editor=editor, method=method, path=path, status=status))


async def list_changes(session: AsyncSession, limit: int) -> list[Change]:
    query = select(Change).order_by(col(Change.at).desc()).limit(limit)
    return list((await session.exec(query)).all())
