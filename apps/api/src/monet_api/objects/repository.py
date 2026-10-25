"""Raw SQLModel queries for the objects domain. No business logic, no 404s — see service.py."""

import uuid
from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy import ColumnElement, or_, union
from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from monet_api.objects.models import (
    Object,
    ObjectReference,
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


async def find_object_by_data(session: AsyncSession, data: dict[str, Any]) -> Object | None:
    return (await session.exec(select(Object).where(col(Object.data) == data).limit(1))).first()


async def query_objects(
    session: AsyncSession,
    *,
    membership_ops: Sequence[uuid.UUID],
    member_of: Sequence[uuid.UUID] | None,
    data_equals: dict[str, Any] | None,
    data_contains: dict[str, Any] | None,
    description_contains: str | None,
    where: Sequence[tuple[uuid.UUID, uuid.UUID]],
    limit: int,
) -> list[Object]:
    query = select(Object)
    if description_contains is not None:
        query = query.where(
            col(Object.description).icontains(description_contains, autoescape=True)
        )
    if member_of is not None:
        query = query.where(
            col(Object.id).in_(
                _inputs_mapped_to(membership_ops, col(RelationOutput.object_id).in_(member_of))
            )
        )
    if data_equals is not None:
        query = query.where(col(Object.data) == data_equals)
    if data_contains is not None:
        query = query.where(col(Object.data).contains(data_contains))
    for operator_id, output_id in where:
        query = query.where(
            col(Object.id).in_(
                _inputs_mapped_to([operator_id], col(RelationOutput.object_id) == output_id)
            )
        )
    return list((await session.exec(query.order_by(col(Object.latex)).limit(limit))).all())


def _inputs_mapped_to(
    operator_ids: Sequence[uuid.UUID], output_matches: ColumnElement[bool]
) -> SelectOfScalar[uuid.UUID]:
    return (
        select(RelationInput.object_id)
        .join(Relation, col(Relation.id) == col(RelationInput.relation_id))
        .join(RelationOutput, col(RelationOutput.relation_id) == col(Relation.id))
        .where(col(Relation.operator_id).in_(operator_ids))
        .where(output_matches)
    )


async def list_related_types(
    session: AsyncSession,
    subtype_ops: Sequence[uuid.UUID],
    start_id: uuid.UUID,
    direction: Literal["down", "up"],
    *,
    transitive: bool,
) -> list[uuid.UUID]:
    if not subtype_ops:
        return []
    edges = (
        select(
            col(RelationInput.object_id).label("sub"),
            col(RelationOutput.object_id).label("super"),
        )
        .join(Relation, col(Relation.id) == col(RelationInput.relation_id))
        .join(RelationOutput, col(RelationOutput.relation_id) == col(Relation.id))
        .where(col(Relation.operator_id).in_(subtype_ops))
        .subquery()
    )
    near, far = (
        (edges.c.super, edges.c.sub) if direction == "down" else (edges.c.sub, edges.c.super)
    )
    if not transitive:
        return list((await session.exec(select(far).where(near == start_id).distinct())).all())

    reached = select(far.label("id")).where(near == start_id).cte(recursive=True)
    reached = reached.union(select(far).join(reached, near == reached.c.id))
    return list((await session.exec(select(reached.c.id))).all())


async def list_relation_ids_touching(
    session: AsyncSession, object_id: uuid.UUID
) -> list[uuid.UUID]:
    touching = union(
        select(Relation.id).where(Relation.operator_id == object_id),
        select(RelationInput.relation_id).where(RelationInput.object_id == object_id),
        select(RelationOutput.relation_id).where(RelationOutput.object_id == object_id),
    )
    return list((await session.exec(touching)).scalars().all())  # type: ignore[call-overload]


async def add_object(
    session: AsyncSession,
    latex: str,
    description: str | None,
    image_url: str | None = None,
    data: dict[str, Any] | None = None,
) -> Object:
    obj = Object(latex=latex, description=description, image_url=image_url, data=data)
    session.add(obj)
    await session.flush()
    return obj


async def update_object(
    session: AsyncSession,
    obj: Object,
    latex: str,
    description: str | None,
    image_url: str | None,
    data: dict[str, Any] | None,
) -> Object:
    obj.latex = latex
    obj.description = description
    obj.image_url = image_url
    obj.data = data
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def list_object_references(
    session: AsyncSession, object_id: uuid.UUID
) -> list[ObjectReference]:
    return list(
        (
            await session.exec(
                select(ObjectReference)
                .where(col(ObjectReference.object_id) == object_id)
                .order_by(col(ObjectReference.position))
            )
        ).all()
    )


async def clear_object_references(session: AsyncSession, object_id: uuid.UUID) -> None:
    await session.exec(delete(ObjectReference).where(col(ObjectReference.object_id) == object_id))


def add_object_reference(
    session: AsyncSession, object_id: uuid.UUID, label: str, url: str, position: int
) -> None:
    session.add(ObjectReference(object_id=object_id, label=label, url=url, position=position))


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


async def list_subtype_operator_ids(session: AsyncSession) -> list[uuid.UUID]:
    return list(
        (
            await session.exec(
                select(OperatorDisplay.operator_id).where(col(OperatorDisplay.is_subtype))
            )
        ).all()
    )


async def list_signature_operator_ids(session: AsyncSession) -> list[uuid.UUID]:
    return list(
        (
            await session.exec(
                select(OperatorDisplay.operator_id).where(col(OperatorDisplay.is_signature))
            )
        ).all()
    )


async def list_type_ids(session: AsyncSession, subtype_ops: Sequence[uuid.UUID]) -> list[uuid.UUID]:
    if not subtype_ops:
        return []
    typed = union(
        _participants(RelationInput, subtype_ops),
        _participants(RelationOutput, subtype_ops),
    )
    return list((await session.exec(typed)).scalars().all())  # type: ignore[call-overload]


def _participants(
    slots: type[RelationInput] | type[RelationOutput], operator_ids: Sequence[uuid.UUID]
) -> SelectOfScalar[uuid.UUID]:
    return (
        select(slots.object_id)
        .join(Relation, col(Relation.id) == col(slots.relation_id))
        .where(col(Relation.operator_id).in_(operator_ids))
    )


async def list_signature_slots(
    session: AsyncSession, signature_ops: Sequence[uuid.UUID], map_id: uuid.UUID
) -> list[RelationOutput]:
    if not signature_ops:
        return []
    return list(
        (
            await session.exec(
                select(RelationOutput)
                .join(Relation, col(Relation.id) == col(RelationOutput.relation_id))
                .join(RelationInput, col(RelationInput.relation_id) == col(Relation.id))
                .where(col(Relation.operator_id).in_(signature_ops))
                .where(RelationInput.object_id == map_id)
                .order_by(col(RelationOutput.relation_id), col(RelationOutput.position))
            )
        ).all()
    )


async def list_maps_with_signature_slot(
    session: AsyncSession, signature_ops: Sequence[uuid.UUID], type_id: uuid.UUID, position: int
) -> list[uuid.UUID]:
    if not signature_ops:
        return []
    found = await session.exec(
        _inputs_mapped_to(
            signature_ops,
            (col(RelationOutput.object_id) == type_id) & (col(RelationOutput.position) == position),
        ).distinct()
    )
    return list(found.all())


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
    is_subtype: bool,
    is_signature: bool,
) -> OperatorDisplay:
    row = await session.get(OperatorDisplay, operator_id)
    if row is None:
        row = OperatorDisplay(operator_id=operator_id)
    row.template = template
    row.hidden_by_default = hidden_by_default
    row.is_membership = is_membership
    row.is_subtype = is_subtype
    row.is_signature = is_signature
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
