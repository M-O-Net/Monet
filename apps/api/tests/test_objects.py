from httpx import AsyncClient


async def test_create_and_list_object(client: AsyncClient) -> None:
    resp = await client.post("/objects", json={"latex": "x^2"})
    assert resp.status_code == 201
    created = resp.json()
    assert created["latex"] == "x^2"
    assert created["description"] is None

    resp = await client.get("/objects")
    assert resp.status_code == 200
    assert [o["id"] for o in resp.json()] == [created["id"]]


async def test_object_description_is_optional_and_editable(client: AsyncClient) -> None:
    resp = await client.post("/objects", json={"latex": "x^2", "description": "a square"})
    obj_id = resp.json()["id"]
    assert resp.json()["description"] == "a square"

    resp = await client.patch(f"/objects/{obj_id}", json={"latex": "x^2", "description": None})
    assert resp.json()["description"] is None


async def test_top_level_objects(client: AsyncClient) -> None:
    resp = await client.post("/objects", json={"latex": "\\text{Matrices}"})
    section_id = resp.json()["id"]
    resp = await client.post("/objects", json={"latex": "A"})
    specimen_id = resp.json()["id"]

    assert (await client.get("/top-level-objects")).json() == []
    assert (await client.get(f"/objects/{section_id}")).json()["is_top_level"] is False

    await client.put(f"/top-level-objects/{section_id}")
    top_level = (await client.get("/top-level-objects")).json()
    assert [o["id"] for o in top_level] == [section_id]
    assert specimen_id not in [o["id"] for o in top_level]
    assert (await client.get(f"/objects/{section_id}")).json()["is_top_level"] is True

    await client.delete(f"/top-level-objects/{section_id}")
    assert (await client.get("/top-level-objects")).json() == []
    assert (await client.get(f"/objects/{section_id}")).json()["is_top_level"] is False


async def test_relation_closes_a_loop(client: AsyncClient) -> None:
    async def make(latex: str) -> str:
        resp = await client.post("/objects", json={"latex": latex})
        result: str = resp.json()["id"]
        return result

    p = await make("x^2 - 4x + 3")
    c = await make("companion matrix")
    char_poly = await make("CharacteristicPolynomial")
    companion = await make("CompanionMatrix")

    await client.post(
        "/relations",
        json={"operator_id": companion, "input_object_ids": [p], "output_object_ids": [c]},
    )
    await client.post(
        "/relations",
        json={"operator_id": char_poly, "input_object_ids": [c], "output_object_ids": [p]},
    )

    detail = (await client.get(f"/objects/{p}")).json()
    assert len(detail["as_input"]) == 1
    assert len(detail["as_output"]) == 1
    assert detail["as_output"][0]["inputs"][0]["object"]["id"] == c


async def test_delete_object_blocked_while_referenced(client: AsyncClient) -> None:
    async def make(latex: str) -> str:
        resp = await client.post("/objects", json={"latex": latex})
        result: str = resp.json()["id"]
        return result

    a = await make("A")
    op = await make("Inverse")
    b = await make("B")
    await client.post(
        "/relations",
        json={"operator_id": op, "input_object_ids": [a], "output_object_ids": [b]},
    )

    resp = await client.delete(f"/objects/{a}")
    assert resp.status_code == 400
