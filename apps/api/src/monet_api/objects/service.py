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
from monet_api.objects.models import Object, Relation, RelationInput, RelationOutput, Type
from monet_api.objects.schemas import (
    ComputedOutput,
    FacetData,
    FacetDetailOut,
    FacetOut,
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
    SignatureIn,
    SignatureOut,
    TypeOut,
)

MAX_SECTION_DEPTH = 6
MAX_SECTION_NODES = 500
MAX_QUERY_RESULTS = 500


async def get_object_or_404(session: AsyncSession, object_id: uuid.UUID) -> Object:
    obj = await repository.get_object(session, object_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="object not found")
    return obj


async def get_type_or_404(session: AsyncSession, type_id: uuid.UUID) -> Type:
    found = await repository.get_type(session, type_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"{type_id} is not a type")
    return found


async def get_relation_or_404(session: AsyncSession, relation_id: uuid.UUID) -> Relation:
    relation = await repository.get_relation(session, relation_id)
    if relation is None:
        raise HTTPException(status_code=404, detail="relation not found")
    return relation


async def objects_out(session: AsyncSession, objs: Sequence[Object]) -> list[ObjectOut]:
    facets: defaultdict[uuid.UUID, list[FacetOut]] = defaultdict(list)
    for membership in await repository.list_memberships_for(session, [obj.id for obj in objs]):
        facets[membership.object_id].append(FacetOut.model_validate(membership))
    return [
        ObjectOut(id=obj.id, latex=obj.latex, description=obj.description, facets=facets[obj.id])
        for obj in objs
    ]


async def _objects_out_by_ids(
    session: AsyncSession, object_ids: Sequence[uuid.UUID]
) -> list[ObjectOut]:
    return await objects_out(session, await repository.list_objects_by_ids(session, object_ids))


async def load_relations(session: AsyncSession, relations: Sequence[Relation]) -> list[RelationOut]:
    if not relations:
        return []

    relation_ids = [relation.id for relation in relations]
    input_rows = await repository.list_relation_inputs_for(session, relation_ids)
    output_rows = await repository.list_relation_outputs_for(session, relation_ids)

    needed_ids = {relation.operator_id for relation in relations}
    needed_ids.update(input_row.object_id for input_row in input_rows)
    needed_ids.update(output_row.object_id for output_row in output_rows)
    objects = {obj.id: obj for obj in await _objects_out_by_ids(session, [*needed_ids])}
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
        return obj

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


async def list_objects(session: AsyncSession) -> list[ObjectOut]:
    return await objects_out(session, await repository.list_objects(session))


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


def _kind_of(data: dict[str, Any]) -> str:
    if len(data) != 1:
        raise HTTPException(
            status_code=400, detail="data must have exactly one top-level key, naming its kind"
        )
    return next(iter(data))


async def _check_facet(
    session: AsyncSession,
    object_id: uuid.UUID | None,
    type_id: uuid.UUID,
    data: dict[str, Any] | None,
) -> None:
    held_as = await get_type_or_404(session, type_id)
    if data is None:
        return
    kind = _kind_of(data)
    if held_as.data_kind is not None and kind != held_as.data_kind:
        raise HTTPException(
            status_code=400, detail=f"this type holds {held_as.data_kind} data, not {kind}"
        )
    existing = await repository.find_membership_by_data(session, data)
    if existing is not None and existing.object_id != object_id:
        raise HTTPException(
            status_code=409, detail=f"object {existing.object_id} already holds this data"
        )


