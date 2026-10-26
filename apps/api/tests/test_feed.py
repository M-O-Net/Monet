from httpx import AsyncClient


async def make(client: AsyncClient, latex: str) -> str:
    resp = await client.post("/objects", json={"latex": latex, "contributor": "Noether"})
    result: str = resp.json()["id"]
    return result


async def test_a_comment_in_the_feed_names_what_it_is_about(client: AsyncClient) -> None:
    obj = await make(client, "A")
    await client.post(f"/objects/{obj}/comments", json={"body": "Look at its trace."})

    comment = (await client.get("/events", params={"kind": "comment_created"})).json()
    assert len(comment) == 1
    assert comment[0]["object"]["id"] == obj
    assert comment[0]["comment"]["body"] == "Look at its trace."


async def test_the_feed_filters_by_kind(client: AsyncClient) -> None:
    operator = await make(client, "\\text{Inverse}")
    matrix = await make(client, "B")
    await client.post(
        "/relations",
        json={"operator_id": operator, "input_object_ids": [matrix], "output_object_ids": [matrix]},
    )
    await client.post(f"/objects/{matrix}/comments", json={"body": "Self-inverse."})

    kinds = {
        kind: len((await client.get("/events", params={"kind": kind})).json())
        for kind in ("object_created", "relation_created", "comment_created")
    }
    assert kinds == {"object_created": 2, "relation_created": 1, "comment_created": 1}
    assert (await client.get("/events", params={"kind": "nonsense"})).status_code == 422
