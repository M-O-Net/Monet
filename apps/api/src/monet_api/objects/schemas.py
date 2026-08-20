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
    sections: list[ObjectOut]
    members: list[ObjectOut]
    as_operator: list[RelationOut]
    as_input: list[RelationOut]
    as_output: list[RelationOut]


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
