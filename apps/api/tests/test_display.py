"""Tests for the GUI-only tables: membership sectioning, the contents tree, operator display."""

from httpx import AsyncClient


async def make_object(client: AsyncClient, latex: str) -> str:
    resp = await client.post("/objects", json={"latex": latex})
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
    client: AsyncClient,
    operator: str,
    *,
    template: str | None = None,
    hidden: bool = False,
    membership: bool = False,
) -> None:
    resp = await client.put(
        f"/operator-displays/{operator}",
        json={
            "template": template,
            "hidden_by_default": hidden,
            "is_membership": membership,
        },
    )
    assert resp.status_code == 200


async def test_membership_relations_become_sections_not_rows(client: AsyncClient) -> None:
    element_of = await make_object(client, "\\text{Element Of}")
    inverse = await make_object(client, "\\text{Inverse}")
    matrices = await make_object(client, "\\text{Matrices}")
    a = await make_object(client, "A")
    b = await make_object(client, "B")

    await set_display(client, element_of, membership=True)
    await relate(client, element_of, [a], [matrices])
    await relate(client, inverse, [a], [b])

    detail = (await client.get(f"/objects/{a}")).json()
    assert [s["id"] for s in detail["sections"]] == [matrices]
    # Only the Inverse relation is left as an ordinary row.
    assert [r["operator"]["id"] for r in detail["as_input"]] == [inverse]


async def test_membership_is_driven_by_the_flag_not_the_name(client: AsyncClient) -> None:
    """An operator called Element Of but not flagged stays an ordinary relation."""
    element_of = await make_object(client, "\\text{Element Of}")
    matrices = await make_object(client, "\\text{Matrices}")
    a = await make_object(client, "A")

    await relate(client, element_of, [a], [matrices])

    detail = (await client.get(f"/objects/{a}")).json()
    assert detail["sections"] == []
    assert [r["operator"]["id"] for r in detail["as_input"]] == [element_of]


async def test_section_members_are_listed_in_latex_order(client: AsyncClient) -> None:
    element_of = await make_object(client, "\\text{Element Of}")
    matrices = await make_object(client, "\\text{Matrices}")
    await set_display(client, element_of, membership=True)

    c = await make_object(client, "C")
    a = await make_object(client, "A")
    b = await make_object(client, "B")
    outsider = await make_object(client, "Z")
    for member in (c, a, b):
        await relate(client, element_of, [member], [matrices])

    detail = (await client.get(f"/objects/{matrices}")).json()
    assert [m["latex"] for m in detail["members"]] == ["A", "B", "C"]
    assert outsider not in [m["id"] for m in detail["members"]]


async def test_contents_tree_nests_sections_and_omits_specimens(client: AsyncClient) -> None:
    element_of = await make_object(client, "\\text{Element Of}")
    await set_display(client, element_of, membership=True)

    linear_algebra = await make_object(client, "\\text{Linear Algebra}")
    matrices = await make_object(client, "\\text{Matrices}")
    a = await make_object(client, "A")

    await relate(client, element_of, [matrices], [linear_algebra])
    await relate(client, element_of, [a], [matrices])
    await client.put(f"/top-level-objects/{linear_algebra}")

    contents = (await client.get("/contents")).json()
    assert [node["id"] for node in contents] == [linear_algebra]
    assert [node["id"] for node in contents[0]["children"]] == [matrices]
    # The specimen is a member of Matrices, but has no members itself, so it is not a section
    # and belongs on Matrices' own page rather than in the table of contents.
    assert contents[0]["children"][0]["children"] == []
    assert contents[0]["children"][0]["member_count"] == 1


async def test_contents_tree_survives_a_cycle(client: AsyncClient) -> None:
    element_of = await make_object(client, "\\text{Element Of}")
    await set_display(client, element_of, membership=True)

    first = await make_object(client, "\\text{First}")
    second = await make_object(client, "\\text{Second}")
    await relate(client, element_of, [second], [first])
    await relate(client, element_of, [first], [second])
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

    rows = (await client.get("/relations")).json()
    by_operator = {r["operator"]["id"]: r["display"] for r in rows}
    assert by_operator[add]["template"] == "{in0} + {in1} = {out0}"
    # hidden_by_default is advice, not a filter — the relation is still returned.
    assert by_operator[add]["hidden_by_default"] is True
    assert by_operator[other] is None


async def test_operator_display_defaults_when_unconfigured(client: AsyncClient) -> None:
    operator = await make_object(client, "\\text{Inverse}")
    resp = await client.get(f"/operator-displays/{operator}")
    assert resp.status_code == 200
    assert resp.json() == {
        "operator_id": operator,
        "template": None,
        "hidden_by_default": False,
        "is_membership": False,
    }


async def test_operator_display_requires_an_existing_object(client: AsyncClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert (await client.get(f"/operator-displays/{missing}")).status_code == 404


async def test_delete_object_on_contents_page_succeeds(client: AsyncClient) -> None:
    """A GUI row must never be what blocks deleting its own object."""
    obj = await make_object(client, "\\text{Matrices}")
    await client.put(f"/top-level-objects/{obj}")
    await set_display(client, obj, template="{in0} = {out0}")

    assert (await client.delete(f"/objects/{obj}")).status_code == 204
    assert (await client.get("/top-level-objects")).json() == []
