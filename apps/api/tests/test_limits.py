import uuid
from collections.abc import AsyncIterator

from httpx import AsyncClient

from monet_api.core.limits import MAX_BODY_BYTES
from monet_api.core.schemas import MAX_DATA_CHARACTERS, MAX_ITEMS


async def test_an_overlong_latex_is_refused(client: AsyncClient) -> None:
    resp = await client.post("/objects", json={"latex": "x" * 20_001})
    assert resp.status_code == 422


async def test_oversized_data_is_refused(client: AsyncClient) -> None:
    kind = (await client.post("/objects", json={"latex": "T", "as_type": {}})).json()["id"]
    data = {"int": "1" * MAX_DATA_CHARACTERS}
    resp = await client.post(
        "/objects", json={"latex": "n", "facets": [{"type_id": kind, "data": data}]}
    )
    assert resp.status_code == 422


async def test_a_relation_with_too_many_inputs_is_refused(client: AsyncClient) -> None:
    operator = (await client.post("/objects", json={"latex": "f"})).json()["id"]
    x = (await client.post("/objects", json={"latex": "x"})).json()["id"]
    resp = await client.post(
        "/relations",
        json={
            "operator_id": operator,
            "input_object_ids": [x] * (MAX_ITEMS + 1),
            "output_object_ids": [x],
        },
    )
    assert resp.status_code == 422


async def test_a_body_over_the_cap_is_refused_before_it_is_read(client: AsyncClient) -> None:
    resp = await client.post(
        f"/objects/{uuid.uuid4()}/comments",
        content=b"x" * (MAX_BODY_BYTES + 1),
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 413


async def test_a_streamed_body_over_the_cap_is_refused(client: AsyncClient) -> None:
    async def chunks() -> AsyncIterator[bytes]:
        for _ in range(9):
            yield b"x" * 1_000_000

    resp = await client.post(
        f"/objects/{uuid.uuid4()}/comments",
        content=chunks(),
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 413
