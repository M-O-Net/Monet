"""Business logic for the objects domain: 404/400 translation and schema assembly.

Orchestrates repository.py calls; owns no SQL of its own.
"""

import re
import uuid
from collections import defaultdict
from collections.abc import Sequence

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.objects import repository
from monet_api.objects.models import Object, Relation, RelationInput, RelationOutput
from monet_api.objects.schemas import (
    ObjectCreate,
    ObjectDetailOut,
    ObjectOut,
    ObjectUpdate,
    OperatorDisplayOut,
    OperatorDisplayUpdate,
    RelationAssert,
    RelationAssertOut,
    RelationCreate,
    RelationDisplayOut,
    RelationOut,
    RelationSlotOut,
    SectionNode,
)

MAX_SECTION_DEPTH = 6
MAX_SECTION_NODES = 500


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


async def _load_relations_out(
    session: AsyncSession, relations: Sequence[Relation]
) -> list[RelationOut]:
    if not relations:
        return []

    relation_ids = [relation.id for relation in relations]
    input_rows = await repository.list_relation_inputs_for(session, relation_ids)
    output_rows = await repository.list_relation_outputs_for(session, relation_ids)

    needed_ids = {relation.operator_id for relation in relations}
    needed_ids.update(input_row.object_id for input_row in input_rows)
    needed_ids.update(output_row.object_id for output_row in output_rows)
    objects = {obj.id: obj for obj in await repository.list_objects_by_ids(session, [*needed_ids])}
    displays = {
        row.operator_id: RelationDisplayOut.model_validate(row)
        for row in await repository.list_operator_displays(
            session, [relation.operator_id for relation in relations]
        )
    }

    def resolve(object_id: uuid.UUID) -> ObjectOut:
        obj = objects.get(object_id)
        if obj is None:
            raise HTTPException(status_code=500, detail="relation references a missing object")
        return ObjectOut.model_validate(obj)

    inputs_by_relation: defaultdict[uuid.UUID, list[RelationSlotOut]] = defaultdict(list)
    for input_row in input_rows:
        inputs_by_relation[input_row.relation_id].append(
            RelationSlotOut(position=input_row.position, object=resolve(input_row.object_id))
        )
    outputs_by_relation: defaultdict[uuid.UUID, list[RelationSlotOut]] = defaultdict(list)
    for output_row in output_rows:
        outputs_by_relation[output_row.relation_id].append(
            RelationSlotOut(position=output_row.position, object=resolve(output_row.object_id))
        )

    return [
        RelationOut(
            id=relation.id,
            operator=resolve(relation.operator_id),
            inputs=inputs_by_relation[relation.id],
            outputs=outputs_by_relation[relation.id],
            display=displays.get(relation.operator_id),
        )
        for relation in relations
    ]


async def _load_relation_out(session: AsyncSession, relation: Relation) -> RelationOut:
    return (await _load_relations_out(session, [relation]))[0]


async def list_objects(session: AsyncSession) -> list[Object]:
    return await repository.list_objects(session)


async def create_object(session: AsyncSession, body: ObjectCreate) -> Object:
    return await repository.create_object(session, body.latex, body.description)


async def get_object_detail(session: AsyncSession, object_id: uuid.UUID) -> ObjectDetailOut:
    obj = await get_object_or_404(session, object_id)
    membership_ops = await repository.list_membership_operator_ids(session)

    as_operator = await repository.list_relations_by_operator(session, object_id)
    as_input_ids = await repository.list_relation_ids_by_input(
        session, object_id, exclude_operator_ids=membership_ops
    )
    as_output_ids = await repository.list_relation_ids_by_output(
        session, object_id, exclude_operator_ids=membership_ops
    )

    as_input = await repository.list_relations_by_ids(session, as_input_ids)
    as_output = await repository.list_relations_by_ids(session, as_output_ids)

    parents = await _membership_parents(session, membership_ops, [object_id])
    children = await _membership_children(session, membership_ops, [object_id])

    is_top_level = await repository.get_top_level_object(session, object_id) is not None

    return ObjectDetailOut(
        id=obj.id,
        latex=obj.latex,
        description=obj.description,
        is_top_level=is_top_level,
        sections=await _objects_in_latex_order(session, parents.get(object_id, [])),
        members=await _objects_in_latex_order(session, children.get(object_id, [])),
        as_operator=await _load_relations_out(session, as_operator),
        as_input=await _load_relations_out(session, as_input),
        as_output=await _load_relations_out(session, as_output),
    )


