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


async def test_deleting_an_object_deletes_the_relations_it_is_in(client: AsyncClient) -> None:
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
    assert len((await client.get("/relations")).json()) == 1

    assert (await client.delete(f"/objects/{a}")).status_code == 204

    assert (await client.get("/relations")).json() == []
    assert (await client.get(f"/objects/{a}")).status_code == 404
    assert (await client.get(f"/objects/{b}")).status_code == 200
    assert (await client.get(f"/objects/{op}")).status_code == 200


async def test_deleting_an_operator_deletes_the_relations_it_operates(
    client: AsyncClient,
) -> None:
    async def make(latex: str) -> str:
        resp = await client.post("/objects", json={"latex": latex})
        result: str = resp.json()["id"]
        return result

    a, op, b = await make("A"), await make("Inverse"), await make("B")
    await client.post(
        "/relations",
        json={"operator_id": op, "input_object_ids": [a], "output_object_ids": [b]},
    )

    assert (await client.delete(f"/objects/{op}")).status_code == 204

    assert (await client.get("/relations")).json() == []
    assert (await client.get(f"/objects/{a}")).status_code == 200


async def test_deleting_a_section_object_clears_its_contents_entry(client: AsyncClient) -> None:
    resp = await client.post("/objects", json={"latex": "\\text{Matrices}"})
    section = resp.json()["id"]
    await client.put(f"/top-level-objects/{section}")
    assert len((await client.get("/top-level-objects")).json()) == 1

    assert (await client.delete(f"/objects/{section}")).status_code == 204
    assert (await client.get("/top-level-objects")).json() == []


async def test_object_carries_an_image_and_ordered_references(client: AsyncClient) -> None:
    resp = await client.post(
        "/objects",
        json={
            "latex": "3_1",
            "image_url": "/knots/2-3.svg",
            "references": [
                {"label": "Knot Atlas", "url": "https://katlas.org/wiki/3_1"},
                {"label": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Trefoil_knot"},
            ],
        },
    )
    assert resp.status_code == 201
    obj_id = resp.json()["id"]

    detail = (await client.get(f"/objects/{obj_id}")).json()
    assert detail["image_url"] == "/knots/2-3.svg"
    assert [(r["label"], r["url"]) for r in detail["references"]] == [
        ("Knot Atlas", "https://katlas.org/wiki/3_1"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Trefoil_knot"),
    ]


async def test_updating_references_replaces_them(client: AsyncClient) -> None:
    resp = await client.post(
        "/objects",
        json={"latex": "K", "references": [{"label": "one", "url": "https://one.example"}]},
    )
    obj_id = resp.json()["id"]

    await client.patch(
        f"/objects/{obj_id}",
        json={"latex": "K", "references": [{"label": "two", "url": "https://two.example"}]},
    )
    assert [r["label"] for r in (await client.get(f"/objects/{obj_id}")).json()["references"]] == [
        "two"
    ]

    await client.patch(f"/objects/{obj_id}", json={"latex": "K"})
    assert (await client.get(f"/objects/{obj_id}")).json()["references"] == []


async def test_deleting_an_object_takes_its_references_with_it(client: AsyncClient) -> None:
    resp = await client.post(
        "/objects",
        json={"latex": "K", "references": [{"label": "one", "url": "https://one.example"}]},
    )
    obj_id = resp.json()["id"]

    assert (await client.delete(f"/objects/{obj_id}")).status_code == 204
    assert (await client.get(f"/objects/{obj_id}")).status_code == 404


async def test_a_url_that_is_not_linkable_is_refused(client: AsyncClient) -> None:
    for url in ("javascript:alert(1)", "//evil.example", "data:text/html;base64,PHNjcmlwdD4="):
        resp = await client.post(
            "/objects", json={"latex": "K", "references": [{"label": "x", "url": url}]}
        )
        assert resp.status_code == 400, url

        resp = await client.post("/objects", json={"latex": "K", "image_url": url})
        assert resp.status_code == 400, url

    resp = await client.post("/objects", json={"latex": "K", "image_url": "/knots/2-3.svg"})
    assert resp.status_code == 201
