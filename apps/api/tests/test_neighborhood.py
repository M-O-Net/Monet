from typing import Any

from httpx import AsyncClient


async def _make(client: AsyncClient, latex: str) -> str:
    resp = await client.post("/objects", json={"latex": latex})
    object_id: str = resp.json()["id"]
    return object_id


async def _relate(client: AsyncClient, operator: str, inputs: list[str], outputs: list[str]) -> str:
    resp = await client.post(
        "/relations",
        json={"operator_id": operator, "input_object_ids": inputs, "output_object_ids": outputs},
    )
    relation_id: str = resp.json()["id"]
    return relation_id


def _hidden(body: dict[str, Any]) -> dict[tuple[str, str], int]:
    return {(row["side"], row["operator"]["id"]): row["count"] for row in body["hidden"]}


async def test_neighborhood_caps_relations_per_operator_and_side(client: AsyncClient) -> None:
    one = await _make(client, "1")
    determinant = await _make(client, r"\text{Determinant}")
    order = await _make(client, r"\text{Matrix Order}")
    for n in range(5):
        matrix = await _make(client, f"M_{n}")
        await _relate(client, determinant, [matrix], [one])
    await _relate(client, order, [await _make(client, "I")], [one])

    resp = await client.get(f"/objects/{one}/neighborhood")
    assert resp.status_code == 200
    body = resp.json()

    by_operator = [relation["operator"]["id"] for relation in body["relations"]]
    assert by_operator.count(determinant) == 3
    assert by_operator.count(order) == 1
    assert _hidden(body) == {("output", determinant): 2}


async def test_neighborhood_cap_is_adjustable(client: AsyncClient) -> None:
    one = await _make(client, "1")
    determinant = await _make(client, r"\text{Determinant}")
    for n in range(4):
        await _relate(client, determinant, [await _make(client, f"M_{n}")], [one])

    body = (await client.get(f"/objects/{one}/neighborhood", params={"per_map": 1})).json()
    assert len(body["relations"]) == 1
    assert _hidden(body) == {("output", determinant): 3}

    body = (await client.get(f"/objects/{one}/neighborhood", params={"per_map": 10})).json()
    assert len(body["relations"]) == 4
    assert body["hidden"] == []


async def test_neighborhood_counts_each_side_separately(client: AsyncClient) -> None:
    p = await _make(client, "p")
    roots = await _make(client, r"\text{Roots}")
    derivative = await _make(client, r"\text{Derivative}")
    for n in range(4):
        await _relate(client, derivative, [await _make(client, f"q_{n}")], [p])
    await _relate(client, derivative, [p], [await _make(client, "p'")])
    await _relate(client, roots, [p], [await _make(client, "r")])

    body = (await client.get(f"/objects/{p}/neighborhood")).json()
    assert len(body["relations"]) == 5
    assert _hidden(body) == {("output", derivative): 1}


async def test_neighborhood_caps_relations_an_operator_runs(client: AsyncClient) -> None:
    determinant = await _make(client, r"\text{Determinant}")
    for n in range(5):
        await _relate(
            client, determinant, [await _make(client, f"M_{n}")], [await _make(client, "d")]
        )

    body = (await client.get(f"/objects/{determinant}/neighborhood")).json()
    assert len(body["relations"]) == 3
    assert _hidden(body) == {("operator", determinant): 2}


async def test_a_relation_shown_on_one_side_is_not_counted_hidden_on_another(
    client: AsyncClient,
) -> None:
    x = await _make(client, "x")
    identity = await _make(client, r"\text{Identity}")
    await _relate(client, identity, [x], [x])

    body = (await client.get(f"/objects/{x}/neighborhood", params={"per_map": 1})).json()
    assert len(body["relations"]) == 1
    assert body["hidden"] == []


async def test_neighborhood_of_a_missing_object_is_404(client: AsyncClient) -> None:
    resp = await client.get("/objects/00000000-0000-0000-0000-000000000000/neighborhood")
    assert resp.status_code == 404


async def test_neighborhood_refuses_a_cap_below_one(client: AsyncClient) -> None:
    one = await _make(client, "1")
    resp = await client.get(f"/objects/{one}/neighborhood", params={"per_map": 0})
    assert resp.status_code == 422