async def create_object(session: AsyncSession, body: ObjectCreate) -> ObjectOut:
    for facet in body.facets:
        await _check_facet(session, None, facet.type_id, facet.data)
    for supertype_id in body.as_type.supertype_ids if body.as_type else []:
        await get_type_or_404(session, supertype_id)
    for signature in body.signatures:
        await get_type_or_404(session, signature.domain_id)
        await get_type_or_404(session, signature.codomain_id)
    for section_id in body.sections:
        await get_object_or_404(session, section_id)

    obj = await repository.add_object(
        session, body.latex, body.description, _linkable(body.image_url)
    )
    await _replace_references(session, obj.id, body.references)
    if body.as_type is not None:
        repository.add_type(session, obj.id, body.as_type.data_kind)
        await session.flush()
        for supertype_id in body.as_type.supertype_ids:
            repository.add_subtype(session, obj.id, supertype_id)
    for facet in body.facets:
        repository.add_membership(session, obj.id, facet.type_id, facet.data)
    for signature in body.signatures:
        repository.add_signature(session, obj.id, signature.domain_id, signature.codomain_id)
    for section_id in body.sections:
        repository.add_section_filing(session, obj.id, section_id)
    events.add_event(session, "object_created", obj.id, body.contributor, "manual")
    await session.commit()
    await session.refresh(obj)
    return (await objects_out(session, [obj]))[0]


async def set_facet(
    session: AsyncSession, object_id: uuid.UUID, type_id: uuid.UUID, body: FacetData
) -> ObjectOut:
    obj = await get_object_or_404(session, object_id)
    await _check_facet(session, object_id, type_id, body.data)
    existing = await repository.get_membership(session, object_id, type_id)
    if existing is None:
        repository.add_membership(session, object_id, type_id, body.data)
    else:
        existing.data = body.data
        session.add(existing)
    await session.commit()
    return (await objects_out(session, [obj]))[0]


async def remove_facet(session: AsyncSession, object_id: uuid.UUID, type_id: uuid.UUID) -> None:
    existing = await repository.get_membership(session, object_id, type_id)
    if existing is not None:
        await repository.delete_membership(session, existing)
        await session.commit()


async def add_signature(
    session: AsyncSession, map_id: uuid.UUID, body: SignatureIn
) -> SignatureOut:
    await get_object_or_404(session, map_id)
    await get_type_or_404(session, body.domain_id)
    await get_type_or_404(session, body.codomain_id)
    signature = repository.add_signature(session, map_id, body.domain_id, body.codomain_id)
    await session.commit()
    return (await _signatures_out(session, map_id, [signature.id]))[0]


async def remove_signature(session: AsyncSession, signature_id: uuid.UUID) -> None:
    signature = await repository.get_signature(session, signature_id)
    if signature is None:
        raise HTTPException(status_code=404, detail="signature not found")
    await repository.delete_signature(session, signature)
    await session.commit()


async def _signatures_out(
    session: AsyncSession, map_id: uuid.UUID, only: Sequence[uuid.UUID] | None = None
) -> list[SignatureOut]:
    signatures = [
        signature
        for signature in await repository.list_signatures_of(session, map_id)
        if only is None or signature.id in only
    ]
    types = {
        obj.id: obj
        for obj in await _objects_out_by_ids(
            session, [t for s in signatures for t in (s.domain_id, s.codomain_id)]
        )
    }
    return [
        SignatureOut(id=s.id, domain=types[s.domain_id], codomain=types[s.codomain_id])
        for s in signatures
    ]


