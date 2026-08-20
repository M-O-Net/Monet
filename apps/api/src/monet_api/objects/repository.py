"""Raw SQLModel queries for the objects domain. No business logic, no 404s — see service.py."""

import uuid
from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.objects.models import (
    Object,
    OperatorDisplay,
    Relation,
    RelationInput,
    RelationOutput,
    TopLevelObject,
)


async def get_object(session: AsyncSession, object_id: uuid.UUID) -> Object | None:
    return await session.get(Object, object_id)


async def list_objects(session: AsyncSession) -> list[Object]:
    return list((await session.exec(select(Object).order_by(col(Object.latex)))).all())


async def list_objects_by_ids(
    session: AsyncSession, object_ids: Sequence[uuid.UUID]
) -> list[Object]:
    if not object_ids:
        return []
    return list(
        (
            await session.exec(
                select(Object).where(col(Object.id).in_(object_ids)).order_by(col(Object.latex))
            )
        ).all()
    )


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


async def list_top_level_objects(session: AsyncSession) -> list[Object]:
    return list(
        (
            await session.exec(
                select(Object)
                .join(TopLevelObject, col(TopLevelObject.object_id) == col(Object.id))
                .order_by(col(Object.latex))
            )
        ).all()
    )


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


async def list_relations_by_ids(
    session: AsyncSession, relation_ids: Sequence[uuid.UUID]
) -> list[Relation]:
    if not relation_ids:
        return []
    return list(
        (await session.exec(select(Relation).where(col(Relation.id).in_(relation_ids)))).all()
    )


async def list_relations_by_operator(session: AsyncSession, object_id: uuid.UUID) -> list[Relation]:
    return list(
        (await session.exec(select(Relation).where(Relation.operator_id == object_id))).all()
    )


async def list_relation_ids_by_input(
    session: AsyncSession, object_id: uuid.UUID, *, exclude_operator_ids: Sequence[uuid.UUID] = ()
) -> list[uuid.UUID]:
    query = select(RelationInput.relation_id).where(RelationInput.object_id == object_id)
    if exclude_operator_ids:
        query = query.join(Relation, col(Relation.id) == col(RelationInput.relation_id)).where(
            col(Relation.operator_id).notin_(exclude_operator_ids)
        )
    return list((await session.exec(query)).all())


async def list_relation_ids_by_output(
    session: AsyncSession, object_id: uuid.UUID, *, exclude_operator_ids: Sequence[uuid.UUID] = ()
) -> list[uuid.UUID]:
    query = select(RelationOutput.relation_id).where(RelationOutput.object_id == object_id)
    if exclude_operator_ids:
        query = query.join(Relation, col(Relation.id) == col(RelationOutput.relation_id)).where(
            col(Relation.operator_id).notin_(exclude_operator_ids)
        )
    return list((await session.exec(query)).all())


async def list_membership_outputs(
    session: AsyncSession, operator_ids: Sequence[uuid.UUID], section_ids: Sequence[uuid.UUID]
) -> list[RelationOutput]:
    if not operator_ids or not section_ids:
        return []
    return list(
        (
            await session.exec(
                select(RelationOutput)
                .join(Relation, col(Relation.id) == col(RelationOutput.relation_id))
                .where(col(Relation.operator_id).in_(operator_ids))
                .where(col(RelationOutput.object_id).in_(section_ids))
            )
        ).all()
    )


async def list_membership_inputs(
    session: AsyncSession, operator_ids: Sequence[uuid.UUID], member_ids: Sequence[uuid.UUID]
) -> list[RelationInput]:
    if not operator_ids or not member_ids:
        return []
    return list(
        (
            await session.exec(
                select(RelationInput)
                .join(Relation, col(Relation.id) == col(RelationInput.relation_id))
                .where(col(Relation.operator_id).in_(operator_ids))
                .where(col(RelationInput.object_id).in_(member_ids))
            )
        ).all()
    )


async def list_membership_operator_ids(session: AsyncSession) -> list[uuid.UUID]:
    return list(
        (
            await session.exec(
                select(OperatorDisplay.operator_id).where(col(OperatorDisplay.is_membership))
            )
        ).all()
    )


async def get_operator_display(
    session: AsyncSession, operator_id: uuid.UUID
) -> OperatorDisplay | None:
    return await session.get(OperatorDisplay, operator_id)


async def list_operator_displays(
    session: AsyncSession, operator_ids: Sequence[uuid.UUID]
) -> list[OperatorDisplay]:
    if not operator_ids:
        return []
    return list(
        (
            await session.exec(
                select(OperatorDisplay).where(col(OperatorDisplay.operator_id).in_(operator_ids))
            )
        ).all()
    )


async def upsert_operator_display(
    session: AsyncSession,
    operator_id: uuid.UUID,
    template: str | None,
    hidden_by_default: bool,
    is_membership: bool,
) -> OperatorDisplay:
    row = await session.get(OperatorDisplay, operator_id)
    if row is None:
        row = OperatorDisplay(operator_id=operator_id)
    row.template = template
    row.hidden_by_default = hidden_by_default
    row.is_membership = is_membership
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def list_relation_inputs_for(
    session: AsyncSession, relation_ids: Sequence[uuid.UUID]
) -> list[RelationInput]:
    if not relation_ids:
        return []
    return list(
        (
            await session.exec(
                select(RelationInput)
                .where(col(RelationInput.relation_id).in_(relation_ids))
                .order_by(col(RelationInput.relation_id), col(RelationInput.position))
            )
        ).all()
    )


async def list_relation_outputs_for(
    session: AsyncSession, relation_ids: Sequence[uuid.UUID]
) -> list[RelationOutput]:
    if not relation_ids:
        return []
    return list(
        (
            await session.exec(
                select(RelationOutput)
                .where(col(RelationOutput.relation_id).in_(relation_ids))
                .order_by(col(RelationOutput.relation_id), col(RelationOutput.position))
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
    for input_row in await list_relation_inputs_for(session, [relation_id]):
        await session.delete(input_row)
    for output_row in await list_relation_outputs_for(session, [relation_id]):
        await session.delete(output_row)
    await session.flush()


async def delete_relation(session: AsyncSession, relation: Relation) -> None:
    await session.delete(relation)
    await session.commit()
