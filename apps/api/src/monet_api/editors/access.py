from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.editors import service
from monet_api.editors.schemas import EditorOut


def editor_at_least(level: int) -> Callable[..., Awaitable[EditorOut]]:
    async def editor(
        request: Request,
        session: Annotated[AsyncSession, Depends(get_session)],
        x_editor_key: Annotated[str | None, Header()] = None,
    ) -> EditorOut:
        found = await service.require(session, x_editor_key)
        request.state.editor = found
        service.check_level(found, level)
        return found

    return editor


Adder = Annotated[EditorOut, Depends(editor_at_least(1))]
Builder = Annotated[EditorOut, Depends(editor_at_least(2))]
Owner = Annotated[EditorOut, Depends(editor_at_least(3))]
