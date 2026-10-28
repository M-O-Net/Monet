import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.objects import service
from monet_api.objects.schemas import (
    FacetData,
    NeighborhoodOut,
    ObjectCreate,
    ObjectDetailOut,
    ObjectOut,
    ObjectUpdate,
    OperatorDisplayOut,
    OperatorDisplayUpdate,
    RelationAssert,
    RelationAssertOut,
    RelationCreate,
    RelationOut,
    SectionNode,
    SignatureIn,
    SignatureOut,
)

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


# ── objects ──────────────────────────────────────────────────────────────────


@router.get("/objects", response_model=list[ObjectOut], operation_id="list_objects")
async def list_objects(session: DbSession) -> list[ObjectOut]:
    return await service.list_objects(session)


@router.get("/objects/query", response_model=list[ObjectOut], operation_id="query_objects")
async def query_objects(
    session: DbSession,
    member_of: uuid.UUID | None = None,
    transitive: bool = True,
    data_equals: str | None = None,
    data_contains: str | None = None,
    description_contains: str | None = None,
    where: Annotated[list[str] | None, Query()] = None,
) -> list[ObjectOut]:
    return await service.query_objects(
        session,
        member_of=member_of,
        transitive=transitive,
        data_equals=data_equals,
        data_contains=data_contains,
        description_contains=description_contains,
        where=where or [],
    )


@router.get("/types", response_model=list[ObjectOut], operation_id="list_types")
async def list_types(session: DbSession) -> list[ObjectOut]:
    return await service.list_types(session)


@router.get("/sections", response_model=list[ObjectOut], operation_id="list_sections")
async def list_sections(session: DbSession) -> list[ObjectOut]:
    return await service.list_sections(session)


@router.get(
    "/objects/{object_id}/subtypes", response_model=list[ObjectOut], operation_id="list_subtypes"
)
async def list_subtypes(
    object_id: uuid.UUID, session: DbSession, transitive: bool = False
) -> list[ObjectOut]:
    return await service.list_related_types(session, object_id, "down", transitive=transitive)


@router.get(
    "/objects/{object_id}/supertypes",
    response_model=list[ObjectOut],
    operation_id="list_supertypes",
)
async def list_supertypes(
    object_id: uuid.UUID, session: DbSession, transitive: bool = False
) -> list[ObjectOut]:
    return await service.list_related_types(session, object_id, "up", transitive=transitive)


@router.post("/objects", response_model=ObjectOut, operation_id="create_object", status_code=201)
async def create_object(body: ObjectCreate, session: DbSession) -> ObjectOut:
    return await service.create_object(session, body)


@router.get("/objects/{object_id}", response_model=ObjectDetailOut, operation_id="get_object")
async def get_object(object_id: uuid.UUID, session: DbSession) -> ObjectDetailOut:
    return await service.get_object_detail(session, object_id)


@router.get(
    "/objects/{object_id}/neighborhood",
    response_model=NeighborhoodOut,
    operation_id="get_neighborhood",
)
async def get_neighborhood(
    object_id: uuid.UUID,
    session: DbSession,
    per_map: Annotated[int, Query(ge=1, le=50)] = 3,
) -> NeighborhoodOut:
    return await service.get_neighborhood(session, object_id, per_map)


@router.patch("/objects/{object_id}", response_model=ObjectOut, operation_id="update_object")
async def update_object(object_id: uuid.UUID, body: ObjectUpdate, session: DbSession) -> ObjectOut:
    return await service.update_object(session, object_id, body)


@router.delete("/objects/{object_id}", status_code=204, operation_id="delete_object")
async def delete_object(object_id: uuid.UUID, session: DbSession) -> None:
    await service.delete_object(session, object_id)


@router.put(
    "/objects/{object_id}/facets/{type_id}", response_model=ObjectOut, operation_id="set_facet"
)
async def set_facet(
    object_id: uuid.UUID, type_id: uuid.UUID, body: FacetData, session: DbSession
) -> ObjectOut:
    return await service.set_facet(session, object_id, type_id, body)


