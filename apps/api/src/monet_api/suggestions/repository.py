import uuid

from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.suggestions.models import Suggestion, SuggestionScreenshot


async def add_suggestion(
    session: AsyncSession,
    body: str,
    page_path: str,
    contributor: str | None,
    screenshots: list[tuple[str, bytes]],
) -> Suggestion:
    suggestion = Suggestion(body=body, page_path=page_path, contributor=contributor)
    session.add(suggestion)
    await session.flush()
    for position, (media_type, content) in enumerate(screenshots):
        session.add(
            SuggestionScreenshot(
                suggestion_id=suggestion.id,
                position=position,
                media_type=media_type,
                content=content,
            )
        )
    return suggestion


async def list_suggestions(session: AsyncSession) -> list[Suggestion]:
    return list((await session.exec(select(Suggestion).order_by(col(Suggestion.at).desc()))).all())


async def list_screenshot_headers(
    session: AsyncSession, suggestion_ids: list[uuid.UUID]
) -> list[tuple[uuid.UUID, uuid.UUID, str]]:
    if not suggestion_ids:
        return []
    rows = await session.exec(
        select(
            SuggestionScreenshot.suggestion_id,
            SuggestionScreenshot.id,
            SuggestionScreenshot.media_type,
        )
        .where(col(SuggestionScreenshot.suggestion_id).in_(suggestion_ids))
        .order_by(col(SuggestionScreenshot.position))
    )
    return list(rows.all())


async def get_screenshot(
    session: AsyncSession, suggestion_id: uuid.UUID, screenshot_id: uuid.UUID
) -> SuggestionScreenshot | None:
    screenshot = await session.get(SuggestionScreenshot, screenshot_id)
    if screenshot is None or screenshot.suggestion_id != suggestion_id:
        return None
    return screenshot


async def delete_suggestion(session: AsyncSession, suggestion_id: uuid.UUID) -> bool:
    result = await session.exec(delete(Suggestion).where(col(Suggestion.id) == suggestion_id))
    return bool(result.rowcount)
