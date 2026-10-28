import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
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
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    label: str
    url: str
    position: int


class Relation(SQLModel, table=True):
    __tablename__ = "relations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    operator_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )


class RelationReference(SQLModel, table=True):
    __tablename__ = "relation_references"
    __table_args__ = (sa.UniqueConstraint("relation_id", "url"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    relation_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("relations.id", ondelete="CASCADE"), nullable=False)
    )
    label: str
    url: str
    position: int


class RelationInput(SQLModel, table=True):
    __tablename__ = "relation_input"
    __table_args__ = (
        sa.Index("ix_relation_input_relation_id_position", "relation_id", "position"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    relation_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("relations.id", ondelete="CASCADE"), nullable=False)
    )
    object_id: uuid.UUID = Field(foreign_key="objects.id", index=True)
    position: int


class RelationOutput(SQLModel, table=True):
    __tablename__ = "relation_output"
    __table_args__ = (
        sa.Index("ix_relation_output_relation_id_position", "relation_id", "position"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    relation_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("relations.id", ondelete="CASCADE"), nullable=False)
    )
    object_id: uuid.UUID = Field(foreign_key="objects.id", index=True)
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


def _owned_by(column: str) -> sa.Column[uuid.UUID]:
    return sa.Column(sa.ForeignKey(column, ondelete="CASCADE"), nullable=False, index=True)


class Type(SQLModel, table=True):
    __tablename__ = "types"

    object_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), primary_key=True, nullable=False
        )
    )
    data_kind: str | None = None


class Membership(SQLModel, table=True):
    __tablename__ = "memberships"
    __table_args__ = (
        sa.UniqueConstraint("object_id", "type_id"),
        sa.Index("ix_memberships_data_equality", "data", postgresql_using="hash"),
        sa.Index(
            "ix_memberships_data_containment",
            "data",
            postgresql_using="gin",
            postgresql_ops={"data": "jsonb_path_ops"},
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    object_id: uuid.UUID = Field(sa_column=_owned_by("objects.id"))
    type_id: uuid.UUID = Field(sa_column=_owned_by("types.object_id"))
    data: dict[str, Any] | None = Field(
        default=None, sa_column=sa.Column(JSONB(none_as_null=True), nullable=True)
    )


class Subtype(SQLModel, table=True):
    __tablename__ = "subtypes"

    type_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("types.object_id", ondelete="CASCADE"), primary_key=True, nullable=False
        )
    )
    supertype_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("types.object_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
            index=True,
        )
    )


class Signature(SQLModel, table=True):
    __tablename__ = "signatures"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    map_id: uuid.UUID = Field(sa_column=_owned_by("objects.id"))
    domain_id: uuid.UUID = Field(sa_column=_owned_by("types.object_id"))
    codomain_id: uuid.UUID = Field(sa_column=_owned_by("types.object_id"))


class SectionFiling(SQLModel, table=True):
    __tablename__ = "section_filings"

    object_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), primary_key=True, nullable=False
        )
    )
    section_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
            index=True,
        )
    )
