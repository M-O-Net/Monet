import asyncio
import json
import math

from httpx import AsyncClient


async def make(client: AsyncClient, body: dict[str, object]) -> str:
    resp = await client.post("/objects", json=body)
    assert resp.status_code == 201, resp.text
    result: str = resp.json()["id"]
    return result


async def test_simultaneous_asserts_of_one_result_create_one_object_and_one_relation(
    client: AsyncClient,
) -> None:
    await make(client, {"latex": "\\mathbb{Z}", "as_type": {"data_kind": "int"}})
    square = await make(client, {"latex": "\\text{Square}"})
    payload = {
        "operator_id": square,
        "input_object_ids": [],
        "outputs": [{"latex": "49", "data": {"int": 49}}],
    }
    responses = await asyncio.gather(
        *(client.post("/relations/assert", json=payload) for _ in range(5))
    )
    assert all(resp.status_code == 200 for resp in responses), [r.text for r in responses]
    holders = await client.get("/objects", params={"data_equals": '{"int": 49}'})
    assert holders.json()["total"] == 1
    assert sum(resp.json()["created_relation"] for resp in responses) == 1


async def test_a_second_broadest_type_of_a_kind_is_refused(client: AsyncClient) -> None:
    integers = await make(client, {"latex": "\\mathbb{Z}", "as_type": {"data_kind": "int"}})
    rival = await client.post(
        "/objects", json={"latex": "\\mathbb{N}", "as_type": {"data_kind": "int"}}
    )
    assert rival.status_code == 400
    assert "subtype" in rival.json()["detail"]
    await make(
        client,
        {"latex": "\\mathbb{N}", "as_type": {"data_kind": "int", "supertype_ids": [integers]}},
    )


async def test_naming_one_id_twice_is_refused(client: AsyncClient) -> None:
    root = await make(client, {"latex": "T", "as_type": {}})
    resp = await client.post(
        "/objects", json={"latex": "S", "as_type": {"supertype_ids": [root, root]}}
    )
    assert resp.status_code == 400


async def test_data_that_postgres_cannot_store_is_refused(client: AsyncClient) -> None:
    kind = await make(client, {"latex": "\\mathbb{R}", "as_type": {}})
    for data in ({"real": math.nan}, {"real": math.inf}, {"text": "a\x00b"}):
        body = json.dumps({"latex": "x", "facets": [{"type_id": kind, "data": data}]})
        resp = await client.post(
            "/objects", content=body, headers={"content-type": "application/json"}
        )
        assert resp.status_code == 422, data
    assert (await client.post("/objects", json={"latex": "a\x00b"})).status_code == 422


async def test_a_deeply_nested_data_filter_is_a_bad_request(client: AsyncClient) -> None:
    nested = "[" * 5_000 + "]" * 5_000
    resp = await client.get("/objects", params={"data_equals": nested})
    assert resp.status_code == 400
