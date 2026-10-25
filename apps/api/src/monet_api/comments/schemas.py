import datetime
import uuid

from pydantic import BaseModel

from monet_api.core.schemas import Contributor, ORMModel


class CommentOut(ORMModel):
    id: uuid.UUID
    object_id: uuid.UUID
    body: str
    contributor: str | None
    at: datetime.datetime


class CommentCreate(BaseModel):
    body: str
    contributor: Contributor = None