async def _membership_parents(
    session: AsyncSession, membership_ops: Sequence[uuid.UUID], object_ids: Sequence[uuid.UUID]
) -> defaultdict[uuid.UUID, list[uuid.UUID]]:
    edges = await repository.list_membership_inputs(session, membership_ops, object_ids)
    parents: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    if not edges:
        return parents
    outputs = await repository.list_relation_outputs_for(
        session, [edge.relation_id for edge in edges]
    )
    sections_of: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    for row in outputs:
        sections_of[row.relation_id].append(row.object_id)
    for edge in edges:
        parents[edge.object_id].extend(sections_of[edge.relation_id])
    return parents


async def _membership_children(
    session: AsyncSession, membership_ops: Sequence[uuid.UUID], section_ids: Sequence[uuid.UUID]
) -> defaultdict[uuid.UUID, list[uuid.UUID]]:
    edges = await repository.list_membership_outputs(session, membership_ops, section_ids)
    children: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    if not edges:
        return children
    inputs = await repository.list_relation_inputs_for(
        session, [edge.relation_id for edge in edges]
    )
    members_of: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    for row in inputs:
        members_of[row.relation_id].append(row.object_id)
    for edge in edges:
        children[edge.object_id].extend(members_of[edge.relation_id])
    return children


async def _objects_in_latex_order(
    session: AsyncSession, object_ids: Sequence[uuid.UUID]
) -> list[ObjectOut]:
    return [
        ObjectOut.model_validate(obj)
        for obj in await repository.list_objects_by_ids(session, object_ids)
    ]


async def get_contents(session: AsyncSession) -> list[SectionNode]:
    membership_ops = await repository.list_membership_operator_ids(session)
    roots = await repository.list_top_level_objects(session)

    children_of: dict[uuid.UUID, list[uuid.UUID]] = {}
    parent_of: dict[uuid.UUID, uuid.UUID] = {}
    visited = {root.id for root in roots}
    frontier = [root.id for root in roots]

    for _ in range(MAX_SECTION_DEPTH):
        if not frontier or len(visited) > MAX_SECTION_NODES:
            break
        found = await _membership_children(session, membership_ops, frontier)
        next_frontier: list[uuid.UUID] = []
        for section_id in frontier:
            members = found.get(section_id, [])
            children_of[section_id] = members
            for member_id in members:
                if member_id not in visited:
                    visited.add(member_id)
                    parent_of[member_id] = section_id
                    next_frontier.append(member_id)
        frontier = next_frontier

    known = {obj.id: obj for obj in await repository.list_objects_by_ids(session, [*visited])}
    rank = {object_id: index for index, object_id in enumerate(known)}

    def build(object_id: uuid.UUID) -> SectionNode:
        obj = known[object_id]
        members = children_of.get(object_id, [])
        nested = [
            member_id
            for member_id in members
            if parent_of.get(member_id) == object_id and children_of.get(member_id)
        ]
        nested.sort(key=lambda member_id: rank.get(member_id, 0))
        return SectionNode(
            id=obj.id,
            latex=obj.latex,
            description=obj.description,
            member_count=len(members),
            children=[build(member_id) for member_id in nested],
        )

    return [build(root.id) for root in roots]


async def get_operator_display(session: AsyncSession, operator_id: uuid.UUID) -> OperatorDisplayOut:
    await get_object_or_404(session, operator_id)
    row = await repository.get_operator_display(session, operator_id)
    if row is None:
        return OperatorDisplayOut(
            operator_id=operator_id, template=None, hidden_by_default=False, is_membership=False
        )
    return OperatorDisplayOut.model_validate(row)


async def set_operator_display(
    session: AsyncSession, operator_id: uuid.UUID, body: OperatorDisplayUpdate
) -> OperatorDisplayOut:
    await get_object_or_404(session, operator_id)
    row = await repository.upsert_operator_display(
        session, operator_id, body.template, body.hidden_by_default, body.is_membership
    )
    return OperatorDisplayOut.model_validate(row)


