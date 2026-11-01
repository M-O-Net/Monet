import secrets
import uuid

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.config import settings
from monet_api.suggestions import repository
from monet_api.suggestions.models import Suggestion, SuggestionScreenshot
from monet_api.suggestions.schemas import ScreenshotOut, SuggestionCreate, SuggestionOut

MAX_SCREENSHOT_BYTES = 1_500_000


def check_review_key(given: str | None) -> None:
    expected = settings.suggestions_review_key
    if not expected:
        raise HTTPException(status_code=503, detail="no review key is set on the server")
    if given is None or not secrets.compare_digest(given.encode(), expected.encode()):
        raise HTTPException(status_code=403, detail="wrong review key")


async def create_suggestion(session: AsyncSession, body: SuggestionCreate) -> Suggestion:
    text = body.body.strip()
    if not text:
        raise HTTPException(status_code=400, detail="a suggestion needs some text")
    if not body.page_path.startswith("/") or body.page_path.startswith("//"):
        raise HTTPException(status_code=400, detail="page_path must be a path on this site")
    for shot in body.screenshots:
        if len(shot.data) > MAX_SCREENSHOT_BYTES:
            raise HTTPException(status_code=413, detail="a screenshot is larger than 1.5 MB")
    suggestion = await repository.add_suggestion(
        session,
        text,
        body.page_path,
        body.contributor,
        [(shot.media_type, shot.data) for shot in body.screenshots],
    )
    await session.commit()
    await session.refresh(suggestion)
    return suggestion


async def list_suggestions(session: AsyncSession) -> list[SuggestionOut]:
    suggestions = await repository.list_suggestions(session)
    headers = await repository.list_screenshot_headers(session, [s.id for s in suggestions])
    shots: dict[uuid.UUID, list[ScreenshotOut]] = {}
    for suggestion_id, screenshot_id, media_type in headers:
        shots.setdefault(suggestion_id, []).append(
            ScreenshotOut(id=screenshot_id, media_type=media_type)
        )
    return [
        SuggestionOut(
            id=s.id,
            body=s.body,
            page_path=s.page_path,
            contributor=s.contributor,
            at=s.at,
            screenshots=shots.get(s.id, []),
        )
        for s in suggestions
    ]


async def get_screenshot(
    session: AsyncSession, suggestion_id: uuid.UUID, screenshot_id: uuid.UUID
) -> SuggestionScreenshot:
    screenshot = await repository.get_screenshot(session, suggestion_id, screenshot_id)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="screenshot not found")
    return screenshot


async def delete_suggestion(session: AsyncSession, suggestion_id: uuid.UUID) -> None:
    if not await repository.delete_suggestion(session, suggestion_id):
        raise HTTPException(status_code=404, detail="suggestion not found")
    await session.commit()
