from httpx import AsyncClient


async def make_object(client: AsyncClient, latex: str, **extra: object) -> str:
    resp = await client.post("/objects", json={"latex": latex, **extra})
    assert resp.status_code == 201, resp.text
    result: str = resp.json()["id"]
    return result


async def relate(client: AsyncClient, operator: str, inputs: list[str], outputs: list[str]) -> None:
    resp = await client.post(
        "/relations",
        json={
            "operator_id": operator,
            "input_object_ids": inputs,
            "output_object_ids": outputs,
        },
    )
    assert resp.status_code == 201


async def set_display(
    client: AsyncClient, operator: str, *, template: str | None = None, hidden: bool = False
) -> None:
    resp = await client.put(
        f"/operator-displays/{operator}",
        json={"template": template, "hidden_by_default": hidden},
    )
    assert resp.status_code == 200


async def test_filing_under_a_section_is_editorial_not_a_relation(client: AsyncClient) -> None:
    linear_algebra = await make_object(client, "\\text{Linear Algebra}")
    inverse = await make_object(client, "\\text{Inverse}", sections=[linear_algebra])

    detail = (await client.get(f"/objects/{inverse}")).json()
    assert [s["id"] for s in detail["sections"]] == [linear_algebra]
    assert detail["as_input"] == []
    assert detail["relation_count"] == 0

    section = (await client.get(f"/objects/{linear_algebra}")).json()
    assert section["filed_count"] == 1
    assert section["roles"] == ["section"]
    filed = (await client.get("/objects", params={"filed_under": linear_algebra})).json()
    assert [o["id"] for o in filed["items"]] == [inverse]


async def test_filed_objects_are_listed_in_latex_order(client: AsyncClient) -> None:
    section = await make_object(client, "\\text{Operations}")
    for latex in ("C", "A", "B"):
        await make_object(client, latex, sections=[section])
    await make_object(client, "Z")

    filed = (await client.get("/objects", params={"filed_under": section})).json()["items"]
    assert [o["latex"] for o in filed] == ["A", "B", "C"]


async def test_contents_tree_nests_sections_and_counts_instances(client: AsyncClient) -> None:
    linear_algebra = await make_object(client, "\\text{Linear Algebra}")
    matrices = await make_object(
        client, "\\text{Matrices}", as_type={"data_kind": "matrix"}, sections=[linear_algebra]
    )
    await make_object(
        client, "A", facets=[{"type_id": matrices, "data": {"matrix": [[{"int": 1}]]}}]
    )
    await client.put(f"/top-level-objects/{linear_algebra}")

    symmetric = await make_object(
        client,
        "\\text{Symmetric Matrices}",
        as_type={"data_kind": "matrix", "supertype_ids": [matrices]},
    )
    await make_object(
        client, "B", facets=[{"type_id": symmetric, "data": {"matrix": [[{"int": 2}]]}}]
    )
    await make_object(client, "\\text{Empty}", as_type={}, sections=[linear_algebra])
    await make_object(client, "\\text{Unfiled note}", sections=[linear_algebra])

    contents = (await client.get("/contents")).json()
    assert [node["id"] for node in contents] == [linear_algebra]
    children = {node["latex"]: node["member_count"] for node in contents[0]["children"]}
    assert children == {"\\text{Matrices}": 2, "\\text{Empty}": 0}
    assert contents[0]["member_count"] == 3


async def test_contents_tree_survives_a_cycle(client: AsyncClient) -> None:
    first = await make_object(client, "\\text{First}")
    second = await make_object(client, "\\text{Second}", sections=[first])
    third = await make_object(client, "\\text{Third}", sections=[second])
    await make_object(client, "\\text{Leaf}", sections=[third])
    await client.put(f"/top-level-objects/{first}")

    resp = await client.get("/contents")
    assert resp.status_code == 200

    seen: list[str] = []

    def walk(nodes: list[dict[str, object]]) -> None:
        for node in nodes:
            assert isinstance(node["id"], str)
            seen.append(node["id"])
            children = node["children"]
            assert isinstance(children, list)
            walk(children)

    walk(resp.json())
    assert len(seen) == len(set(seen))


async def test_operator_display_round_trip(client: AsyncClient) -> None:
    add = await make_object(client, "\\text{Matrix Addition}")
    other = await make_object(client, "\\text{Inverse}")
    a = await make_object(client, "A")
    b = await make_object(client, "B")
    c = await make_object(client, "C")

    await set_display(client, add, template="{in0} + {in1} = {out0}", hidden=True)
    await relate(client, add, [a, b], [c])
    await relate(client, other, [a], [c])

    stored = (await client.get(f"/operator-displays/{add}")).json()
    assert stored["template"] == "{in0} + {in1} = {out0}"
    assert stored["hidden_by_default"] is True

    groups = (await client.get(f"/objects/{a}")).json()["as_input"]
    by_operator = {g["operator"]["id"]: g["relations"][0]["display"] for g in groups}
    assert by_operator[add]["template"] == "{in0} + {in1} = {out0}"
    assert by_operator[add]["hidden_by_default"] is True
    assert by_operator[other] is None


async def test_operator_display_defaults_when_unconfigured(client: AsyncClient) -> None:
    operator = await make_object(client, "\\text{Inverse}")
    resp = await client.get(f"/operator-displays/{operator}")
    assert resp.status_code == 200
    assert resp.json() == {"operator_id": operator, "template": None, "hidden_by_default": False}


async def test_operator_display_requires_an_existing_object(client: AsyncClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert (await client.get(f"/operator-displays/{missing}")).status_code == 404


async def test_deleting_an_object_is_never_blocked_by_its_own_gui_rows(
    client: AsyncClient,
) -> None:
    obj = await make_object(client, "\\text{Matrices}")
    await client.put(f"/top-level-objects/{obj}")
    await set_display(client, obj, template="{in0} = {out0}")

    assert (await client.delete(f"/objects/{obj}")).status_code == 204
    assert (await client.get("/top-level-objects")).json() == []
