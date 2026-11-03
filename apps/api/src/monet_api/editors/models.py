import datetime
import uuid

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Editor(SQLModel, table=True):
    __tablename__ = "editors"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    level: int
    key_hash: str = Field(sa_column=sa.Column(sa.Text, nullable=False, unique=True))


class Change(SQLModel, table=True):
    __tablename__ = "changes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    at: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True
        )
    )
    editor: str
    method: str
    path: str
    status: int
