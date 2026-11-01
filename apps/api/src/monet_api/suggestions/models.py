import datetime
import uuid

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Suggestion(SQLModel, table=True):
    __tablename__ = "suggestions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    body: str
    page_path: str
    contributor: str | None = None
    at: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True
        )
    )


class SuggestionScreenshot(SQLModel, table=True):
    __tablename__ = "suggestion_screenshots"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    suggestion_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    position: int
    media_type: str
    content: bytes = Field(sa_column=sa.Column(sa.LargeBinary, nullable=False))
