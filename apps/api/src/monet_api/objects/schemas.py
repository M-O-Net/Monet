import uuid

from pydantic import BaseModel

from monet_api.core.schemas import ORMModel


class ObjectOut(ORMModel):
    id: uuid.UUID
    latex: str
    description: str | None


class ObjectCreate(BaseModel):
    latex: str
    description: str | None = None


class ObjectUpdate(BaseModel):
    latex: str
    description: str | None = None


class RelationDisplayOut(ORMModel):
    """How to render this relation, carried on every row that has an operator configured.

    `hidden_by_default` is advice, never a filter: the relation is still in the response, so
    the front end can collapse it behind a disclosure that knows its own count.
    """

    template: str | None
    hidden_by_default: bool


class RelationSlotOut(BaseModel):
    position: int
    object: ObjectOut


class RelationOut(BaseModel):
    id: uuid.UUID
    operator: ObjectOut
    inputs: list[RelationSlotOut]
    outputs: list[RelationSlotOut]
    display: RelationDisplayOut | None


class RelationCreate(BaseModel):
    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID]
    output_object_ids: list[uuid.UUID]


class ObjectDetailOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    is_top_level: bool
    # Membership relations are hoisted out of the three lists below into these two: they are
    # what an object is filed under, and what is filed under it. Left in as_operator, though —
    # on the membership operator's own page those rows are the entire content.
    sections: list[ObjectOut]
    members: list[ObjectOut]
    as_operator: list[RelationOut]
    as_input: list[RelationOut]
    as_output: list[RelationOut]


class SectionNode(BaseModel):
    """One entry in the contents tree.

    `children` holds only those members that are themselves sections (have members of their
    own); a section's specimens live on its own page, so the contents page stays a table of
    contents rather than a dump of the whole network. `member_count` is every member, so the
    UI can say how much is inside without asking again.
    """

    id: uuid.UUID
    latex: str
    description: str | None
    member_count: int
    children: list["SectionNode"]


SectionNode.model_rebuild()


class OperatorDisplayOut(ORMModel):
    operator_id: uuid.UUID
    template: str | None
    hidden_by_default: bool
    is_membership: bool


class OperatorDisplayUpdate(BaseModel):
    template: str | None
    hidden_by_default: bool
    is_membership: bool