async def get_object_detail(session: AsyncSession, object_id: uuid.UUID) -> ObjectDetailOut:
    obj = await get_object_or_404(session, object_id)
    as_type = await repository.get_type(session, object_id)
    memberships = await repository.list_memberships_for(session, [object_id])
    signatures = await _signatures_out(session, object_id)

    as_operator = await repository.list_relations_by_operator(session, object_id)
    as_input = await repository.list_relations_by_ids(
        session, await repository.list_relation_ids_by_input(session, object_id)
    )
    as_output = await repository.list_relations_by_ids(
        session, await repository.list_relation_ids_by_output(session, object_id)
    )

    is_top_level = await repository.get_top_level_object(session, object_id) is not None
    filed = [row.object_id for row in await repository.list_filed_under(session, [object_id])]
    sections = [row.section_id for row in await repository.list_filings_of(session, [object_id])]

    roles: list[ObjectRole] = []
    if as_type is not None:
        roles.append("type")
    if signatures or as_operator or await implementations.has_implementation(session, object_id):
        roles.append("map")
    if memberships:
        roles.append("instance")
    if filed or is_top_level:
        roles.append("section")

    types_of = {
        o.id: o for o in await _objects_out_by_ids(session, [m.type_id for m in memberships])
    }
    provenance = await _provenance(session, "object_created", [object_id])
    references = await repository.list_object_references(session, object_id)

    async def related(direction: Literal["down", "up"]) -> list[ObjectOut]:
        found = await repository.list_related_types(
            session, [object_id], direction, transitive=False
        )
        return await _objects_out_by_ids(session, found)

    return ObjectDetailOut(
        id=obj.id,
        latex=obj.latex,
        description=obj.description,
        image_url=obj.image_url,
        roles=roles,
        provenance=provenance.get(object_id),
        facets=[
            FacetDetailOut(type=types_of[m.type_id], data=m.data)
            for m in memberships
            if m.type_id in types_of
        ],
        as_type=None if as_type is None else TypeOut(data_kind=as_type.data_kind),
        subtypes=await related("down") if as_type else [],
        supertypes=await related("up") if as_type else [],
        instances=await _objects_out_by_ids(
            session, await repository.list_instance_ids(session, object_id)
        )
        if as_type
        else [],
        signatures=signatures,
        maps_from=await _objects_out_by_ids(
            session, await repository.list_map_ids_by_signature(session, object_id, as_domain=True)
        ),
        maps_to=await _objects_out_by_ids(
            session,
            await repository.list_map_ids_by_signature(session, object_id, as_domain=False),
        ),
        references=[ObjectReferenceOut.model_validate(row) for row in references],
        is_top_level=is_top_level,
        sections=await _objects_out_by_ids(session, sections),
        filed=await _objects_out_by_ids(session, filed),
        as_operator=await load_relations(session, as_operator),
        as_input=await load_relations(session, as_input),
        as_output=await load_relations(session, as_output),
    )


async def _instance_count(session: AsyncSession, type_id: uuid.UUID) -> int:
    below = await repository.list_related_types(session, [type_id], "down", transitive=True)
    instances: set[uuid.UUID] = set()
    for held_by in [type_id, *below]:
        instances.update(await repository.list_instance_ids(session, held_by))
    return len(instances)


async def get_contents(session: AsyncSession) -> list[SectionNode]:
    roots = await repository.list_top_level_objects(session)

    children_of: dict[uuid.UUID, list[uuid.UUID]] = {}
    parent_of: dict[uuid.UUID, uuid.UUID] = {}
    visited = {root.id for root in roots}
    frontier = [root.id for root in roots]

    for _ in range(MAX_SECTION_DEPTH):
        if not frontier or len(visited) > MAX_SECTION_NODES:
            break
        found: defaultdict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
        for row in await repository.list_filed_under(session, frontier):
            found[row.section_id].append(row.object_id)
        next_frontier: list[uuid.UUID] = []
        for section_id in frontier:
            children = found.get(section_id, [])
            children_of[section_id] = children
            for child_id in children:
                if child_id not in visited:
                    visited.add(child_id)
                    parent_of[child_id] = section_id
                    next_frontier.append(child_id)
        frontier = next_frontier

    known = {obj.id: obj for obj in await repository.list_objects_by_ids(session, [*visited])}
    rank = {object_id: index for index, object_id in enumerate(known)}
    types = {t.id for t in await repository.list_types(session)}
    instance_counts = {
        type_id: await _instance_count(session, type_id) for type_id in known if type_id in types
    }

    def build(object_id: uuid.UUID) -> SectionNode:
        obj = known[object_id]
        children = children_of.get(object_id, [])
        nested = [
            child_id
            for child_id in children
            if parent_of.get(child_id) == object_id
            and (children_of.get(child_id) or child_id in types)
        ]
        nested.sort(key=lambda child_id: rank.get(child_id, 0))
        return SectionNode(
            id=obj.id,
            latex=obj.latex,
            description=obj.description,
            member_count=len(children) + instance_counts.get(object_id, 0),
            children=[build(child_id) for child_id in nested],
        )

    return [build(root.id) for root in roots]


