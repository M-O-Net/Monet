"""Business logic for the objects domain: 404/400 translation and schema assembly.

Orchestrates repository.py calls; owns no SQL of its own.
"""

import datetime
import json
import re
import uuid
from collections import Counter, defaultdict
from collections.abc import Collection, Sequence
from typing import Any, Literal

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from monet_api.comments import repository as comments
from monet_api.events import repository as events
from monet_api.events.models import Event
from monet_api.implementations import repository as implementations
from monet_api.objects import repository
from monet_api.objects.models import Object, Relation, RelationInput, RelationOutput, Type
from monet_api.objects.repository import ObjectFilter, Step
from monet_api.objects.schemas import (
    ComputedOutput,
    FacetData,
    FacetDetailOut,
    FacetOut,
    HiddenRelationsOut,
    LoopStepOut,
    NeighborhoodOut,
    NeighborhoodSide,
    ObjectCreate,
    ObjectDetailOut,
    ObjectOut,
    ObjectPageOut,
    ObjectRole,
    ObjectUpdate,
    OperatorDisplayOut,
    OperatorDisplayUpdate,
    ProvenanceOut,
    ReferenceIn,
    ReferenceOut,
    RelationAssert,
    RelationAssertOut,
    RelationCreate,
    RelationDisplayOut,
    RelationGroupOut,
    RelationMapOut,
    RelationOut,
    RelationPageOut,
    RelationSlotOut,
    SectionNode,
    SignatureIn,
    SignatureOut,
    TypeOut,
)

MAX_SECTION_DEPTH = 6
MAX_SECTION_NODES = 500
SIDES: tuple[NeighborhoodSide, ...] = ("operator", "input", "output")
DETAIL_PER_OPERATOR = 3
DETAIL_OPERATED = 10
DETAIL_MAX_GROUPS = 30
LOOP_MAX_LENGTH = 6
LOOP_MAX_FOUND = 3
LOOP_MAX_STEPS = 5000
LOOP_MAX_VISITS = 20000
MAP_MAX_NODES = 150
MAP_PER_OPERATOR = 2
MAP_HUBS = 3

StepsOut = defaultdict[uuid.UUID, list[Step]]


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


async def objects_out_by_ids(
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
    objects = {obj.id: obj for obj in await objects_out_by_ids(session, [*needed_ids])}
    displays = {
        row.operator_id: RelationDisplayOut.model_validate(row)
        for row in await repository.list_operator_displays(
            session, [relation.operator_id for relation in relations]
        )
    }
    provenance = await _provenance(session, "relation_created", relation_ids)
    references: defaultdict[uuid.UUID, list[ReferenceOut]] = defaultdict(list)
    for row in await repository.list_relation_references_for(session, relation_ids):
        references[row.relation_id].append(ReferenceOut.model_validate(row))

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
            references=references[relation.id],
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


async def _load_relations_by_ids(
    session: AsyncSession, relation_ids: Sequence[uuid.UUID]
) -> dict[uuid.UUID, RelationOut]:
    relations = await repository.list_relations_by_ids(session, relation_ids)
    return {relation.id: relation for relation in await load_relations(session, relations)}


_MACRO = re.compile(r"\\[a-zA-Z]+")
_GROUPING = re.compile(r"[{}$]")
_NOISE = re.compile(r"[\s,&\\]+")


def _search_key(text: str) -> str:
    return _NOISE.sub(" ", _GROUPING.sub("", _MACRO.sub(" ", text))).strip().lower()


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
    session: AsyncSession, object_id: uuid.UUID, references: Sequence[ReferenceIn]
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
        for obj in await objects_out_by_ids(
            session, [t for s in signatures for t in (s.domain_id, s.codomain_id)]
        )
    }
    return [
        SignatureOut(id=s.id, domain=types[s.domain_id], codomain=types[s.codomain_id])
        for s in signatures
    ]


