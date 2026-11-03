import datetime
import uuid

from pydantic import BaseModel

from monet_api.core.schemas import Contributor, OptionalEmail, ORMModel, Prose


class CommentOut(ORMModel):
    id: uuid.UUID
    object_id: uuid.UUID
    body: str
    contributor: str | None
    email: str | None
    at: datetime.datetime


class CommentCreate(BaseModel):
    body: Prose
    contributor: Contributor = None
    email: OptionalEmail = None