async def update_object(session: AsyncSession, object_id: uuid.UUID, body: ObjectUpdate) -> Object:
    obj = await get_object_or_404(session, object_id)
    return await repository.update_object(session, obj, body.latex, body.description)


async def delete_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    obj = await get_object_or_404(session, object_id)
    await repository.delete_relations_referencing_object(session, object_id)
    await repository.delete_object(session, obj)


async def list_top_level_objects(session: AsyncSession) -> list[Object]:
    return await repository.list_top_level_objects(session)


async def mark_top_level_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    await get_object_or_404(session, object_id)
    if await repository.get_top_level_object(session, object_id) is None:
        await repository.add_top_level_object(session, object_id)


async def unmark_top_level_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    row = await repository.get_top_level_object(session, object_id)
    if row is not None:
        await repository.delete_top_level_object(session, row)


async def list_relations(session: AsyncSession) -> list[RelationOut]:
    return await _load_relations_out(session, await repository.list_relations(session))


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


_TEXT_GROUP = re.compile(r"\\text\{[^{}]*\}")


def _without_whitespace(latex: str) -> str:
    return "".join(latex.split())


def _with_whitespace_collapsed(latex: str) -> str:
    return " ".join(latex.split())


def normalize_latex(latex: str) -> str:
    parts: list[str] = []
    last = 0
    for match in _TEXT_GROUP.finditer(latex):
        parts.append(_without_whitespace(latex[last : match.start()]))
        parts.append(_with_whitespace_collapsed(match.group()))
        last = match.end()
    parts.append(_without_whitespace(latex[last:]))
    return "".join(parts)


async def _find_or_create_object(
    session: AsyncSession, latex: str, existing: list[Object]
) -> tuple[Object, bool]:
    key = normalize_latex(latex)
    for obj in existing:
        if normalize_latex(obj.latex) == key:
            return obj, False
    obj = await repository.add_object(session, latex, None)
    existing.append(obj)
    return obj, True


def _operands_by_relation(
    rows: Sequence[RelationInput] | Sequence[RelationOutput],
) -> defaultdict[uuid.UUID, list[uuid.UUID]]:
    operands: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    for row in rows:
        operands[row.relation_id].append(row.object_id)
    return operands


async def _find_matching_relation(
    session: AsyncSession,
    operator_id: uuid.UUID,
    input_ids: list[uuid.UUID],
    output_ids: list[uuid.UUID],
) -> Relation | None:
    candidates = await repository.list_relations_by_operator(session, operator_id)
    if not candidates:
        return None
    candidate_ids = [candidate.id for candidate in candidates]
    operands_in = _operands_by_relation(
        await repository.list_relation_inputs_for(session, candidate_ids)
    )
    operands_out = _operands_by_relation(
        await repository.list_relation_outputs_for(session, candidate_ids)
    )
    for candidate in candidates:
        if operands_in[candidate.id] == input_ids and operands_out[candidate.id] == output_ids:
            return candidate
    return None


async def assert_relation(session: AsyncSession, body: RelationAssert) -> RelationAssertOut:
    if not body.output_latex:
        raise HTTPException(status_code=400, detail="a relation needs at least one output")

    await get_object_or_404(session, body.operator_id)
    for oid in body.input_object_ids:
        await get_object_or_404(session, oid)

    existing = await repository.list_objects(session)
    outputs: list[Object] = []
    created_object_ids: list[uuid.UUID] = []
    for latex in body.output_latex:
        obj, was_created = await _find_or_create_object(session, latex, existing)
        outputs.append(obj)
        if was_created:
            created_object_ids.append(obj.id)

    output_ids = [obj.id for obj in outputs]
    relation = await _find_matching_relation(
        session, body.operator_id, body.input_object_ids, output_ids
    )
    created_relation = relation is None
    if relation is None:
        relation = await repository.create_relation(session, body.operator_id)
        for position, oid in enumerate(body.input_object_ids):
            repository.add_relation_input(session, relation.id, oid, position)
        for position, oid in enumerate(output_ids):
            repository.add_relation_output(session, relation.id, oid, position)

    await session.commit()
    await session.refresh(relation)
    return RelationAssertOut(
        relation=await _load_relation_out(session, relation),
        created_object_ids=created_object_ids,
        created_relation=created_relation,
    )