async def _relation_groups(
    session: AsyncSession, object_id: uuid.UUID
) -> dict[NeighborhoodSide, list[RelationGroupOut]]:
    samples: dict[NeighborhoodSide, defaultdict[uuid.UUID, list[uuid.UUID]]] = {}
    totals: dict[tuple[NeighborhoodSide, uuid.UUID], int] = {}
    for side in SIDES:
        cap = DETAIL_OPERATED if side == "operator" else DETAIL_PER_OPERATOR
        samples[side] = defaultdict(list)
        for _, operator_id, relation_id, total in await repository.sample_relations(
            session, [object_id], side, cap
        ):
            samples[side][operator_id].append(relation_id)
            totals[side, operator_id] = total

    operators = await objects_out_by_ids(session, list({key[1] for key in totals}))
    shown = {
        side: [operator for operator in operators if operator.id in samples[side]][
            :DETAIL_MAX_GROUPS
        ]
        for side in SIDES
    }
    relations = await _load_relations_by_ids(
        session,
        [
            relation_id
            for side in SIDES
            for operator in shown[side]
            for relation_id in samples[side][operator.id]
        ],
    )
    shown_ids = {side: {operator.id for operator in shown[side]} for side in SIDES}
    return {
        side: [
            RelationGroupOut(
                operator=operator,
                relations=[relations[relation_id] for relation_id in samples[side][operator.id]]
                if operator.id in shown_ids[side]
                else [],
                total=totals[side, operator.id],
            )
            for operator in operators
            if operator.id in samples[side]
        ]
        for side in SIDES
    }


async def get_object_detail(session: AsyncSession, object_id: uuid.UUID) -> ObjectDetailOut:
    obj = await get_object_or_404(session, object_id)
    as_type = await repository.get_type(session, object_id)
    memberships = await repository.list_memberships_for(session, [object_id])
    signatures = await _signatures_out(session, object_id)
    groups = await _relation_groups(session, object_id)

    is_top_level = await repository.get_top_level_object(session, object_id) is not None
    filed_count = await repository.count_objects(session, ObjectFilter(filed_under=object_id))
    sections = [row.section_id for row in await repository.list_filings_of(session, [object_id])]

    roles: list[ObjectRole] = []
    if as_type is not None:
        roles.append("type")
    if (
        signatures
        or groups["operator"]
        or await implementations.has_implementation(session, object_id)
    ):
        roles.append("map")
    if memberships:
        roles.append("instance")
    if filed_count or is_top_level:
        roles.append("section")

    types_of = {
        o.id: o for o in await objects_out_by_ids(session, [m.type_id for m in memberships])
    }
    provenance = await _provenance(session, "object_created", [object_id])
    references = await repository.list_object_references(session, object_id)

    async def related(direction: Literal["down", "up"]) -> list[ObjectOut]:
        found = await repository.list_related_types(
            session, [object_id], direction, transitive=False
        )
        return await objects_out_by_ids(session, found)

    async def type_out(found: Type) -> TypeOut:
        below = await repository.list_related_types(session, [object_id], "down", transitive=True)
        kinds = await repository.list_data_kinds(session, [object_id, *below])
        return TypeOut(data_kind=found.data_kind, data_kinds=kinds)

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
        as_type=None if as_type is None else await type_out(as_type),
        subtypes=await related("down") if as_type else [],
        supertypes=await related("up") if as_type else [],
        instance_count=await repository.count_objects(session, ObjectFilter(member_of=[object_id]))
        if as_type
        else 0,
        signatures=signatures,
        maps_from=await objects_out_by_ids(
            session, await repository.list_map_ids_by_signature(session, object_id, as_domain=True)
        ),
        maps_to=await objects_out_by_ids(
            session,
            await repository.list_map_ids_by_signature(session, object_id, as_domain=False),
        ),
        references=[ReferenceOut.model_validate(row) for row in references],
        is_top_level=is_top_level,
        sections=await objects_out_by_ids(session, sections),
        filed_count=filed_count,
        relation_count=await repository.count_relations_touching(session, [object_id]),
        as_operator=groups["operator"],
        as_input=groups["input"],
        as_output=groups["output"],
    )


