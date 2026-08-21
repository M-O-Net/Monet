import uuid

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Object(SQLModel, table=True):
    __tablename__ = "objects"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    latex: str
    description: str | None = None
    image_url: str | None = None


class ObjectReference(SQLModel, table=True):
    """Where to read more about an object — metadata, never a node in the network.

    Deliberately not a relation: a citation is not a mathematical fact relating two objects, and
    surfacing it as one would put Knot Atlas in the graph alongside polynomials.
    """

    __tablename__ = "object_references"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    object_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    )
    label: str
    url: str
    position: int


class Relation(SQLModel, table=True):
    __tablename__ = "relations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    operator_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    )


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
