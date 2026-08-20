import uuid

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Implementation(SQLModel, table=True):
    __tablename__ = "implementations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    operator_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    )
    code: str
