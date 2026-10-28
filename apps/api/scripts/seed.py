"""Seed the demo dataset: objects, relations, and an implementation per operator.

Wipes and reinserts, so it's safe to re-run — `uv run python scripts/seed.py` from apps/api/,
or `just seed`, always resets to exactly this dataset. Pass --if-empty to skip entirely when
the objects table already has rows (used by docker-compose.dev.yml's startup command, so a
fresh `just up` always has demo data without clobbering anything you've since added by hand
through the GUI on every restart).
"""

import asyncio
import pathlib
import sys
import uuid

from seed_data.catalogue import TOP_LEVEL, TYPES
from seed_data.dataset import (
    DISPLAYS,
    FILINGS,
    IMAGES,
    IMPLEMENTATIONS,
    INSTANCES,
    OBJECTS,
    REFERENCES,
    RELATIONS,
    SIGNATURES,
)
from sqlmodel import delete, func, select

from monet_api.comments.models import Comment
from monet_api.core.db import async_session
from monet_api.events.models import Event
from monet_api.implementations.models import Implementation
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


async def seed() -> None:
    async with async_session() as session:
        if "--if-empty" in sys.argv:
            count = (await session.exec(select(func.count()).select_from(Object))).one()
            if count > 0:
                print(f"objects table already has {count} rows, skipping (--if-empty)")
                return

        await session.exec(delete(Event))
        await session.exec(delete(Comment))
        await session.exec(delete(Implementation))
        await session.exec(delete(ObjectReference))
        await session.exec(delete(OperatorDisplay))
        await session.exec(delete(TopLevelObject))
        await session.exec(delete(RelationOutput))
        await session.exec(delete(RelationInput))
        await session.exec(delete(Relation))
        await session.exec(delete(Object))
        await session.commit()

        ids: dict[str, uuid.UUID] = {}
        for key, (latex, description) in OBJECTS.items():
            obj = Object(latex=latex, description=description, image_url=IMAGES.get(key))
            session.add(obj)
            await session.flush()
            ids[key] = obj.id

        for key, entries in REFERENCES.items():
            for position, (label, url) in enumerate(entries):
                session.add(
                    ObjectReference(object_id=ids[key], label=label, url=url, position=position)
                )

        for operator, inputs, outputs in RELATIONS:
            rel = Relation(operator_id=ids[operator])
            session.add(rel)
            await session.flush()
            for position, key in enumerate(inputs):
                session.add(
                    RelationInput(relation_id=rel.id, object_id=ids[key], position=position)
                )
            for position, key in enumerate(outputs):
                session.add(
                    RelationOutput(relation_id=rel.id, object_id=ids[key], position=position)
                )

        for key, (_, _, data_kind, _) in TYPES.items():
            session.add(Type(object_id=ids[key], data_kind=data_kind))
        await session.flush()

        for key, (_, _, _, supertypes) in TYPES.items():
            for supertype in supertypes:
                session.add(Subtype(type_id=ids[key], supertype_id=ids[supertype]))

        for key, (_, _, facets) in INSTANCES.items():
            for type_key, data in facets:
                session.add(Membership(object_id=ids[key], type_id=ids[type_key], data=data))

        for operator, domain, codomain in SIGNATURES:
            session.add(
                Signature(map_id=ids[operator], domain_id=ids[domain], codomain_id=ids[codomain])
            )

        for operator, (template, hidden) in DISPLAYS.items():
            session.add(
                OperatorDisplay(
                    operator_id=ids[operator], template=template, hidden_by_default=hidden
                )
            )

        for section, filed in FILINGS.items():
            for key in filed:
                session.add(SectionFiling(object_id=ids[key], section_id=ids[section]))

        for root in TOP_LEVEL:
            session.add(TopLevelObject(object_id=ids[root]))

        implementation_dir = pathlib.Path(__file__).parent / "implementations"
        for operator, filename in IMPLEMENTATIONS.items():
            session.add(
                Implementation(
                    operator_id=ids[operator],
                    code=(implementation_dir / f"{filename}.py").read_text(),
                )
            )

        await session.commit()
        reference_count = sum(len(entries) for entries in REFERENCES.values())
        print(
            f"seeded {len(OBJECTS)} objects ({len(TYPES)} types), {len(RELATIONS)} relations, "
            f"{len(IMPLEMENTATIONS)} implementations, {len(IMAGES)} images "
            f"and {reference_count} references"
        )


if __name__ == "__main__":
    asyncio.run(seed())
