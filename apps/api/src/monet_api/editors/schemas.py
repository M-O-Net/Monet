import datetime
import uuid
from typing import Annotated

from pydantic import BaseModel, Field

from monet_api.core.schemas import Label, ORMModel

Level = Annotated[int, Field(ge=1, le=3)]


class EditorOut(ORMModel):
    id: uuid.UUID | None
    name: str
    level: int


class EditorCreate(BaseModel):
    name: Label
    level: Level


class EditorCreated(EditorOut):
    key: str


class ChangeOut(ORMModel):
    at: datetime.datetime
    editor: str
    method: str
    path: str
    status: int
