from typing import Any

from httpx import AsyncClient
from sqlmodel import func, select

from monet_api.core.db import async_session
from monet_api.objects.models import RelationReference

KNOTINFO = {"label": "KnotInfo", "url": "https://knotinfo.math.indiana.edu/results.php?3_1"}
ATLAS = {"label": "Knot Atlas", "url": "https://katlas.org/wiki/3_1"}


async def _make(client: AsyncClient, latex: str) -> str:
    result: str = (await client.post("/objects", json={"latex": latex})).json()["id"]
    return result


async def _edge(client: AsyncClient) -> tuple[str, str, str]:
    return (
        await _make(client, "Alexander"),
        await _make(client, "3_1"),
        await _make(client, "t^2 - t + 1"),
    )


def _labels(relation: dict[str, Any]) -> list[str]:
    return [reference["label"] for reference in relation["references"]]


async def _reference_rows() -> int:
    async with async_session() as session:
        count: int = (await session.exec(select(func.count()).select_from(RelationReference))).one()
        return count


async def test_a_relation_carries_its_references_everywhere_it_is_shown(
    client: AsyncClient,
) -> None:
    operator, knot, polynomial = await _edge(client)
    resp = await client.post(
        "/relations",
        json={
            "operator_id": operator,
            "input_object_ids": [knot],
            "output_object_ids": [polynomial],
            "references": [KNOTINFO, ATLAS],
        },
    )
    assert resp.status_code == 201
    assert _labels(resp.json()) == ["KnotInfo", "Knot Atlas"]

    mapped = (await client.get("/relations", params={"focus": polynomial})).json()
    assert _labels(mapped["relations"][0]) == ["KnotInfo", "Knot Atlas"]
    detail = (await client.get(f"/objects/{knot}")).json()
    assert _labels(detail["as_input"][0]["relations"][0]) == ["KnotInfo", "Knot Atlas"]
    output_side = (await client.get(f"/objects/{polynomial}")).json()["as_output"][0]
    assert _labels(output_side["relations"][0]) == [
        "KnotInfo",
        "Knot Atlas",
    ]
    neighborhood = (await client.get(f"/objects/{knot}/neighborhood")).json()
    assert _labels(neighborhood["relations"][0]) == ["KnotInfo", "Knot Atlas"]


async def test_a_second_source_credits_an_existing_relation(client: AsyncClient) -> None:
    operator, knot, polynomial = await _edge(client)
    relation = (
        await client.post(
            "/relations",
            json={
                "operator_id": operator,
                "input_object_ids": [knot],
                "output_object_ids": [polynomial],
                "references": [KNOTINFO],
            },
        )
    ).json()

    resp = await client.post(f"/relations/{relation['id']}/references", json=ATLAS)
    assert resp.status_code == 200
    assert _labels(resp.json()) == ["KnotInfo", "Knot Atlas"]

    again = await client.post(f"/relations/{relation['id']}/references", json=ATLAS)
    assert _labels(again.json()) == ["KnotInfo", "Knot Atlas"]

    refused = await client.post(
        f"/relations/{relation['id']}/references", json={"label": "x", "url": "javascript:1"}
    )
    assert refused.status_code == 400


async def test_posting_an_existing_relation_credits_it_instead_of_creating_a_twin(
    client: AsyncClient,
) -> None:
    operator, knot, polynomial = await _edge(client)
    body = {"operator_id": operator, "input_object_ids": [knot], "output_object_ids": [polynomial]}
    first = await client.post("/relations", json={**body, "references": [KNOTINFO]})
    second = await client.post("/relations", json={**body, "references": [ATLAS, KNOTINFO]})

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert _labels(second.json()) == ["KnotInfo", "Knot Atlas"]
    assert (await client.get(f"/objects/{knot}")).json()["relation_count"] == 1


async def test_a_relation_cannot_be_edited_into_a_twin_of_another(client: AsyncClient) -> None:
    operator, knot, polynomial = await _edge(client)
    other = await _make(client, "4_1")
    body = {"operator_id": operator, "input_object_ids": [knot], "output_object_ids": [polynomial]}
    await client.post("/relations", json=body)
    second = (
        await client.post(
            "/relations",
            json={**body, "input_object_ids": [other]},
        )
    ).json()

    resp = await client.put(f"/relations/{second['id']}", json=body)
    assert resp.status_code == 409


async def test_asserting_a_known_relation_adds_its_credit(client: AsyncClient) -> None:
    integers = (
        await client.post("/objects", json={"latex": "Z", "as_type": {"data_kind": "int"}})
    ).json()["id"]
    determinant = (await client.post("/objects", json={"latex": "Crossings"})).json()["id"]
    knot = await _make(client, "3_1")
    three = {"int": 3}
    await client.post(
        "/objects", json={"latex": "3", "facets": [{"type_id": integers, "data": three}]}
    )
    payload = {
        "operator_id": determinant,
        "input_object_ids": [knot],
        "outputs": [{"latex": "3", "data": three}],
    }

    first = (await client.post("/relations/assert", json=payload)).json()
    assert first["relation"]["references"] == []
    second = (
        await client.post("/relations/assert", json={**payload, "references": [KNOTINFO]})
    ).json()

    assert second["created_relation"] is False
    assert second["relation"]["id"] == first["relation"]["id"]
    assert _labels(second["relation"]) == ["KnotInfo"]


async def test_references_go_with_their_relation(client: AsyncClient) -> None:
    operator, knot, polynomial = await _edge(client)
    body = {"operator_id": operator, "output_object_ids": [polynomial], "references": [KNOTINFO]}
    first = (await client.post("/relations", json={**body, "input_object_ids": [knot]})).json()
    other = await _make(client, "4_1")
    await client.post("/relations", json={**body, "input_object_ids": [other]})
    assert await _reference_rows() == 2

    await client.delete(f"/relations/{first['id']}")
    assert await _reference_rows() == 1

    await client.delete(f"/objects/{other}")
    assert await _reference_rows() == 0
