import datetime
import uuid

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    object_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    body: str
    contributor: str | None = None
    at: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        )
    )
