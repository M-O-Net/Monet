"""Business logic for the objects domain: 404/400 translation and schema assembly.

Orchestrates repository.py calls; owns no SQL of its own.
"""

import datetime
import json
import re
import uuid
from collections import defaultdict
from collections.abc import Sequence
from typing import Any, Literal

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments import repository as comments
from monet_api.events import repository as events
from monet_api.events.models import Event
from monet_api.implementations import repository as implementations
from monet_api.objects import repository
from monet_api.objects.models import Object, Relation, RelationInput, RelationOutput
from monet_api.objects.schemas import (
    ComputedOutput,
    ObjectCreate,
    ObjectDetailOut,
    ObjectOut,
    ObjectReferenceIn,
    ObjectReferenceOut,
    ObjectRole,
    ObjectUpdate,
    OperatorDisplayOut,
    OperatorDisplayUpdate,
    ProvenanceOut,
    RelationAssert,
    RelationAssertOut,
    RelationCreate,
    RelationDisplayOut,
    RelationOut,
    RelationSlotOut,
    SectionNode,
    SignatureOut,
)

MAX_SECTION_DEPTH = 6
MAX_SECTION_NODES = 500
MAX_QUERY_RESULTS = 500


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


async def load_relations(session: AsyncSession, relations: Sequence[Relation]) -> list[RelationOut]:
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
    provenance = await _provenance(session, "relation_created", relation_ids)

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
            provenance=provenance.get(relation.id),
        )
        for relation in relations
    ]


async def _provenance(
    session: AsyncSession, kind: str, subject_ids: Sequence[uuid.UUID]
) -> dict[uuid.UUID, ProvenanceOut]:
    found: dict[uuid.UUID, ProvenanceOut] = {}
    for event in sorted(await events.list_events_for(session, kind, subject_ids), key=_when):
        found.setdefault(event.subject_id, ProvenanceOut.model_validate(event))
    return found


def _when(event: Event) -> datetime.datetime:
    return event.at


async def _load_relation_out(session: AsyncSession, relation: Relation) -> RelationOut:
    return (await load_relations(session, [relation]))[0]


async def list_objects(session: AsyncSession) -> list[Object]:
    return await repository.list_objects(session)


_LINKABLE_URL = re.compile(r"^(?:https?://|/(?!/))")


def _linkable(url: str | None) -> str | None:
    """Return url if it is safe to place in an href or src, else raise 400.

    Monet has no auth, so a `javascript:` URL saved by one visitor would run for every later
    one. A leading `//` is rejected too: it is protocol-relative, not site-relative.
    """
    if url is None:
        return None
    candidate = url.strip()
    if not candidate:
        return None
    if not _LINKABLE_URL.match(candidate):
        raise HTTPException(
            status_code=400, detail="url must start with http://, https:// or a single /"
        )
    return candidate


async def _replace_references(
    session: AsyncSession, object_id: uuid.UUID, references: Sequence[ObjectReferenceIn]
) -> None:
    await repository.clear_object_references(session, object_id)
    for position, reference in enumerate(references):
        url = _linkable(reference.url)
        if url is None:
            continue
        repository.add_object_reference(session, object_id, reference.label.strip(), url, position)


async def _refuse_duplicate_data(
    session: AsyncSession, data: dict[str, Any] | None, own_id: uuid.UUID | None = None
) -> None:
    if data is None:
        return
    existing = await repository.find_object_by_data(session, data)
    if existing is not None and existing.id != own_id:
        raise HTTPException(status_code=409, detail=f"object {existing.id} already holds this data")


def _structural_operator(flagged: Sequence[uuid.UUID], name: str) -> uuid.UUID:
    if not flagged:
        raise HTTPException(status_code=400, detail=f"no {name} operator is configured")
    return sorted(flagged)[0]


async def _relate(
    session: AsyncSession,
    operator_id: uuid.UUID,
    inputs: Sequence[uuid.UUID],
    outputs: Sequence[uuid.UUID],
) -> None:
    for oid in [*inputs, *outputs]:
        await get_object_or_404(session, oid)
    relation = await repository.create_relation(session, operator_id)
    for position, oid in enumerate(inputs):
        repository.add_relation_input(session, relation.id, oid, position)
    for position, oid in enumerate(outputs):
        repository.add_relation_output(session, relation.id, oid, position)


