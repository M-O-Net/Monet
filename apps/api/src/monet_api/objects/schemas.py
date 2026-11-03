import datetime
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field

from monet_api.core.schemas import (
    MAX_ITEMS,
    Contributor,
    Data,
    Label,
    Latex,
    ORMModel,
    Prose,
    Url,
)


class FacetOut(ORMModel):
    type_id: uuid.UUID
    data: dict[str, Any] | None


class ObjectOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    facets: list[FacetOut]


class ObjectPageOut(BaseModel):
    items: list[ObjectOut]
    total: int


class ReferenceIn(BaseModel):
    label: Label
    url: Url


class ReferenceOut(ORMModel):
    label: str
    url: str


class FacetIn(BaseModel):
    type_id: uuid.UUID
    data: Data = None


class TypeIn(BaseModel):
    data_kind: Label | None = None
    supertype_ids: list[uuid.UUID] = Field(default_factory=list, max_length=MAX_ITEMS)


class SignatureIn(BaseModel):
    domain_id: uuid.UUID
    codomain_id: uuid.UUID


class ObjectCreate(BaseModel):
    latex: Latex
    description: Prose | None = None
    image_url: Url | None = None
    references: list[ReferenceIn] = Field(default_factory=list, max_length=MAX_ITEMS)
    facets: list[FacetIn] = Field(default_factory=list, max_length=MAX_ITEMS)
    as_type: TypeIn | None = None
    signatures: list[SignatureIn] = Field(default_factory=list, max_length=MAX_ITEMS)
    sections: list[uuid.UUID] = Field(default_factory=list, max_length=MAX_ITEMS)
    contributor: Contributor = None


class ObjectUpdate(BaseModel):
    latex: Latex
    description: Prose | None = None
    image_url: Url | None = None
    references: list[ReferenceIn] = Field(default_factory=list, max_length=MAX_ITEMS)


class FacetData(BaseModel):
    data: Data = None


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
    references: list[ReferenceOut]


class RelationCreate(BaseModel):
    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID] = Field(max_length=MAX_ITEMS)
    output_object_ids: list[uuid.UUID] = Field(max_length=MAX_ITEMS)
    references: list[ReferenceIn] = Field(default_factory=list, max_length=MAX_ITEMS)
    contributor: Contributor = None


ObjectRole = Literal["type", "map", "section", "instance"]


class FacetDetailOut(BaseModel):
    type: ObjectOut
    data: dict[str, Any] | None


class TypeOut(BaseModel):
    data_kind: str | None
    data_kinds: list[str]


class SignatureOut(BaseModel):
    id: uuid.UUID
    domain: ObjectOut
    codomain: ObjectOut


class RelationGroupOut(BaseModel):
    operator: ObjectOut
    relations: list[RelationOut]
    total: int


class ObjectDetailOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    image_url: str | None
    roles: list[ObjectRole]
    provenance: ProvenanceOut | None
    facets: list[FacetDetailOut]
    implied_types: list[ObjectOut]
    as_type: TypeOut | None
    subtypes: list[ObjectOut]
    supertypes: list[ObjectOut]
    instance_count: int
    signatures: list[SignatureOut]
    maps_from: list[ObjectOut]
    maps_to: list[ObjectOut]
    references: list[ReferenceOut]
    is_top_level: bool
    sections: list[ObjectOut]
    filed_count: int
    relation_count: int
    as_operator: list[RelationGroupOut]
    as_input: list[RelationGroupOut]
    as_output: list[RelationGroupOut]


NeighborhoodSide = Literal["operator", "input", "output"]


class RelationPageOut(BaseModel):
    items: list[RelationOut]
    total: int


class LoopStepOut(BaseModel):
    relation: RelationOut
    source: ObjectOut
    target: ObjectOut


class RelationMapOut(BaseModel):
    relations: list[RelationOut]
    omitted: int


class HiddenRelationsOut(BaseModel):
    operator: ObjectOut
    side: NeighborhoodSide
    count: int


class NeighborhoodOut(BaseModel):
    relations: list[RelationOut]
    hidden: list[HiddenRelationsOut]


class ComputedOutput(BaseModel):
    latex: Latex
    data: Data = None


class RelationAssert(BaseModel):
    """Record a computed result; outputs are values because they may not exist as objects yet."""

    operator_id: uuid.UUID
    input_object_ids: list[uuid.UUID] = Field(max_length=MAX_ITEMS)
    outputs: list[ComputedOutput] = Field(max_length=MAX_ITEMS)
    implementation_id: uuid.UUID | None = None
    references: list[ReferenceIn] = Field(default_factory=list, max_length=MAX_ITEMS)
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


class SectionTypeOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    instance_count: int
    supertype_ids: list[uuid.UUID]
    elsewhere: list[ObjectOut]


class SubsectionOut(BaseModel):
    id: uuid.UUID
    latex: str
    description: str | None
    entries: list[ObjectOut]


class SectionOut(BaseModel):
    types: list[SectionTypeOut]
    entries: list[ObjectOut]
    subsections: list[SubsectionOut]


class OperatorDisplayOut(ORMModel):
    operator_id: uuid.UUID
    template: str | None
    hidden_by_default: bool


class OperatorDisplayUpdate(BaseModel):
    template: Prose | None
    hidden_by_default: bool