async def list_object_relations(
    session: AsyncSession,
    object_id: uuid.UUID,
    side: NeighborhoodSide,
    operator_id: uuid.UUID | None,
    offset: int,
    limit: int,
) -> RelationPageOut:
    await get_object_or_404(session, object_id)
    found = await repository.list_relations_on_side(
        session, object_id, side, operator_id, offset=offset, limit=limit
    )
    return RelationPageOut(
        items=await load_relations(session, found),
        total=await repository.count_relations_on_side(session, object_id, side, operator_id),
    )


async def get_neighborhood(
    session: AsyncSession, object_id: uuid.UUID, per_map: int
) -> NeighborhoodOut:
    await get_object_or_404(session, object_id)
    shown: set[uuid.UUID] = set()
    hidden: dict[tuple[NeighborhoodSide, uuid.UUID], int] = {}
    for side in SIDES:
        sampled: defaultdict[uuid.UUID, int] = defaultdict(int)
        totals: dict[uuid.UUID, int] = {}
        for _, operator_id, relation_id, total in await repository.sample_relations(
            session, [object_id], side, per_map
        ):
            shown.add(relation_id)
            sampled[operator_id] += 1
            totals[operator_id] = total
        for operator_id, total in totals.items():
            if total > sampled[operator_id]:
                hidden[side, operator_id] = total - sampled[operator_id]

    operators = {
        obj.id: obj
        for obj in await objects_out_by_ids(session, [operator_id for _, operator_id in hidden])
    }
    relations = await _load_relations_by_ids(session, sorted(shown))
    return NeighborhoodOut(
        relations=[relations[relation_id] for relation_id in sorted(shown)],
        hidden=[
            HiddenRelationsOut(operator=operators[operator_id], side=side, count=count)
            for (side, operator_id), count in hidden.items()
        ],
    )


async def _steps_near(session: AsyncSession, object_id: uuid.UUID) -> StepsOut:
    steps_out: StepsOut = defaultdict(list)
    reached = {object_id}
    frontier = [object_id]
    collected = 0
    for _ in range(LOOP_MAX_LENGTH):
        if not frontier or collected > LOOP_MAX_STEPS:
            break
        steps = await repository.list_steps_from(session, frontier)
        collected += len(steps)
        frontier = []
        for step in steps:
            steps_out[step.source].append(step)
            if step.target not in reached:
                reached.add(step.target)
                frontier.append(step.target)
    return steps_out


def _distances_back(steps_out: StepsOut, object_id: uuid.UUID) -> dict[uuid.UUID, int]:
    into: defaultdict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
    for steps in steps_out.values():
        for step in steps:
            into[step.target].add(step.source)
    distance = {object_id: 0}
    frontier = [object_id]
    while frontier:
        following: list[uuid.UUID] = []
        for node in frontier:
            for source in into[node] - distance.keys():
                distance[source] = distance[node] + 1
                following.append(source)
        frontier = following
    return distance


def _cycles_through(
    steps_out: StepsOut, object_id: uuid.UUID, via: uuid.UUID | None
) -> list[list[Step]]:
    back = _distances_back(steps_out, object_id)
    found: list[list[Step]] = []
    seen: set[tuple[uuid.UUID, ...]] = set()
    visits = 0

    def walk(node: uuid.UUID, path: list[Step]) -> None:
        nonlocal visits
        visits += 1
        for step in steps_out[node]:
            if len(found) >= LOOP_MAX_FOUND or visits > LOOP_MAX_VISITS:
                return
            if not path and via is not None and step.relation_id != via:
                continue
            if step.target == object_id:
                key = tuple(taken.relation_id for taken in [*path, step])
                if key not in seen:
                    seen.add(key)
                    found.append([*path, step])
                continue
            home = back.get(step.target)
            if home is None or len(path) + 1 + home > LOOP_MAX_LENGTH:
                continue
            if all(taken.target != step.target for taken in path):
                walk(step.target, [*path, step])

    walk(object_id, [])
    return found


