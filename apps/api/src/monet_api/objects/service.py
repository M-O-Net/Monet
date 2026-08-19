"""Business logic for the objects domain: 404/400 translation and schema assembly.

Orchestrates repository.py calls; owns no SQL of its own.
"""

import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.objects import repository
from monet_api.objects.models import Object, Relation
from monet_api.objects.schemas import (
    ObjectCreate,
    ObjectDetailOut,
    ObjectOut,
    ObjectUpdate,
    RelationCreate,
    RelationOut,
    RelationSlotOut,
)


async def get_object_or_404(session: AsyncSession, object_id: uuid.UUID) -> Object:
    obj = await repository.get_object(session, object_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="object not found")
    return obj


async def get_relation_or_404(session: AsyncSession, relation_id: uuid.UUID) -> Relation:
    relation = await repository.get_relation(session, relation_id)
    if relation is None:
        raise HTTPException(status_code=404, detail="relation not found")
    return relation


async def _load_relation_out(session: AsyncSession, relation: Relation) -> RelationOut:
    operator = await repository.get_object(session, relation.operator_id)
    if operator is None:
        raise HTTPException(status_code=500, detail="relation references a missing operator")

    input_rows = await repository.list_relation_inputs(session, relation.id)
    output_rows = await repository.list_relation_outputs(session, relation.id)

    inputs: list[RelationSlotOut] = []
    for input_row in input_rows:
        obj = await get_object_or_404(session, input_row.object_id)
        inputs.append(
            RelationSlotOut(position=input_row.position, object=ObjectOut.model_validate(obj))
        )

    outputs: list[RelationSlotOut] = []
    for output_row in output_rows:
        obj = await get_object_or_404(session, output_row.object_id)
        outputs.append(
            RelationSlotOut(position=output_row.position, object=ObjectOut.model_validate(obj))
        )

    return RelationOut(
        id=relation.id,
        operator=ObjectOut.model_validate(operator),
        inputs=inputs,
        outputs=outputs,
    )


async def list_objects(session: AsyncSession) -> list[Object]:
    return await repository.list_objects(session)


async def create_object(session: AsyncSession, body: ObjectCreate) -> Object:
    return await repository.create_object(session, body.latex, body.description)


async def get_object_detail(session: AsyncSession, object_id: uuid.UUID) -> ObjectDetailOut:
    obj = await get_object_or_404(session, object_id)

    as_operator = await repository.list_relations_by_operator(session, object_id)
    as_input_ids = await repository.list_relation_ids_by_input(session, object_id)
    as_output_ids = await repository.list_relation_ids_by_output(session, object_id)

    async def _load_many(relations: list[Relation]) -> list[RelationOut]:
        return [await _load_relation_out(session, r) for r in relations]

    as_input_relations = [
        r for rid in as_input_ids if (r := await repository.get_relation(session, rid)) is not None
    ]
    as_output_relations = [
        r
        for rid in as_output_ids
        if (r := await repository.get_relation(session, rid)) is not None
    ]

    is_top_level = await repository.get_top_level_object(session, object_id) is not None

    return ObjectDetailOut(
        id=obj.id,
        latex=obj.latex,
        description=obj.description,
        is_top_level=is_top_level,
        as_operator=await _load_many(as_operator),
        as_input=await _load_many(as_input_relations),
        as_output=await _load_many(as_output_relations),
    )


async def update_object(session: AsyncSession, object_id: uuid.UUID, body: ObjectUpdate) -> Object:
    obj = await get_object_or_404(session, object_id)
    return await repository.update_object(session, obj, body.latex, body.description)


async def delete_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    obj = await get_object_or_404(session, object_id)
    try:
        await repository.delete_object(session, obj)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail="object is still used as an operator or as a relation's input/output — "
            "remove those relations first",
        ) from exc


async def list_top_level_objects(session: AsyncSession) -> list[Object]:
    ids = await repository.list_top_level_object_ids(session)
    return [obj for oid in ids if (obj := await repository.get_object(session, oid)) is not None]


async def mark_top_level_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    await get_object_or_404(session, object_id)
    if await repository.get_top_level_object(session, object_id) is None:
        await repository.add_top_level_object(session, object_id)


async def unmark_top_level_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    row = await repository.get_top_level_object(session, object_id)
    if row is not None:
        await repository.delete_top_level_object(session, row)


async def list_relations(session: AsyncSession) -> list[RelationOut]:
    relations = await repository.list_relations(session)
    return [await _load_relation_out(session, r) for r in relations]


async def _validate_relation_operands(session: AsyncSession, body: RelationCreate) -> None:
    await get_object_or_404(session, body.operator_id)
    for oid in [*body.input_object_ids, *body.output_object_ids]:
        await get_object_or_404(session, oid)


async def create_relation(session: AsyncSession, body: RelationCreate) -> RelationOut:
    await _validate_relation_operands(session, body)

    relation = await repository.create_relation(session, body.operator_id)
    for position, oid in enumerate(body.input_object_ids):
        repository.add_relation_input(session, relation.id, oid, position)
    for position, oid in enumerate(body.output_object_ids):
        repository.add_relation_output(session, relation.id, oid, position)

    await session.commit()
    await session.refresh(relation)
    return await _load_relation_out(session, relation)


async def get_relation(session: AsyncSession, relation_id: uuid.UUID) -> RelationOut:
    relation = await get_relation_or_404(session, relation_id)
    return await _load_relation_out(session, relation)


async def replace_relation(
    session: AsyncSession, relation_id: uuid.UUID, body: RelationCreate
) -> RelationOut:
    relation = await get_relation_or_404(session, relation_id)
    await _validate_relation_operands(session, body)

    relation.operator_id = body.operator_id
    session.add(relation)
    await repository.clear_relation_slots(session, relation_id)

    for position, oid in enumerate(body.input_object_ids):
        repository.add_relation_input(session, relation.id, oid, position)
    for position, oid in enumerate(body.output_object_ids):
        repository.add_relation_output(session, relation.id, oid, position)

    await session.commit()
    await session.refresh(relation)
    return await _load_relation_out(session, relation)


async def delete_relation(session: AsyncSession, relation_id: uuid.UUID) -> None:
    relation = await get_relation_or_404(session, relation_id)
    await repository.delete_relation(session, relation)
