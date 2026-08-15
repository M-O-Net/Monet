import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.core.db import get_session
from monet_api.objects import service
from monet_api.objects.models import Object
from monet_api.objects.schemas import (
    ObjectCreate,
    ObjectDetailOut,
    ObjectOut,
    ObjectUpdate,
    RelationCreate,
    RelationOut,
)

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


# ── objects ──────────────────────────────────────────────────────────────────


@router.get("/objects", response_model=list[ObjectOut], operation_id="list_objects")
async def list_objects(session: DbSession) -> list[Object]:
    return await service.list_objects(session)


@router.post("/objects", response_model=ObjectOut, operation_id="create_object", status_code=201)
async def create_object(body: ObjectCreate, session: DbSession) -> Object:
    return await service.create_object(session, body)


@router.get("/objects/{object_id}", response_model=ObjectDetailOut, operation_id="get_object")
async def get_object(object_id: uuid.UUID, session: DbSession) -> ObjectDetailOut:
    return await service.get_object_detail(session, object_id)


@router.patch("/objects/{object_id}", response_model=ObjectOut, operation_id="update_object")
async def update_object(object_id: uuid.UUID, body: ObjectUpdate, session: DbSession) -> Object:
    return await service.update_object(session, object_id, body)


@router.delete("/objects/{object_id}", status_code=204, operation_id="delete_object")
async def delete_object(object_id: uuid.UUID, session: DbSession) -> None:
    await service.delete_object(session, object_id)


# ── top-level objects ────────────────────────────────────────────────────────
# The homepage's table of contents — see TopLevelObject's own docstring in models.py.


@router.get(
    "/top-level-objects", response_model=list[ObjectOut], operation_id="list_top_level_objects"
)
async def list_top_level_objects(session: DbSession) -> list[Object]:
    return await service.list_top_level_objects(session)


@router.put(
    "/top-level-objects/{object_id}", status_code=204, operation_id="mark_top_level_object"
)
async def mark_top_level_object(object_id: uuid.UUID, session: DbSession) -> None:
    await service.mark_top_level_object(session, object_id)


@router.delete(
    "/top-level-objects/{object_id}", status_code=204, operation_id="unmark_top_level_object"
)
async def unmark_top_level_object(object_id: uuid.UUID, session: DbSession) -> None:
    await service.unmark_top_level_object(session, object_id)


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