async def find_loops(
    session: AsyncSession, object_id: uuid.UUID, via: uuid.UUID | None
) -> list[list[LoopStepOut]]:
    await get_object_or_404(session, object_id)
    cycles = _cycles_through(await _steps_near(session, object_id), object_id, via)
    relations = await _load_relations_by_ids(
        session, list({step.relation_id for cycle in cycles for step in cycle})
    )
    objects = {
        slot.object.id: slot.object
        for relation in relations.values()
        for slot in [*relation.inputs, *relation.outputs]
    }
    return [
        [
            LoopStepOut(
                relation=relations[step.relation_id],
                source=objects[step.source],
                target=objects[step.target],
            )
            for step in cycle
        ]
        for cycle in cycles
    ]


async def _map_candidates(
    session: AsyncSession, frontier: Sequence[uuid.UUID], drawn: Collection[uuid.UUID]
) -> list[uuid.UUID]:
    ranked: list[tuple[int, uuid.UUID]] = []
    for side in SIDES:
        seen_in_group: Counter[tuple[uuid.UUID, uuid.UUID]] = Counter()
        for sample in await repository.sample_relations(session, frontier, side, MAP_PER_OPERATOR):
            seen_in_group[sample.object_id, sample.operator_id] += 1
            ranked.append((seen_in_group[sample.object_id, sample.operator_id], sample.relation_id))
    ranked.sort(key=_first)
    return [
        relation_id
        for relation_id in dict.fromkeys(relation_id for _, relation_id in ranked)
        if relation_id not in drawn
    ]


def _first(pair: tuple[int, uuid.UUID]) -> int:
    return pair[0]


async def map_relations(
    session: AsyncSession, focus: Sequence[uuid.UUID], depth: int
) -> RelationMapOut:
    for object_id in focus:
        await get_object_or_404(session, object_id)
    centres = list(focus) or await repository.list_busiest_objects(session, MAP_HUBS)

    drawn: dict[uuid.UUID, int] = {}
    reached = set(centres)
    frontier = list(centres)
    for layer in range(depth):
        candidates = await _map_candidates(session, frontier, drawn)
        slots: list[RelationInput | RelationOutput] = [
            *await repository.list_relation_inputs_for(session, candidates),
            *await repository.list_relation_outputs_for(session, candidates),
        ]
        operands: defaultdict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
        for slot in slots:
            operands[slot.relation_id].add(slot.object_id)
        frontier = []
        for relation_id in candidates:
            arriving = operands[relation_id] - reached
            if len(drawn) + 1 + len(reached) + len(arriving) > MAP_MAX_NODES:
                continue
            drawn[relation_id] = layer
            reached |= arriving
            frontier.extend(arriving)

    relations = await _load_relations_by_ids(session, list(drawn))
    around_centres = sum(layer == 0 for layer in drawn.values())
    return RelationMapOut(
        relations=[relations[relation_id] for relation_id in drawn],
        omitted=await repository.count_relations_touching(session, centres) - around_centres,
    )


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
        for row in await repository.list_filed_sections_and_types(session, frontier):
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
    types = set(await repository.list_type_ids(session, list(known)))
    instance_counts = await repository.count_instances_below(session, list(types))
    filed_counts = await repository.count_filed_under(session, list(known))

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
            member_count=filed_counts.get(object_id, 0) + instance_counts.get(object_id, 0),
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


async def _validate_relation_operands(session: AsyncSession, body: RelationCreate) -> None:
    await get_object_or_404(session, body.operator_id)
    for oid in [*body.input_object_ids, *body.output_object_ids]:
        await get_object_or_404(session, oid)


async def _add_relation_references(
    session: AsyncSession, relation_id: uuid.UUID, references: Sequence[ReferenceIn]
) -> None:
    held = await repository.list_relation_references_for(session, [relation_id])
    urls = {row.url for row in held}
    for reference in references:
        url = _linkable(reference.url)
        if url is None or url in urls:
            continue
        urls.add(url)
        repository.add_relation_reference(
            session, relation_id, reference.label.strip(), url, len(urls) - 1
        )


