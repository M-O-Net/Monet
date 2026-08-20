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


# ── GUI-only tables ──────────────────────────────────────────────────────────
# How the network is presented, never what it means. Kept off Object deliberately: an object's
# latex is mathematics and outlives any interface, whereas everything below is editorial and
# would be rewritten by a different front end. Both cascade on delete — a presentation row
# exists only in service of its object, so it must never be what blocks deleting one.


class TopLevelObject(SQLModel, table=True):
    """The contents page's roots.

    Which objects open the contents page as a section, rather than being reached by browsing
    into one. Nesting is NOT here: a section sits under another section by way of an ordinary
    membership relation in the graph (see OperatorDisplay.is_membership), so the hierarchy is
    the network's own data and this table only records where reading starts.
    """

    __tablename__ = "top_level_objects"

    object_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), primary_key=True, nullable=False
        )
    )


class OperatorDisplay(SQLModel, table=True):
    """How the GUI renders the relations built on one operator.

    Every field is presentation. Nothing here changes what a relation means, and the API never
    filters on it — `hidden_by_default` is advice the front end acts on, so that the count
    behind a "show more" disclosure is knowable without a second request.
    """

    __tablename__ = "operator_displays"

    operator_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("objects.id", ondelete="CASCADE"), primary_key=True, nullable=False
        )
    )
    # A LaTeX template with {in0}/{in1}/{out0} placeholders, e.g. "{in0} + {in1} = {out0}", so
    # an addition reads as an equation instead of the generic operands-arrow-operator row.
    template: str | None = None
    # For operators that will accumulate far more relations than anyone wants listed inline.
    hidden_by_default: bool = False
    # Marks an operator as meaning "belongs to": its relations stop being listed as ordinary
    # rows and become the section tags and member lists instead. A flag rather than a hardcoded
    # name, so renaming the Element Of object cannot break sectioning. Deliberately not unique
    # — SubsetOf and InstanceOf are membership-shaped too, and every query already takes a set.
    is_membership: bool = False
