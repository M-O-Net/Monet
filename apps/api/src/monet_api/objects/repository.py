"""Raw SQLModel queries for the objects domain. No business logic, no 404s — see service.py."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, NamedTuple

from sqlalchemy import (
    ColumnElement,
    SQLColumnExpression,
    Subquery,
    case,
    distinct,
    func,
    or_,
    union,
    union_all,
)
from sqlalchemy import select as select_columns
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
    RelationReference,
    SectionFiling,
    Signature,
    Subtype,
    TopLevelObject,
    Type,
)


async def get_object(session: AsyncSession, object_id: uuid.UUID) -> Object | None:
    return await session.get(Object, object_id)


Role = Literal["type", "map", "section", "instance"]
Side = Literal["operator", "input", "output"]


@dataclass(frozen=True)
class ObjectFilter:
    member_of: Sequence[uuid.UUID] | None = None
    filed_under: uuid.UUID | None = None
    role: Role | None = None
    implemented: Sequence[uuid.UUID] = ()
    data_equals: dict[str, Any] | None = None
    data_contains: dict[str, Any] | None = None
    description_contains: str | None = None
    where: Sequence[tuple[uuid.UUID, uuid.UUID]] = ()
    search: str | None = None


def _search_key(text: SQLColumnExpression[str]) -> ColumnElement[str]:
    without_macros = func.regexp_replace(text, r"\\[a-zA-Z]+", " ", "g")
    ungrouped = func.regexp_replace(without_macros, "[{}$]", "", "g")
    return func.lower(func.btrim(func.regexp_replace(ungrouped, r"[\s,&\\]+", " ", "g")))


def _like_escaped(text: str) -> str:
    return text.replace("%", r"\%").replace("_", r"\_")


def _search_rank(needle: str) -> ColumnElement[int]:
    exact = _like_escaped(needle)

    def rank(key: ColumnElement[str]) -> ColumnElement[int]:
        return case(
            (key.like(f"{exact}%"), 0),
            (key.like(f"% {exact}%"), 1),
            (key.like(f"%{exact}%"), 2),
            else_=3,
        )

    keys = (_search_key(col(Object.latex)), _search_key(func.coalesce(col(Object.description), "")))
    return func.least(*(rank(key) for key in keys))


def _matches_search(needle: str) -> ColumnElement[bool]:
    scattered = "%" + "%".join(_like_escaped(character) for character in needle) + "%"
    return or_(
        _search_key(col(Object.latex)).like(scattered),
        _search_key(func.coalesce(col(Object.description), "")).like(scattered),
    )


def _has_role(role: Role, implemented: Sequence[uuid.UUID]) -> ColumnElement[bool]:
    object_id = col(Object.id)
    if role == "type":
        return object_id.in_(select(Type.object_id))
    if role == "instance":
        return object_id.in_(select(Membership.object_id))
    if role == "section":
        return or_(
            object_id.in_(select(SectionFiling.section_id)),
            object_id.in_(select(TopLevelObject.object_id)),
        )
    return or_(
        object_id.in_(select(Relation.operator_id)),
        object_id.in_(select(Signature.map_id)),
        object_id.in_(implemented),
    )


def _conditions(found: ObjectFilter) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if found.description_contains is not None:
        conditions.append(
            col(Object.description).icontains(found.description_contains, autoescape=True)
        )
    if (
        found.member_of is not None
        or found.data_equals is not None
        or found.data_contains is not None
    ):
        facets = select(Membership.object_id)
        if found.member_of is not None:
            facets = facets.where(col(Membership.type_id).in_(found.member_of))
        if found.data_equals is not None:
            facets = facets.where(col(Membership.data) == found.data_equals)
        if found.data_contains is not None:
            facets = facets.where(col(Membership.data).contains(found.data_contains))
        conditions.append(col(Object.id).in_(facets))
    if found.filed_under is not None:
        filed = select(SectionFiling.object_id).where(SectionFiling.section_id == found.filed_under)
        conditions.append(col(Object.id).in_(filed))
    if found.role is not None:
        conditions.append(_has_role(found.role, found.implemented))
    conditions.extend(
        col(Object.id).in_(
            _inputs_mapped_to([operator_id], col(RelationOutput.object_id) == output_id)
        )
        for operator_id, output_id in found.where
    )
    if found.search is not None:
        conditions.append(_matches_search(found.search))
    return conditions


async def page_objects(
    session: AsyncSession, found: ObjectFilter, *, offset: int, limit: int
) -> tuple[list[Object], int]:
    query = select(Object, func.count().over()).where(*_conditions(found))
    if found.search is not None:
        query = query.order_by(
            _search_rank(found.search), func.length(_search_key(col(Object.latex)))
        )
    query = query.order_by(col(Object.latex), col(Object.id)).offset(offset).limit(limit)
    rows = (await session.exec(query)).all()
    if rows:
        return [obj for obj, _ in rows], rows[0][1]
    return [], await count_objects(session, found) if offset else 0


async def count_objects(session: AsyncSession, found: ObjectFilter) -> int:
    query = select(func.count()).select_from(Object).where(*_conditions(found))
    return (await session.exec(query)).one()


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


async def list_relations_by_ids(
    session: AsyncSession, relation_ids: Sequence[uuid.UUID]
) -> list[Relation]:
    if not relation_ids:
        return []
    return list(
        (await session.exec(select(Relation).where(col(Relation.id).in_(relation_ids)))).all()
    )


async def list_relations_matching(
    session: AsyncSession, operator_id: uuid.UUID, first_input: uuid.UUID | None
) -> list[Relation]:
    query = select(Relation).where(Relation.operator_id == operator_id)
    if first_input is not None:
        query = query.where(
            col(Relation.id).in_(
                select(RelationInput.relation_id)
                .where(RelationInput.object_id == first_input)
                .where(RelationInput.position == 0)
            )
        )
    return list((await session.exec(query)).all())


def _touching(side: Side, object_ids: Sequence[uuid.UUID]) -> Subquery:
    if side == "operator":
        return (
            select(
                col(Relation.operator_id).label("object_id"), col(Relation.id).label("relation_id")
            )
            .where(col(Relation.operator_id).in_(object_ids))
            .subquery()
        )
    slot = RelationInput if side == "input" else RelationOutput
    return (
        select(col(slot.object_id).label("object_id"), col(slot.relation_id).label("relation_id"))
        .where(col(slot.object_id).in_(object_ids))
        .distinct()
        .subquery()
    )


class RelationSample(NamedTuple):
    object_id: uuid.UUID
    operator_id: uuid.UUID
    relation_id: uuid.UUID
    group_size: int


async def sample_relations(
    session: AsyncSession, object_ids: Sequence[uuid.UUID], side: Side, per_operator: int
) -> list[RelationSample]:
    if not object_ids:
        return []
    touching = _touching(side, object_ids)
    group = (touching.c.object_id, col(Relation.operator_id))
    ranked = (
        select_columns(
            touching.c.object_id,
            col(Relation.operator_id),
            col(Relation.id),
            func.row_number().over(partition_by=group, order_by=col(Relation.id)).label("rank"),
            func.count().over(partition_by=group).label("total"),
        )
        .join(Relation, col(Relation.id) == touching.c.relation_id)
        .subquery()
    )
    query = (
        select(ranked.c.object_id, ranked.c.operator_id, ranked.c.id, ranked.c.total)
        .where(ranked.c.rank <= per_operator)
        .order_by(ranked.c.object_id, ranked.c.operator_id, ranked.c.id)
    )
    return [RelationSample(*row) for row in (await session.exec(query)).all()]


def _relations_on_side(
    object_id: uuid.UUID, side: Side, operator_id: uuid.UUID | None
) -> list[ColumnElement[bool]]:
    touching = _touching(side, [object_id])
    conditions: list[ColumnElement[bool]] = [col(Relation.id).in_(select(touching.c.relation_id))]
    if operator_id is not None:
        conditions.append(col(Relation.operator_id) == operator_id)
    return conditions


async def list_relations_on_side(
    session: AsyncSession,
    object_id: uuid.UUID,
    side: Side,
    operator_id: uuid.UUID | None,
    *,
    offset: int,
    limit: int,
) -> list[Relation]:
    query = (
        select(Relation)
        .where(*_relations_on_side(object_id, side, operator_id))
        .order_by(col(Relation.id))
        .offset(offset)
        .limit(limit)
    )
    return list((await session.exec(query)).all())


async def count_relations_on_side(
    session: AsyncSession, object_id: uuid.UUID, side: Side, operator_id: uuid.UUID | None
) -> int:
    query = (
        select(func.count())
        .select_from(Relation)
        .where(*_relations_on_side(object_id, side, operator_id))
    )
    return (await session.exec(query)).one()


async def count_relations_touching(session: AsyncSession, object_ids: Sequence[uuid.UUID]) -> int:
    sides: tuple[Side, ...] = ("operator", "input", "output")
    touching = union(*(select(_touching(side, object_ids).c.relation_id) for side in sides))
    return (await session.exec(select(func.count()).select_from(touching.subquery()))).one()


class Step(NamedTuple):
    relation_id: uuid.UUID
    source: uuid.UUID
    target: uuid.UUID


async def list_steps_from(session: AsyncSession, source_ids: Sequence[uuid.UUID]) -> list[Step]:
    if not source_ids:
        return []
    query = (
        select(RelationInput.relation_id, RelationInput.object_id, RelationOutput.object_id)
        .join(RelationOutput, col(RelationOutput.relation_id) == col(RelationInput.relation_id))
        .where(col(RelationInput.object_id).in_(source_ids))
        .distinct()
        .order_by(col(RelationInput.relation_id), col(RelationOutput.object_id))
    )
    return [Step(*row) for row in (await session.exec(query)).all()]


async def list_busiest_objects(session: AsyncSession, limit: int) -> list[uuid.UUID]:
    slots = union_all(
        select(col(RelationInput.object_id).label("object_id")),
        select(col(RelationOutput.object_id).label("object_id")),
    ).subquery()
    query = (
        select(slots.c.object_id)
        .group_by(slots.c.object_id)
        .order_by(func.count().desc(), slots.c.object_id)
        .limit(limit)
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


async def list_relation_references_for(
    session: AsyncSession, relation_ids: Sequence[uuid.UUID]
) -> list[RelationReference]:
    if not relation_ids:
        return []
    return list(
        (
            await session.exec(
                select(RelationReference)
                .where(col(RelationReference.relation_id).in_(relation_ids))
                .order_by(col(RelationReference.relation_id), col(RelationReference.position))
            )
        ).all()
    )


async def clear_relation_references(session: AsyncSession, relation_id: uuid.UUID) -> None:
    await session.exec(
        delete(RelationReference).where(col(RelationReference.relation_id) == relation_id)
    )


def add_relation_reference(
    session: AsyncSession, relation_id: uuid.UUID, label: str, url: str, position: int
) -> None:
    session.add(RelationReference(relation_id=relation_id, label=label, url=url, position=position))


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


async def list_type_ids(session: AsyncSession, object_ids: Sequence[uuid.UUID]) -> list[uuid.UUID]:
    if not object_ids:
        return []
    query = select(Type.object_id).where(col(Type.object_id).in_(object_ids))
    return list((await session.exec(query)).all())


async def list_data_kinds(session: AsyncSession, type_ids: Sequence[uuid.UUID]) -> list[str]:
    query = (
        select(Type.data_kind)
        .where(col(Type.object_id).in_(type_ids))
        .where(col(Type.data_kind).is_not(None))
        .distinct()
        .order_by(col(Type.data_kind))
    )
    return [kind for kind in (await session.exec(query)).all() if kind is not None]


async def count_instances_below(
    session: AsyncSession, type_ids: Sequence[uuid.UUID]
) -> dict[uuid.UUID, int]:
    if not type_ids:
        return {}
    below = (
        select(col(Type.object_id).label("root"), col(Type.object_id).label("type_id"))
        .where(col(Type.object_id).in_(type_ids))
        .cte(recursive=True)
    )
    below = below.union(
        select(below.c.root, col(Subtype.type_id)).join(
            below, col(Subtype.supertype_id) == below.c.type_id
        )
    )
    query = (
        select(below.c.root, func.count(distinct(col(Membership.object_id))))
        .join(Membership, col(Membership.type_id) == below.c.type_id)
        .group_by(below.c.root)
    )
    return dict((await session.exec(query)).all())


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


async def list_filed_sections_and_types(
    session: AsyncSession, section_ids: Sequence[uuid.UUID]
) -> list[SectionFiling]:
    if not section_ids:
        return []
    filed = col(SectionFiling.object_id)
    query = (
        select(SectionFiling)
        .where(col(SectionFiling.section_id).in_(section_ids))
        .where(or_(filed.in_(select(Type.object_id)), filed.in_(select(SectionFiling.section_id))))
    )
    return list((await session.exec(query)).all())


async def count_filed_under(
    session: AsyncSession, section_ids: Sequence[uuid.UUID]
) -> dict[uuid.UUID, int]:
    query = (
        select(SectionFiling.section_id, func.count())
        .where(col(SectionFiling.section_id).in_(section_ids))
        .group_by(col(SectionFiling.section_id))
    )
    return dict((await session.exec(query)).all())


def add_section_filing(session: AsyncSession, object_id: uuid.UUID, section_id: uuid.UUID) -> None:
    session.add(SectionFiling(object_id=object_id, section_id=section_id))
