import datetime
import uuid
from typing import Literal

from pydantic import Base64Bytes, BaseModel, Field

from monet_api.core.schemas import Contributor, ORMModel

MAX_SCREENSHOTS = 3

ScreenshotType = Literal["image/png", "image/jpeg", "image/webp"]


class ScreenshotIn(BaseModel):
    media_type: ScreenshotType
    data: Base64Bytes


class SuggestionCreate(BaseModel):
    body: str = Field(max_length=5000)
    page_path: str = Field(max_length=2000)
    contributor: Contributor = None
    screenshots: list[ScreenshotIn] = Field(default=[], max_length=MAX_SCREENSHOTS)


class SuggestionCreated(ORMModel):
    id: uuid.UUID
    at: datetime.datetime


class ScreenshotOut(ORMModel):
    id: uuid.UUID
    media_type: str


class SuggestionOut(ORMModel):
    id: uuid.UUID
    body: str
    page_path: str
    contributor: str | None
    at: datetime.datetime
    screenshots: list[ScreenshotOut]