async def get_operator_display(session: AsyncSession, operator_id: uuid.UUID) -> OperatorDisplayOut:
    await get_object_or_404(session, operator_id)
    row = await repository.get_operator_display(session, operator_id)
    if row is None:
        return OperatorDisplayOut(operator_id=operator_id, template=None, hidden_by_default=False)
    return OperatorDisplayOut.model_validate(row)


async def set_operator_display(
    session: AsyncSession, operator_id: uuid.UUID, body: OperatorDisplayUpdate
) -> OperatorDisplayOut:
    await get_object_or_404(session, operator_id)
    row = await repository.upsert_operator_display(
        session, operator_id, body.template, body.hidden_by_default
    )
    return OperatorDisplayOut.model_validate(row)


async def update_object(
    session: AsyncSession, object_id: uuid.UUID, body: ObjectUpdate
) -> ObjectOut:
    obj = await get_object_or_404(session, object_id)
    image_url = _linkable(body.image_url)
    await _replace_references(session, object_id, body.references)
    updated = await repository.update_object(session, obj, body.latex, body.description, image_url)
    return (await objects_out(session, [updated]))[0]


async def delete_object(session: AsyncSession, object_id: uuid.UUID) -> None:
    obj = await get_object_or_404(session, object_id)
    touching = await repository.list_relation_ids_touching(session, object_id)
    remarks = [comment.id for comment in await comments.list_comments_for(session, object_id)]
    await events.delete_events_for(session, [object_id, *touching, *remarks])
    await repository.delete_relations_referencing_object(session, object_id)
    await repository.delete_object(session, obj)


async def list_top_level_objects(session: AsyncSession) -> list[ObjectOut]:
    return await objects_out(session, await repository.list_top_level_objects(session))


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


async def _home_type(session: AsyncSession, kind: str) -> uuid.UUID:
    candidates = {t.object_id for t in await repository.list_types_of_kind(session, kind)}
    broadest = [
        type_id
        for type_id in candidates
        if not candidates.intersection(
            await repository.list_related_types(session, [type_id], "up", transitive=True)
        )
    ]
    if len(broadest) != 1:
        raise HTTPException(
            status_code=400,
            detail=f"no single type holds {kind} data, so a computed {kind} has nowhere to go",
        )
    return broadest[0]


async def _find_or_create_output(
    session: AsyncSession, output: ComputedOutput
) -> tuple[Object, bool]:
    if output.data is None:
        return await repository.add_object(session, output.latex, None), True
    existing = await repository.find_membership_by_data(session, output.data)
    if existing is not None:
        return await get_object_or_404(session, existing.object_id), False
    home = await _home_type(session, _kind_of(output.data))
    obj = await repository.add_object(session, output.latex, None)
    repository.add_membership(session, obj.id, home, output.data)
    await session.flush()
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
) -> list[ObjectOut]:
    types: list[uuid.UUID] | None = None
    if member_of is not None:
        await get_type_or_404(session, member_of)
        types = [member_of]
        if transitive:
            types += await repository.list_related_types(
                session, [member_of], "down", transitive=True
            )
    found = await repository.query_objects(
        session,
        member_of=types,
        data_equals=_json_object("data_equals", data_equals),
        data_contains=_json_object("data_contains", data_contains),
        description_contains=(description_contains or "").strip() or None,
        where=[_property_filter(raw) for raw in where],
        limit=MAX_QUERY_RESULTS,
    )
    return await objects_out(session, found)


async def list_related_types(
    session: AsyncSession,
    type_id: uuid.UUID,
    direction: Literal["down", "up"],
    *,
    transitive: bool,
) -> list[ObjectOut]:
    await get_type_or_404(session, type_id)
    found = await repository.list_related_types(
        session, [type_id], direction, transitive=transitive
    )
    return await _objects_out_by_ids(session, found)


async def list_types(session: AsyncSession) -> list[ObjectOut]:
    return await objects_out(session, await repository.list_types(session))


async def list_sections(session: AsyncSession) -> list[ObjectOut]:
    return await _objects_out_by_ids(session, await repository.list_section_ids(session))
