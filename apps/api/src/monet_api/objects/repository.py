"""Raw SQLModel queries for the objects domain. No business logic, no 404s — see service.py."""

import uuid
from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy import ColumnElement, or_, union
from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from monet_api.objects.models import (
    Membership,
    Object,
    ObjectReference,
    OperatorDisplay,
    Relation,
    RelationInput,
    RelationOutput,
    SectionFiling,
    Signature,
    Subtype,
    TopLevelObject,
    Type,
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
    session: AsyncSession, latex: str, description: str | None, image_url: str | None = None
) -> Object:
    obj = Object(latex=latex, description=description, image_url=image_url)
    session.add(obj)
    await session.flush()
    return obj


async def update_object(
    session: AsyncSession,
    obj: Object,
    latex: str,
    description: str | None,
    image_url: str | None,
) -> Object:
    obj.latex = latex
    obj.description = description
    obj.image_url = image_url
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
    session: AsyncSession, object_id: uuid.UUID
) -> list[uuid.UUID]:
    query = select(RelationInput.relation_id).where(RelationInput.object_id == object_id)
    return list((await session.exec(query)).all())


async def list_relation_ids_by_output(
    session: AsyncSession, object_id: uuid.UUID
) -> list[uuid.UUID]:
    query = select(RelationOutput.relation_id).where(RelationOutput.object_id == object_id)
    return list((await session.exec(query)).all())


async def list_operated_relations(
    session: AsyncSession, object_id: uuid.UUID
) -> list[tuple[uuid.UUID, uuid.UUID]]:
    query = (
        select(Relation.operator_id, Relation.id)
        .where(Relation.operator_id == object_id)
        .order_by(col(Relation.id))
    )
    return list((await session.exec(query)).all())


async def list_operand_relations(
    session: AsyncSession, object_id: uuid.UUID, side: Literal["input", "output"]
) -> list[tuple[uuid.UUID, uuid.UUID]]:
    slot = RelationInput if side == "input" else RelationOutput
    query = (
        select(Relation.operator_id, Relation.id)
        .join(slot, col(slot.relation_id) == col(Relation.id))
        .where(slot.object_id == object_id)
        .distinct()
        .order_by(col(Relation.operator_id), col(Relation.id))
    )
    return list((await session.exec(query)).all())


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
) -> OperatorDisplay:
    row = await session.get(OperatorDisplay, operator_id)
    if row is None:
        row = OperatorDisplay(operator_id=operator_id)
    row.template = template
    row.hidden_by_default = hidden_by_default
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