async def _insert_relation(
    session: AsyncSession,
    operator_id: uuid.UUID,
    input_ids: Sequence[uuid.UUID],
    output_ids: Sequence[uuid.UUID],
) -> Relation:
    relation = await repository.create_relation(session, operator_id)
    for position, oid in enumerate(input_ids):
        repository.add_relation_input(session, relation.id, oid, position)
    for position, oid in enumerate(output_ids):
        repository.add_relation_output(session, relation.id, oid, position)
    return relation


async def create_relation(session: AsyncSession, body: RelationCreate) -> tuple[RelationOut, bool]:
    await _validate_relation_operands(session, body)

    relation = await _find_matching_relation(
        session, body.operator_id, body.input_object_ids, body.output_object_ids
    )
    created = relation is None
    if relation is None:
        relation = await _insert_relation(
            session, body.operator_id, body.input_object_ids, body.output_object_ids
        )
        events.add_event(session, "relation_created", relation.id, body.contributor, "manual")
    await _add_relation_references(session, relation.id, body.references)

    await session.commit()
    await session.refresh(relation)
    return await _load_relation_out(session, relation), created


async def add_relation_reference(
    session: AsyncSession, relation_id: uuid.UUID, body: ReferenceIn
) -> RelationOut:
    relation = await get_relation_or_404(session, relation_id)
    if _linkable(body.url) is None:
        raise HTTPException(status_code=400, detail="a reference needs a url")
    await _add_relation_references(session, relation_id, [body])
    await session.commit()
    return await _load_relation_out(session, relation)


async def get_relation(session: AsyncSession, relation_id: uuid.UUID) -> RelationOut:
    relation = await get_relation_or_404(session, relation_id)
    return await _load_relation_out(session, relation)


async def replace_relation(
    session: AsyncSession, relation_id: uuid.UUID, body: RelationCreate
) -> RelationOut:
    relation = await get_relation_or_404(session, relation_id)
    await _validate_relation_operands(session, body)
    twin = await _find_matching_relation(
        session, body.operator_id, body.input_object_ids, body.output_object_ids
    )
    if twin is not None and twin.id != relation_id:
        raise HTTPException(status_code=409, detail=f"relation {twin.id} already states this")

    relation.operator_id = body.operator_id
    session.add(relation)
    await repository.clear_relation_slots(session, relation_id)
    await repository.clear_relation_references(session, relation_id)

    for position, oid in enumerate(body.input_object_ids):
        repository.add_relation_input(session, relation.id, oid, position)
    for position, oid in enumerate(body.output_object_ids):
        repository.add_relation_output(session, relation.id, oid, position)
    await _add_relation_references(session, relation_id, body.references)

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
    candidates = await repository.list_relations_matching(
        session, operator_id, input_ids[0] if input_ids else None
    )
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
        relation = await _insert_relation(
            session, body.operator_id, body.input_object_ids, output_ids
        )
        events.add_event(session, "relation_created", relation.id, body.contributor, source)
    await _add_relation_references(session, relation.id, body.references)

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


async def list_objects(
    session: AsyncSession,
    *,
    q: str | None,
    role: ObjectRole | None,
    member_of: uuid.UUID | None,
    transitive: bool,
    filed_under: uuid.UUID | None,
    data_equals: str | None,
    data_contains: str | None,
    description_contains: str | None,
    where: Sequence[str],
    offset: int,
    limit: int,
) -> ObjectPageOut:
    types: list[uuid.UUID] | None = None
    if member_of is not None:
        await get_type_or_404(session, member_of)
        types = [member_of]
        if transitive:
            types += await repository.list_related_types(
                session, [member_of], "down", transitive=True
            )
    found = ObjectFilter(
        member_of=types,
        filed_under=filed_under,
        role=role,
        implemented=await implementations.list_implemented_operator_ids(session)
        if role == "map"
        else (),
        data_equals=_json_object("data_equals", data_equals),
        data_contains=_json_object("data_contains", data_contains),
        description_contains=(description_contains or "").strip() or None,
        where=[_property_filter(raw) for raw in where],
        search=_search_key(q or "") or None,
    )
    page, total = await repository.page_objects(session, found, offset=offset, limit=limit)
    return ObjectPageOut(items=await objects_out(session, page), total=total)


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
    return await objects_out_by_ids(session, found)