async def create_object(session: AsyncSession, body: ObjectCreate) -> Object:
    await _refuse_duplicate_data(session, body.data)
    obj = await repository.add_object(
        session, body.latex, body.description, _linkable(body.image_url), body.data
    )
    await _replace_references(session, obj.id, body.references)
    if body.member_of:
        element_of = _structural_operator(
            await repository.list_membership_operator_ids(session), "membership"
        )
        for type_id in body.member_of:
            await _relate(session, element_of, [obj.id], [type_id])
    if body.subtype_of:
        subset_of = _structural_operator(
            await repository.list_subtype_operator_ids(session), "subtype"
        )
        for type_id in body.subtype_of:
            await _relate(session, subset_of, [obj.id], [type_id])
    if body.signature is not None:
        signature_of = _structural_operator(
            await repository.list_signature_operator_ids(session), "signature"
        )
        await _relate(
            session, signature_of, [obj.id], [body.signature.domain_id, body.signature.codomain_id]
        )
    events.add_event(session, "object_created", obj.id, body.contributor, "manual")
    await session.commit()
    await session.refresh(obj)
    return obj


async def get_object_detail(session: AsyncSession, object_id: uuid.UUID) -> ObjectDetailOut:
    obj = await get_object_or_404(session, object_id)
    membership_ops = await repository.list_membership_operator_ids(session)
    subtype_ops = await repository.list_subtype_operator_ids(session)
    signature_ops = await repository.list_signature_operator_ids(session)
    structural_ops = [*membership_ops, *subtype_ops, *signature_ops]

    as_operator = await repository.list_relations_by_operator(session, object_id)
    as_input_ids = await repository.list_relation_ids_by_input(
        session, object_id, exclude_operator_ids=structural_ops
    )
    as_output_ids = await repository.list_relation_ids_by_output(
        session, object_id, exclude_operator_ids=structural_ops
    )

    as_input = await repository.list_relations_by_ids(session, as_input_ids)
    as_output = await repository.list_relations_by_ids(session, as_output_ids)

    parents = await _membership_parents(session, membership_ops, [object_id])
    children = await _membership_children(session, membership_ops, [object_id])

    is_top_level = await repository.get_top_level_object(session, object_id) is not None

    references = await repository.list_object_references(session, object_id)

    subtype_ids = await repository.list_related_types(
        session, subtype_ops, object_id, "down", transitive=False
    )
    supertype_ids = await repository.list_related_types(
        session, subtype_ops, object_id, "up", transitive=False
    )
    members = children.get(object_id, [])
    signature = await _signature_of(session, signature_ops, object_id)

    role: ObjectRole = "instance"
    if (
        as_operator
        or signature is not None
        or await implementations.has_implementation(session, object_id)
    ):
        role = "map"
    elif subtype_ids or supertype_ids:
        role = "type"
    elif members:
        role = "section"

    maps_from = await repository.list_maps_with_signature_slot(session, signature_ops, object_id, 0)
    maps_to = await repository.list_maps_with_signature_slot(session, signature_ops, object_id, 1)
    provenance = await _provenance(session, "object_created", [object_id])

    return ObjectDetailOut(
        id=obj.id,
        latex=obj.latex,
        description=obj.description,
        image_url=obj.image_url,
        data=obj.data,
        role=role,
        provenance=provenance.get(object_id),
        subtypes=await _objects_in_latex_order(session, subtype_ids),
        supertypes=await _objects_in_latex_order(session, supertype_ids),
        signature=signature,
        maps_from=await _objects_in_latex_order(session, maps_from),
        maps_to=await _objects_in_latex_order(session, maps_to),
        references=[ObjectReferenceOut.model_validate(row) for row in references],
        is_top_level=is_top_level,
        sections=await _objects_in_latex_order(session, parents.get(object_id, [])),
        members=await _objects_in_latex_order(session, members),
        as_operator=await load_relations(session, as_operator),
        as_input=await load_relations(session, as_input),
        as_output=await load_relations(session, as_output),
    )


async def _signature_of(
    session: AsyncSession, signature_ops: Sequence[uuid.UUID], map_id: uuid.UUID
) -> SignatureOut | None:
    slots = await repository.list_signature_slots(session, signature_ops, map_id)
    if not slots:
        return None
    first = [slot.object_id for slot in slots if slot.relation_id == slots[0].relation_id]
    if len(first) != 2:
        return None
    found = {obj.id: obj for obj in await repository.list_objects_by_ids(session, first)}
    return SignatureOut(
        domain=ObjectOut.model_validate(found[first[0]]),
        codomain=ObjectOut.model_validate(found[first[1]]),
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
            operator_id=operator_id,
            template=None,
            hidden_by_default=False,
            is_membership=False,
            is_subtype=False,
            is_signature=False,
        )
    return OperatorDisplayOut.model_validate(row)


