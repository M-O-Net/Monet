import datetime
import uuid

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    at: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True
        )
    )
    kind: str
    subject_id: uuid.UUID = Field(index=True)
    contributor: str | None = Field(default=None, index=True)
    source: str | None = None
