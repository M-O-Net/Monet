"""Business logic for the objects domain: 404/400 translation and schema assembly.

Orchestrates repository.py calls; owns no SQL of its own.
"""

import uuid
from collections import defaultdict
from collections.abc import Sequence

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
    OperatorDisplayOut,
    OperatorDisplayUpdate,
    RelationCreate,
    RelationDisplayOut,
    RelationOut,
    RelationSlotOut,
    SectionNode,
)

# The contents tree walks membership relations, which are ordinary data — nothing stops a user
# creating "X is in X", or a longer cycle, through the normal relation form. A global visited
# set makes a cycle harmless; these two caps bound the walk even for a pathological dataset.
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
    """Assemble RelationOut for many relations in a fixed number of queries.

    Everything the rows need — both slot tables and every object they mention, operators
    included — is fetched in one query each and assembled from dicts, so the cost does not
    grow with the number of relations.
    """
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
            # Foreign keys make this unreachable; if it ever fires the database is
            # inconsistent, which is ours to answer for, not the caller's.
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

    # Membership relations come back as `sections`/`members` below rather than as rows in the
    # operand lists, where they would otherwise bury every specimen's actual mathematics. They
    # stay in as_operator, though: on the membership operator's own page they are the content.
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


# ── membership ───────────────────────────────────────────────────────────────


async def _membership_parents(
    session: AsyncSession, membership_ops: Sequence[uuid.UUID], object_ids: Sequence[uuid.UUID]
) -> defaultdict[uuid.UUID, list[uuid.UUID]]:
    """Map each member id to the sections it is filed under."""
    edges = await repository.list_membership_inputs(session, membership_ops, object_ids)
    parents: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    if not edges:
        return parents
    outputs = await repository.list_relation_outputs_for(
        session, [edge.relation_id for edge in edges]
    )
    section_of = {row.relation_id: row.object_id for row in outputs}
    for edge in edges:
        section_id = section_of.get(edge.relation_id)
        if section_id is not None:
            parents[edge.object_id].append(section_id)
    return parents


async def _membership_children(
    session: AsyncSession, membership_ops: Sequence[uuid.UUID], section_ids: Sequence[uuid.UUID]
) -> defaultdict[uuid.UUID, list[uuid.UUID]]:
    """Map each section id to the objects filed under it."""
    edges = await repository.list_membership_outputs(session, membership_ops, section_ids)
    children: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    if not edges:
        return children
    inputs = await repository.list_relation_inputs_for(
        session, [edge.relation_id for edge in edges]
    )
    member_of = {row.relation_id: row.object_id for row in inputs}
    for edge in edges:
        member_id = member_of.get(edge.relation_id)
        if member_id is not None:
            children[edge.object_id].append(member_id)
    return children


async def _objects_in_latex_order(
    session: AsyncSession, object_ids: Sequence[uuid.UUID]
) -> list[ObjectOut]:
    return [
        ObjectOut.model_validate(obj)
        for obj in await repository.list_objects_by_ids(session, object_ids)
    ]


async def get_contents(session: AsyncSession) -> list[SectionNode]:
    """Build the contents page: top-level sections, and the sections nested under them.

    Only members that are themselves sections become children — a section's specimens belong
    on its own page, so the contents stays a table of contents rather than a listing of the
    whole network. An object reachable from two places is filed under whichever section the
    walk reached first, and a pinned object always renders at the top level rather than as
    someone's child, since that is what pinning it meant.
    """
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


# ── operator display ─────────────────────────────────────────────────────────


async def get_operator_display(
    session: AsyncSession, operator_id: uuid.UUID
) -> OperatorDisplayOut:
    await get_object_or_404(session, operator_id)
    row = await repository.get_operator_display(session, operator_id)
    if row is None:
        # Unconfigured is a normal state, not a missing resource — every operator starts here,
        # and a 404 would make the editor open on an error for all of them.
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
