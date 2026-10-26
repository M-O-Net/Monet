import datetime
import uuid
from typing import Literal

from pydantic import BaseModel

from monet_api.comments.schemas import CommentOut
from monet_api.objects.schemas import ObjectOut, RelationOut

EventKind = Literal["object_created", "relation_created", "comment_created"]


class EventOut(BaseModel):
    id: uuid.UUID
    at: datetime.datetime
    kind: EventKind
    contributor: str | None
    source: str | None
    object: ObjectOut | None
    relation: RelationOut | None
    comment: CommentOut | None