@router.delete(
    "/objects/{object_id}/facets/{type_id}", status_code=204, operation_id="remove_facet"
)
async def remove_facet(object_id: uuid.UUID, type_id: uuid.UUID, session: DbSession) -> None:
    await service.remove_facet(session, object_id, type_id)


@router.post(
    "/objects/{object_id}/signatures",
    response_model=SignatureOut,
    operation_id="add_signature",
    status_code=201,
)
async def add_signature(
    object_id: uuid.UUID, body: SignatureIn, session: DbSession
) -> SignatureOut:
    return await service.add_signature(session, object_id, body)


@router.delete("/signatures/{signature_id}", status_code=204, operation_id="remove_signature")
async def remove_signature(signature_id: uuid.UUID, session: DbSession) -> None:
    await service.remove_signature(session, signature_id)


# ── top-level objects ────────────────────────────────────────────────────────
# The homepage's table of contents — see TopLevelObject's own docstring in models.py.


@router.get(
    "/top-level-objects", response_model=list[ObjectOut], operation_id="list_top_level_objects"
)
async def list_top_level_objects(session: DbSession) -> list[ObjectOut]:
    return await service.list_top_level_objects(session)


@router.put("/top-level-objects/{object_id}", status_code=204, operation_id="mark_top_level_object")
async def mark_top_level_object(object_id: uuid.UUID, session: DbSession) -> None:
    await service.mark_top_level_object(session, object_id)


@router.delete(
    "/top-level-objects/{object_id}", status_code=204, operation_id="unmark_top_level_object"
)
async def unmark_top_level_object(object_id: uuid.UUID, session: DbSession) -> None:
    await service.unmark_top_level_object(session, object_id)


@router.get("/contents", response_model=list[SectionNode], operation_id="get_contents")
async def get_contents(session: DbSession) -> list[SectionNode]:
    return await service.get_contents(session)


@router.get(
    "/operator-displays/{operator_id}",
    response_model=OperatorDisplayOut,
    operation_id="get_operator_display",
)
async def get_operator_display(operator_id: uuid.UUID, session: DbSession) -> OperatorDisplayOut:
    return await service.get_operator_display(session, operator_id)


@router.put(
    "/operator-displays/{operator_id}",
    response_model=OperatorDisplayOut,
    operation_id="set_operator_display",
)
async def set_operator_display(
    operator_id: uuid.UUID, body: OperatorDisplayUpdate, session: DbSession
) -> OperatorDisplayOut:
    return await service.set_operator_display(session, operator_id, body)


# ── relations ────────────────────────────────────────────────────────────────


@router.get("/relations", response_model=list[RelationOut], operation_id="list_relations")
async def list_relations(session: DbSession) -> list[RelationOut]:
    return await service.list_relations(session)


@router.post(
    "/relations", response_model=RelationOut, operation_id="create_relation", status_code=201
)
async def create_relation(body: RelationCreate, session: DbSession) -> RelationOut:
    return await service.create_relation(session, body)


@router.get("/relations/{relation_id}", response_model=RelationOut, operation_id="get_relation")
async def get_relation(relation_id: uuid.UUID, session: DbSession) -> RelationOut:
    return await service.get_relation(session, relation_id)


@router.put("/relations/{relation_id}", response_model=RelationOut, operation_id="replace_relation")
async def replace_relation(
    relation_id: uuid.UUID, body: RelationCreate, session: DbSession
) -> RelationOut:
    return await service.replace_relation(session, relation_id, body)


@router.delete("/relations/{relation_id}", status_code=204, operation_id="delete_relation")
async def delete_relation(relation_id: uuid.UUID, session: DbSession) -> None:
    await service.delete_relation(session, relation_id)


@router.post(
    "/relations/assert",
    response_model=RelationAssertOut,
    operation_id="assert_relation",
    status_code=200,
)
async def assert_relation(body: RelationAssert, session: DbSession) -> RelationAssertOut:
    return await service.assert_relation(session, body)
