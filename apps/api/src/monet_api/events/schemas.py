import datetime
import uuid

from pydantic import BaseModel

from monet_api.comments.schemas import CommentOut
from monet_api.objects.schemas import ObjectOut, RelationOut


class EventOut(BaseModel):
    id: uuid.UUID
    at: datetime.datetime
    kind: str
    contributor: str | None
    source: str | None
    object: ObjectOut | None
    relation: RelationOut | None
    comment: CommentOut | None
