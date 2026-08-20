import uuid

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Object(SQLModel, table=True):
    __tablename__ = "objects"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    latex: str
    description: str | None = None


class Relation(SQLModel, table=True):
    __tablename__ = "relations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # No ondelete here (defaults to RESTRICT): deleting an object still used as an
    # operator somewhere is blocked, not silently cascaded — see router's delete_object.
    operator_id: uuid.UUID = Field(foreign_key="objects.id")


class RelationInput(SQLModel, table=True):
    __tablename__ = "relation_input"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    relation_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("relations.id", ondelete="CASCADE"), nullable=False)
    )
    object_id: uuid.UUID = Field(foreign_key="objects.id")
    position: int


class RelationOutput(SQLModel, table=True):
    __tablename__ = "relation_output"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    relation_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("relations.id", ondelete="CASCADE"), nullable=False)
    )
    object_id: uuid.UUID = Field(foreign_key="objects.id")
    position: int




class TopLevelObject(SQLModel, table=True):
    """The homepage's table of contents.

    Which objects are a journal "section" (Matrices, Polynomials, ...) rather than a specimen
    filed under one. Deliberately just a flag table, not a column on Object: membership here is
    closer to editorial curation than an intrinsic property of the object itself.
    """

    __tablename__ = "top_level_objects"

    object_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), primary_key=True, nullable=False
        )
    )


class OperatorDisplay(SQLModel, table=True):
    __tablename__ = "operator_displays"

    operator_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), primary_key=True, nullable=False
        )
    )
    template: str | None = None
    hidden_by_default: bool = False
    is_membership: bool = False
