import datetime
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field

from monet_api.core.schemas import Contributor, ORMModel


class FacetOut(ORMModel):
    type_id: uuid.UUID
    data: dict[str, Any] | None


class ObjectOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    facets: list[FacetOut]


class ObjectReferenceIn(BaseModel):
    label: str
    url: str


class ObjectReferenceOut(ORMModel):
    label: str
    url: str


class FacetIn(BaseModel):
    type_id: uuid.UUID
    data: dict[str, Any] | None = None


class TypeIn(BaseModel):
    data_kind: str | None = None
    supertype_ids: list[uuid.UUID] = Field(default_factory=list)


class SignatureIn(BaseModel):
    domain_id: uuid.UUID
    codomain_id: uuid.UUID


class ObjectCreate(BaseModel):
    latex: str
    description: str | None = None
    image_url: str | None = None
    references: list[ObjectReferenceIn] = Field(default_factory=list)
    facets: list[FacetIn] = Field(default_factory=list)
    as_type: TypeIn | None = None
    signatures: list[SignatureIn] = Field(default_factory=list)
    sections: list[uuid.UUID] = Field(default_factory=list)
    contributor: Contributor = None


class ObjectUpdate(BaseModel):
    latex: str
    description: str | None = None
    image_url: str | None = None
    references: list[ObjectReferenceIn] = Field(default_factory=list)


class FacetData(BaseModel):
    data: dict[str, Any] | None = None


class RelationDisplayOut(ORMModel):
    template: str | None
    hidden_by_default: bool


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


class FacetDetailOut(BaseModel):
    type: ObjectOut
    data: dict[str, Any] | None


class TypeOut(BaseModel):
    data_kind: str | None


class SignatureOut(BaseModel):
    id: uuid.UUID
    domain: ObjectOut
    codomain: ObjectOut


class ObjectDetailOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    image_url: str | None
    roles: list[ObjectRole]
    provenance: ProvenanceOut | None
    facets: list[FacetDetailOut]
    as_type: TypeOut | None
    subtypes: list[ObjectOut]
    supertypes: list[ObjectOut]
    instances: list[ObjectOut]
    signatures: list[SignatureOut]
    maps_from: list[ObjectOut]
    maps_to: list[ObjectOut]
    references: list[ObjectReferenceOut]
    is_top_level: bool
    sections: list[ObjectOut]
    filed: list[ObjectOut]
    as_operator: list[RelationOut]
    as_input: list[RelationOut]
    as_output: list[RelationOut]


NeighborhoodSide = Literal["operator", "input", "output"]


class HiddenRelationsOut(BaseModel):
    operator: ObjectOut
    side: NeighborhoodSide
    count: int


class NeighborhoodOut(BaseModel):
    relations: list[RelationOut]
    hidden: list[HiddenRelationsOut]


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


class OperatorDisplayUpdate(BaseModel):
    template: str | None
    hidden_by_default: bool
