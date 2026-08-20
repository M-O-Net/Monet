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


class RelationSlotOut(BaseModel):
    position: int
    object: ObjectOut


class RelationOut(BaseModel):
    id: uuid.UUID
    operator: ObjectOut
    inputs: list[RelationSlotOut]
    outputs: list[RelationSlotOut]


class RelationCreate(BaseModel):
    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID]
    output_object_ids: list[uuid.UUID]


class ObjectDetailOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    is_top_level: bool
    as_operator: list[RelationOut]
    as_input: list[RelationOut]
    as_output: list[RelationOut]


class RelationAssert(BaseModel):
    """A computed result being recorded.

    Outputs arrive as LaTeX rather than as ids because an implementation's output may not exist as
    an object yet.
    """

    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID]
    output_latex: list[str]


class RelationAssertOut(BaseModel):
    relation: RelationOut
    created_object_ids: list[uuid.UUID]
    created_relation: bool
