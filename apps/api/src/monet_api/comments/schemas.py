import datetime
import uuid

from pydantic import BaseModel

from monet_api.core.schemas import Contributor, ORMModel, Prose


class CommentOut(ORMModel):
    id: uuid.UUID
    object_id: uuid.UUID
    body: str
    contributor: str | None
    at: datetime.datetime


class CommentCreate(BaseModel):
    body: Prose
    contributor: Contributor = None
