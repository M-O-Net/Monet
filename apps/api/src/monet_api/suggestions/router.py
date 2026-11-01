import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.suggestions import service
from monet_api.suggestions.models import Suggestion
from monet_api.suggestions.schemas import SuggestionCreate, SuggestionCreated, SuggestionOut

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


def require_review_key(x_review_key: Annotated[str | None, Header()] = None) -> None:
    service.check_review_key(x_review_key)


ReviewKey = Depends(require_review_key)


@router.post(
    "/suggestions",
    response_model=SuggestionCreated,
    operation_id="create_suggestion",
    status_code=201,
)
async def create_suggestion(body: SuggestionCreate, session: DbSession) -> Suggestion:
    return await service.create_suggestion(session, body)


@router.get(
    "/suggestions",
    response_model=list[SuggestionOut],
    operation_id="list_suggestions",
    dependencies=[ReviewKey],
)
async def list_suggestions(session: DbSession) -> list[SuggestionOut]:
    return await service.list_suggestions(session)


@router.get(
    "/suggestions/{suggestion_id}/screenshots/{screenshot_id}",
    response_class=Response,
    response_model=None,
    operation_id="get_suggestion_screenshot",
    dependencies=[ReviewKey],
    responses={200: {"content": {"image/*": {}}}},
)
async def get_suggestion_screenshot(
    suggestion_id: uuid.UUID, screenshot_id: uuid.UUID, session: DbSession
) -> Response:
    screenshot = await service.get_screenshot(session, suggestion_id, screenshot_id)
    return Response(content=screenshot.content, media_type=screenshot.media_type)


@router.delete(
    "/suggestions/{suggestion_id}",
    status_code=204,
    operation_id="delete_suggestion",
    dependencies=[ReviewKey],
)
async def delete_suggestion(suggestion_id: uuid.UUID, session: DbSession) -> None:
    await service.delete_suggestion(session, suggestion_id)
