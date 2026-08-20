"""Raw SQLModel queries for the objects domain. No business logic, no 404s — see service.py."""

import uuid

from sqlalchemy import or_
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.objects.models import Object, Relation, RelationInput, RelationOutput, TopLevelObject


async def get_object(session: AsyncSession, object_id: uuid.UUID) -> Object | None:
    return await session.get(Object, object_id)


async def list_objects(session: AsyncSession) -> list[Object]:
    return list((await session.exec(select(Object))).all())


async def create_object(session: AsyncSession, latex: str, description: str | None) -> Object:
    obj = Object(latex=latex, description=description)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_object(
    session: AsyncSession, obj: Object, latex: str, description: str | None
) -> Object:
    obj.latex = latex
    obj.description = description
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_object(session: AsyncSession, obj: Object) -> None:
    await session.delete(obj)
    await session.commit()


async def get_top_level_object(
    session: AsyncSession, object_id: uuid.UUID
) -> TopLevelObject | None:
    return await session.get(TopLevelObject, object_id)


async def list_top_level_object_ids(session: AsyncSession) -> list[uuid.UUID]:
    return list((await session.exec(select(TopLevelObject.object_id))).all())


async def add_top_level_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    session.add(TopLevelObject(object_id=object_id))
    await session.commit()


async def delete_top_level_object(session: AsyncSession, row: TopLevelObject) -> None:
    await session.delete(row)
    await session.commit()


async def get_relation(session: AsyncSession, relation_id: uuid.UUID) -> Relation | None:
    return await session.get(Relation, relation_id)


async def list_relations(session: AsyncSession) -> list[Relation]:
    return list((await session.exec(select(Relation))).all())


async def list_relations_by_operator(session: AsyncSession, object_id: uuid.UUID) -> list[Relation]:
    return list(
        (await session.exec(select(Relation).where(Relation.operator_id == object_id))).all()
    )


async def list_relation_ids_by_input(
    session: AsyncSession, object_id: uuid.UUID
) -> list[uuid.UUID]:
    return list(
        (
            await session.exec(
                select(RelationInput.relation_id).where(RelationInput.object_id == object_id)
            )
        ).all()
    )


async def list_relation_ids_by_output(
    session: AsyncSession, object_id: uuid.UUID
) -> list[uuid.UUID]:
    return list(
        (
            await session.exec(
                select(RelationOutput.relation_id).where(RelationOutput.object_id == object_id)
            )
        ).all()
    )


async def list_relation_inputs(
    session: AsyncSession, relation_id: uuid.UUID
) -> list[RelationInput]:
    return list(
        (
            await session.exec(
                select(RelationInput)
                .where(RelationInput.relation_id == relation_id)
                .order_by(RelationInput.position)  # type: ignore[arg-type]
            )
        ).all()
    )


async def list_relation_outputs(
    session: AsyncSession, relation_id: uuid.UUID
) -> list[RelationOutput]:
    return list(
        (
            await session.exec(
                select(RelationOutput)
                .where(RelationOutput.relation_id == relation_id)
                .order_by(RelationOutput.position)  # type: ignore[arg-type]
            )
        ).all()
    )


async def create_relation(session: AsyncSession, operator_id: uuid.UUID) -> Relation:
    relation = Relation(operator_id=operator_id)
    session.add(relation)
    await session.flush()
    return relation


def add_relation_input(
    session: AsyncSession, relation_id: uuid.UUID, object_id: uuid.UUID, position: int
) -> None:
    session.add(RelationInput(relation_id=relation_id, object_id=object_id, position=position))


def add_relation_output(
    session: AsyncSession, relation_id: uuid.UUID, object_id: uuid.UUID, position: int
) -> None:
    session.add(RelationOutput(relation_id=relation_id, object_id=object_id, position=position))


async def clear_relation_slots(session: AsyncSession, relation_id: uuid.UUID) -> None:
    for input_row in await list_relation_inputs(session, relation_id):
        await session.delete(input_row)
    for output_row in await list_relation_outputs(session, relation_id):
        await session.delete(output_row)
    await session.flush()


async def delete_relations_referencing_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    used_as_input = select(RelationInput.relation_id).where(RelationInput.object_id == object_id)
    used_as_output = select(RelationOutput.relation_id).where(RelationOutput.object_id == object_id)
    referenced = or_(
        Relation.id.in_(used_as_input),  # type: ignore[attr-defined]
        Relation.id.in_(used_as_output),  # type: ignore[attr-defined]
    )
    await session.exec(delete(Relation).where(referenced))
    await session.flush()


async def delete_relation(session: AsyncSession, relation: Relation) -> None:
    await session.delete(relation)
    await session.commit()
