import uuid

from pydantic import BaseModel, Field

from monet_api.core.schemas import ORMModel


class ObjectOut(ORMModel):
    id: uuid.UUID
    latex: str
    description: str | None


class ObjectReferenceIn(BaseModel):
    label: str
    url: str


class ObjectReferenceOut(ORMModel):
    label: str
    url: str


class ObjectCreate(BaseModel):
    latex: str
    description: str | None = None
    image_url: str | None = None
    references: list[ObjectReferenceIn] = Field(default_factory=list)


class ObjectUpdate(BaseModel):
    latex: str
    description: str | None = None
    image_url: str | None = None
    references: list[ObjectReferenceIn] = Field(default_factory=list)


class RelationDisplayOut(ORMModel):
    template: str | None
    hidden_by_default: bool
    is_membership: bool


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
    image_url: str | None
    references: list[ObjectReferenceOut]
    is_top_level: bool
    sections: list[ObjectOut]
    members: list[ObjectOut]
    as_operator: list[RelationOut]
    as_input: list[RelationOut]
    as_output: list[RelationOut]


class RelationAssert(BaseModel):
    """Record a computed result; outputs are LaTeX because they may not exist as objects yet."""

    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID]
    output_latex: list[str]


class RelationAssertOut(BaseModel):
    relation: RelationOut
    created_object_ids: list[uuid.UUID]
    created_relation: bool


class SectionNode(BaseModel):
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