async def query_objects(
    session: AsyncSession,
    *,
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
    if member_of is not None or data_equals is not None or data_contains is not None:
        facets = select(Membership.object_id)
        if member_of is not None:
            facets = facets.where(col(Membership.type_id).in_(member_of))
        if data_equals is not None:
            facets = facets.where(col(Membership.data) == data_equals)
        if data_contains is not None:
            facets = facets.where(col(Membership.data).contains(data_contains))
        query = query.where(col(Object.id).in_(facets))
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


async def get_type(session: AsyncSession, type_id: uuid.UUID) -> Type | None:
    return await session.get(Type, type_id)


async def list_types(session: AsyncSession) -> list[Object]:
    return list(
        (
            await session.exec(
                select(Object)
                .join(Type, col(Type.object_id) == col(Object.id))
                .order_by(col(Object.latex))
            )
        ).all()
    )


async def list_types_of_kind(session: AsyncSession, data_kind: str) -> list[Type]:
    return list((await session.exec(select(Type).where(Type.data_kind == data_kind))).all())


def add_type(session: AsyncSession, object_id: uuid.UUID, data_kind: str | None) -> None:
    session.add(Type(object_id=object_id, data_kind=data_kind))


def add_subtype(session: AsyncSession, type_id: uuid.UUID, supertype_id: uuid.UUID) -> None:
    session.add(Subtype(type_id=type_id, supertype_id=supertype_id))


async def list_related_types(
    session: AsyncSession,
    start_ids: Sequence[uuid.UUID],
    direction: Literal["down", "up"],
    *,
    transitive: bool,
) -> list[uuid.UUID]:
    if not start_ids:
        return []
    near, far = (
        (col(Subtype.supertype_id), col(Subtype.type_id))
        if direction == "down"
        else (col(Subtype.type_id), col(Subtype.supertype_id))
    )
    if not transitive:
        return list((await session.exec(select(far).where(near.in_(start_ids)).distinct())).all())

    reached = select(far.label("id")).where(near.in_(start_ids)).cte(recursive=True)
    reached = reached.union(select(far).join(reached, near == reached.c.id))
    return list((await session.exec(select(reached.c.id))).all())


async def find_membership_by_data(session: AsyncSession, data: dict[str, Any]) -> Membership | None:
    return (
        await session.exec(select(Membership).where(col(Membership.data) == data).limit(1))
    ).first()


async def get_membership(
    session: AsyncSession, object_id: uuid.UUID, type_id: uuid.UUID
) -> Membership | None:
    return (
        await session.exec(
            select(Membership)
            .where(Membership.object_id == object_id)
            .where(Membership.type_id == type_id)
        )
    ).first()


async def list_memberships_for(
    session: AsyncSession, object_ids: Sequence[uuid.UUID]
) -> list[Membership]:
    if not object_ids:
        return []
    return list(
        (
            await session.exec(select(Membership).where(col(Membership.object_id).in_(object_ids)))
        ).all()
    )


async def list_instance_ids(session: AsyncSession, type_id: uuid.UUID) -> list[uuid.UUID]:
    return list(
        (
            await session.exec(select(Membership.object_id).where(Membership.type_id == type_id))
        ).all()
    )


def add_membership(
    session: AsyncSession, object_id: uuid.UUID, type_id: uuid.UUID, data: dict[str, Any] | None
) -> None:
    session.add(Membership(object_id=object_id, type_id=type_id, data=data))


async def delete_membership(session: AsyncSession, membership: Membership) -> None:
    await session.delete(membership)


async def list_signatures_of(session: AsyncSession, map_id: uuid.UUID) -> list[Signature]:
    return list((await session.exec(select(Signature).where(Signature.map_id == map_id))).all())


async def get_signature(session: AsyncSession, signature_id: uuid.UUID) -> Signature | None:
    return await session.get(Signature, signature_id)


async def list_map_ids_by_signature(
    session: AsyncSession, type_id: uuid.UUID, *, as_domain: bool
) -> list[uuid.UUID]:
    slot = col(Signature.domain_id) if as_domain else col(Signature.codomain_id)
    return list(
        (await session.exec(select(Signature.map_id).where(slot == type_id).distinct())).all()
    )


def add_signature(
    session: AsyncSession, map_id: uuid.UUID, domain_id: uuid.UUID, codomain_id: uuid.UUID
) -> Signature:
    signature = Signature(map_id=map_id, domain_id=domain_id, codomain_id=codomain_id)
    session.add(signature)
    return signature


async def delete_signature(session: AsyncSession, signature: Signature) -> None:
    await session.delete(signature)


async def list_filings_of(
    session: AsyncSession, object_ids: Sequence[uuid.UUID]
) -> list[SectionFiling]:
    if not object_ids:
        return []
    return list(
        (
            await session.exec(
                select(SectionFiling).where(col(SectionFiling.object_id).in_(object_ids))
            )
        ).all()
    )


async def list_filed_under(
    session: AsyncSession, section_ids: Sequence[uuid.UUID]
) -> list[SectionFiling]:
    if not section_ids:
        return []
    return list(
        (
            await session.exec(
                select(SectionFiling).where(col(SectionFiling.section_id).in_(section_ids))
            )
        ).all()
    )


async def list_section_ids(session: AsyncSession) -> list[uuid.UUID]:
    filed = select(SectionFiling.section_id)
    top = select(TopLevelObject.object_id)
    return list((await session.exec(union(filed, top))).scalars().all())  # type: ignore[call-overload]


def add_section_filing(session: AsyncSession, object_id: uuid.UUID, section_id: uuid.UUID) -> None:
    session.add(SectionFiling(object_id=object_id, section_id=section_id))