async def set_operator_display(
    session: AsyncSession, operator_id: uuid.UUID, body: OperatorDisplayUpdate
) -> OperatorDisplayOut:
    await get_object_or_404(session, operator_id)
    row = await repository.upsert_operator_display(
        session,
        operator_id,
        body.template,
        body.hidden_by_default,
        body.is_membership,
        body.is_subtype,
        body.is_signature,
    )
    return OperatorDisplayOut.model_validate(row)


async def update_object(session: AsyncSession, object_id: uuid.UUID, body: ObjectUpdate) -> Object:
    obj = await get_object_or_404(session, object_id)
    await _refuse_duplicate_data(session, body.data, object_id)
    image_url = _linkable(body.image_url)
    await _replace_references(session, object_id, body.references)
    return await repository.update_object(
        session, obj, body.latex, body.description, image_url, body.data
    )


async def delete_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    obj = await get_object_or_404(session, object_id)
    touching = await repository.list_relation_ids_touching(session, object_id)
    remarks = [comment.id for comment in await comments.list_comments_for(session, object_id)]
    await events.delete_events_for(session, [object_id, *touching, *remarks])
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
    return await load_relations(session, await repository.list_relations(session))


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
    events.add_event(session, "relation_created", relation.id, body.contributor, "manual")

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
    await events.delete_events_for(session, [relation_id])
    await repository.delete_relation(session, relation)


async def _find_or_create_output(
    session: AsyncSession, output: ComputedOutput
) -> tuple[Object, bool]:
    if output.data is not None:
        existing = await repository.find_object_by_data(session, output.data)
        if existing is not None:
            return existing, False
    return await repository.add_object(session, output.latex, None, data=output.data), True


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
    if not body.outputs:
        raise HTTPException(status_code=400, detail="a relation needs at least one output")

    await get_object_or_404(session, body.operator_id)
    for oid in body.input_object_ids:
        await get_object_or_404(session, oid)

    source = (
        "computed" if body.implementation_id is None else f"implementation:{body.implementation_id}"
    )
    outputs: list[Object] = []
    created_object_ids: list[uuid.UUID] = []
    for output in body.outputs:
        obj, was_created = await _find_or_create_output(session, output)
        outputs.append(obj)
        if was_created:
            created_object_ids.append(obj.id)
            events.add_event(session, "object_created", obj.id, body.contributor, source)

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
        events.add_event(session, "relation_created", relation.id, body.contributor, source)

    await session.commit()
    await session.refresh(relation)
    return RelationAssertOut(
        relation=await _load_relation_out(session, relation),
        created_object_ids=created_object_ids,
        created_relation=created_relation,
    )


def _json_object(name: str, raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=400, detail=f"{name} is not valid JSON") from error
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail=f"{name} must be a JSON object")
    return parsed


def _property_filter(raw: str) -> tuple[uuid.UUID, uuid.UUID]:
    operator, _, output = raw.partition(":")
    try:
        return uuid.UUID(operator), uuid.UUID(output)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail="where must be <operator id>:<output object id>"
        ) from error


async def query_objects(
    session: AsyncSession,
    *,
    member_of: uuid.UUID | None,
    transitive: bool,
    data_equals: str | None,
    data_contains: str | None,
    description_contains: str | None,
    where: Sequence[str],
) -> list[Object]:
    types: list[uuid.UUID] | None = None
    if member_of is not None:
        await get_object_or_404(session, member_of)
        types = [member_of]
        if transitive:
            subtype_ops = await repository.list_subtype_operator_ids(session)
            types += await repository.list_related_types(
                session, subtype_ops, member_of, "down", transitive=True
            )
    return await repository.query_objects(
        session,
        membership_ops=await repository.list_membership_operator_ids(session),
        member_of=types,
        data_equals=_json_object("data_equals", data_equals),
        data_contains=_json_object("data_contains", data_contains),
        description_contains=(description_contains or "").strip() or None,
        where=[_property_filter(raw) for raw in where],
        limit=MAX_QUERY_RESULTS,
    )


async def list_related_types(
    session: AsyncSession,
    type_id: uuid.UUID,
    direction: Literal["down", "up"],
    *,
    transitive: bool,
) -> list[ObjectOut]:
    await get_object_or_404(session, type_id)
    subtype_ops = await repository.list_subtype_operator_ids(session)
    found = await repository.list_related_types(
        session, subtype_ops, type_id, direction, transitive=transitive
    )
    return await _objects_in_latex_order(session, found)


async def list_types(session: AsyncSession) -> list[ObjectOut]:
    subtype_ops = await repository.list_subtype_operator_ids(session)
    return await _objects_in_latex_order(
        session, await repository.list_type_ids(session, subtype_ops)
    )
