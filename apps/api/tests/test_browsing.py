from httpx import AsyncClient

from tests.test_display import make_object, relate, set_display


async def _section_with(client: AsyncClient, latex: str, count: int) -> tuple[str, list[str]]:
    element_of = await make_object(client, "\\text{Element Of}")
    await set_display(client, element_of, membership=True)
    section = await make_object(client, latex)
    members = []
    for index in range(count):
        member = await make_object(client, f"m_{{{index:03d}}}")
        await relate(client, element_of, [member], [section])
        members.append(member)
    return section, members


async def test_members_are_capped_but_the_total_is_honest(client: AsyncClient) -> None:
    section, members = await _section_with(client, "\\text{Matrices}", 60)

    detail = (await client.get(f"/objects/{section}")).json()
    assert len(detail["members"]) == 50
    assert detail["members_total"] == len(members)


async def test_the_rest_of_a_section_can_be_paged_through(client: AsyncClient) -> None:
    section, members = await _section_with(client, "\\text{Matrices}", 60)

    first = (await client.get(f"/objects/{section}/members?offset=0&limit=50")).json()
    second = (await client.get(f"/objects/{section}/members?offset=50&limit=50")).json()
    assert len(first) == 50
    assert len(second) == 10
    walked = [row["id"] for row in [*first, *second]]
    assert sorted(walked) == sorted(members)
    assert len(set(walked)) == len(walked)


async def test_objects_can_be_searched_and_looked_up_exactly(client: AsyncClient) -> None:
    await make_object(client, "x^{2}-4x+3")
    await make_object(client, "\\text{Characteristic Polynomial}")

    found = (await client.get("/objects?q=Characteristic")).json()
    assert [o["latex"] for o in found] == ["\\text{Characteristic Polynomial}"]

    spaced = (await client.get("/objects", params={"latex": "x^{2} - 4 x + 3"})).json()
    assert [o["latex"] for o in spaced] == ["x^{2}-4x+3"]

    assert (await client.get("/objects", params={"latex": "y"})).json() == []


async def test_relations_can_be_scoped_to_a_neighbourhood(client: AsyncClient) -> None:
    operator = await make_object(client, "\\text{Determinant}")
    near = await make_object(client, "A")
    value = await make_object(client, "3")
    far_operator = await make_object(client, "\\text{Degree}")
    far = await make_object(client, "P")
    await relate(client, operator, [near], [value])
    await relate(client, far_operator, [far], [value])

    everything = (await client.get("/relations")).json()
    assert len(everything) == 2

    around = (await client.get(f"/relations?focus={near}&depth=1")).json()
    assert [r["operator"]["latex"] for r in around] == ["\\text{Determinant}"]

    wider = (await client.get(f"/relations?focus={near}&depth=2")).json()
    assert len(wider) == 2


async def test_focusing_on_an_object_that_is_not_there_is_a_404(client: AsyncClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert (await client.get(f"/relations?focus={missing}")).status_code == 404
