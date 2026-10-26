import datetime
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field

from monet_api.core.schemas import Contributor, ORMModel


class ObjectOut(ORMModel):
    id: uuid.UUID
    latex: str
    description: str | None
    data: dict[str, Any] | None


class ObjectReferenceIn(BaseModel):
    label: str
    url: str


class ObjectReferenceOut(ORMModel):
    label: str
    url: str


class SignatureIn(BaseModel):
    domain_id: uuid.UUID
    codomain_id: uuid.UUID


class ObjectCreate(BaseModel):
    latex: str
    description: str | None = None
    image_url: str | None = None
    data: dict[str, Any] | None = None
    references: list[ObjectReferenceIn] = Field(default_factory=list)
    member_of: list[uuid.UUID] = Field(default_factory=list)
    subtype_of: list[uuid.UUID] = Field(default_factory=list)
    signature: SignatureIn | None = None
    contributor: Contributor = None


class ObjectUpdate(BaseModel):
    latex: str
    description: str | None = None
    image_url: str | None = None
    data: dict[str, Any] | None = None
    references: list[ObjectReferenceIn] = Field(default_factory=list)


class RelationDisplayOut(ORMModel):
    template: str | None
    hidden_by_default: bool
    is_membership: bool
    is_subtype: bool
    is_signature: bool


class ProvenanceOut(ORMModel):
    at: datetime.datetime
    contributor: str | None
    source: str | None


class RelationSlotOut(BaseModel):
    position: int
    object: ObjectOut


class RelationOut(BaseModel):
    id: uuid.UUID
    operator: ObjectOut
    inputs: list[RelationSlotOut]
    outputs: list[RelationSlotOut]
    display: RelationDisplayOut | None
    provenance: ProvenanceOut | None


class RelationCreate(BaseModel):
    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID]
    output_object_ids: list[uuid.UUID]
    contributor: Contributor = None


ObjectRole = Literal["type", "map", "section", "instance"]


class SignatureOut(BaseModel):
    domain: ObjectOut
    codomain: ObjectOut


class ObjectDetailOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    image_url: str | None
    data: dict[str, Any] | None
    role: ObjectRole
    provenance: ProvenanceOut | None
    subtypes: list[ObjectOut]
    supertypes: list[ObjectOut]
    signature: SignatureOut | None
    maps_from: list[ObjectOut]
    maps_to: list[ObjectOut]
    references: list[ObjectReferenceOut]
    is_top_level: bool
    sections: list[ObjectOut]
    members: list[ObjectOut]
    as_operator: list[RelationOut]
    as_input: list[RelationOut]
    as_output: list[RelationOut]


class ComputedOutput(BaseModel):
    latex: str
    data: dict[str, Any] | None = None


class RelationAssert(BaseModel):
    """Record a computed result; outputs are values because they may not exist as objects yet."""

    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID]
    outputs: list[ComputedOutput]
    implementation_id: uuid.UUID | None = None
    contributor: Contributor = None


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
    is_subtype: bool
    is_signature: bool


class OperatorDisplayUpdate(BaseModel):
    template: str | None
    hidden_by_default: bool
    is_membership: bool
    is_subtype: bool = False
    is_signature: bool = False
