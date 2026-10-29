import datetime
import itertools
import uuid
from typing import Any

from httpx import AsyncClient

from monet_api.core.db import async_session
from monet_api.events.models import Event


async def _make(client: AsyncClient, latex: str, **extra: object) -> str:
    resp = await client.post("/objects", json={"latex": latex, **extra})
    assert resp.status_code == 201, resp.text
    object_id: str = resp.json()["id"]
    return object_id


async def _relate(client: AsyncClient, operator: str, inputs: list[str], outputs: list[str]) -> str:
    resp = await client.post(
        "/relations",
        json={"operator_id": operator, "input_object_ids": inputs, "output_object_ids": outputs},
    )
    assert resp.status_code == 201, resp.text
    relation_id: str = resp.json()["id"]
    return relation_id


async def _page(client: AsyncClient, **params: str | int) -> dict[str, Any]:
    resp = await client.get("/objects", params=params)
    assert resp.status_code == 200, resp.text
    body: dict[str, Any] = resp.json()
    return body


async def _latex_found(client: AsyncClient, q: str) -> list[str]:
    return [o["latex"] for o in (await _page(client, q=q))["items"]]


async def test_objects_are_paged_with_an_honest_total(client: AsyncClient) -> None:
    made = [await _make(client, f"m_{{{index:02d}}}") for index in range(12)]

    first = await _page(client, limit=5)
    assert first["total"] == 12
    assert len(first["items"]) == 5
    assert (await _page(client, limit=5, offset=20)) == {"items": [], "total": 12}

    walked = [
        o["id"]
        for offset in (0, 5, 10)
        for o in (await _page(client, limit=5, offset=offset))["items"]
    ]
    assert len(walked) == len(set(walked))
    assert sorted(walked) == sorted(made)


async def test_a_page_is_capped(client: AsyncClient) -> None:
    assert (await client.get("/objects", params={"limit": 201})).status_code == 422
    assert (await client.get("/objects", params={"offset": -1})).status_code == 422


async def test_text_search_reads_through_notation(client: AsyncClient) -> None:
    await _make(client, "\\text{Characteristic Polynomial}")
    await _make(client, "x^{2} - 4 x + 3")
    await _make(client, "\\mathrm{3}_{1}", description="The trefoil, the simplest knot.")

    assert await _latex_found(client, "characteristic") == ["\\text{Characteristic Polynomial}"]
    assert await _latex_found(client, "POLYNOMIAL") == ["\\text{Characteristic Polynomial}"]
    assert await _latex_found(client, "x^2") == ["x^{2} - 4 x + 3"]
    assert await _latex_found(client, "x^{2}") == ["x^{2} - 4 x + 3"]
    assert await _latex_found(client, "trefoil") == ["\\mathrm{3}_{1}"]
    assert await _latex_found(client, "zzzz") == []


async def test_text_search_ranks_a_prefix_first(client: AsyncClient) -> None:
    await _make(client, "\\text{Characteristic Polynomial}")
    await _make(client, "\\text{Polynomial}")
    await _make(client, "\\text{Polynomial Ring}")

    assert await _latex_found(client, "poly") == [
        "\\text{Polynomial}",
        "\\text{Polynomial Ring}",
        "\\text{Characteristic Polynomial}",
    ]


async def test_text_search_treats_wildcards_literally(client: AsyncClient) -> None:
    await _make(client, "x_{1}")
    await _make(client, "y")

    assert await _latex_found(client, "_") == ["x_{1}"]
    assert await _latex_found(client, "%") == []


async def test_text_search_combines_with_a_role(client: AsyncClient) -> None:
    determinant = await _make(client, "\\text{Determinant}")
    await _make(client, "\\text{Determinant Note}")
    await _relate(client, determinant, [await _make(client, "A")], [await _make(client, "1")])

    found = await _page(client, q="determinant", role="map")
    assert [o["id"] for o in found["items"]] == [determinant]
    assert found["total"] == 1


async def test_detail_caps_each_operator_and_keeps_its_total(client: AsyncClient) -> None:
    one = await _make(client, "1")
    determinant = await _make(client, "\\text{Determinant}")
    trace = await _make(client, "\\text{Trace}")
    for index in range(7):
        await _relate(client, determinant, [await _make(client, f"M_{{{index}}}")], [one])
    await _relate(client, trace, [await _make(client, "N")], [one])

    detail = (await client.get(f"/objects/{one}")).json()
    groups = {g["operator"]["id"]: g for g in detail["as_output"]}
    assert len(groups[determinant]["relations"]) == 3
    assert groups[determinant]["total"] == 7
    assert len(groups[trace]["relations"]) == 1
    assert detail["relation_count"] == 8


async def test_an_operators_own_relations_are_capped_separately(client: AsyncClient) -> None:
    determinant = await _make(client, "\\text{Determinant}")
    for index in range(12):
        await _relate(
            client, determinant, [await _make(client, f"M_{{{index}}}")], [await _make(client, "d")]
        )

    (group,) = (await client.get(f"/objects/{determinant}")).json()["as_operator"]
    assert len(group["relations"]) == 10
    assert group["total"] == 12


async def test_a_capped_group_is_walked_to_the_end_without_repeats(client: AsyncClient) -> None:
    one = await _make(client, "1")
    determinant = await _make(client, "\\text{Determinant}")
    for index in range(7):
        await _relate(client, determinant, [await _make(client, f"M_{{{index}}}")], [one])

    (group,) = (await client.get(f"/objects/{one}")).json()["as_output"]
    shown = [r["id"] for r in group["relations"]]
    rest = await client.get(
        f"/objects/{one}/relations",
        params={"side": "output", "operator_id": determinant, "offset": len(shown), "limit": 20},
    )
    assert rest.status_code == 200
    assert rest.json()["total"] == 7
    walked = [*shown, *(r["id"] for r in rest.json()["items"])]
    assert len(walked) == len(set(walked)) == 7


async def test_operators_beyond_the_cap_are_still_counted(client: AsyncClient) -> None:
    x = await _make(client, "x")
    operators = [await _make(client, f"\\text{{Op {index:02d}}}") for index in range(32)]
    for operator in operators:
        await _relate(client, operator, [x], [await _make(client, "y")])

    groups = (await client.get(f"/objects/{x}")).json()["as_input"]
    assert len(groups) == 32
    assert sum(1 for g in groups if g["relations"]) == 30
    assert all(g["total"] == 1 for g in groups)


def _operators(cycle: list[dict[str, Any]]) -> list[str]:
    return [step["relation"]["operator"]["id"] for step in cycle]


async def _loops(client: AsyncClient, object_id: str, **params: str) -> list[list[dict[str, Any]]]:
    resp = await client.get(f"/objects/{object_id}/loops", params=params)
    assert resp.status_code == 200, resp.text
    loops: list[list[dict[str, Any]]] = resp.json()
    return loops


async def test_a_loop_through_an_object_is_found(client: AsyncClient) -> None:
    p = await _make(client, "x^{2} - 1")
    d = await _make(client, "D")
    companion = await _make(client, "\\text{Companion Matrix}")
    charpoly = await _make(client, "\\text{Characteristic Polynomial}")
    await _relate(client, companion, [p], [d])
    await _relate(client, charpoly, [d], [p])

    (cycle,) = await _loops(client, p)
    assert _operators(cycle) == [companion, charpoly]
    assert cycle[0]["source"]["id"] == p
    assert cycle[-1]["target"]["id"] == p


async def test_an_object_that_is_its_own_inverse_closes_a_loop(client: AsyncClient) -> None:
    d = await _make(client, "D")
    inverse = await _make(client, "\\text{Inverse}")
    await _relate(client, inverse, [d], [d])

    (cycle,) = await _loops(client, d)
    assert len(cycle) == 1


async def test_sharing_an_output_is_not_a_loop(client: AsyncClient) -> None:
    a, d, p = await _make(client, "A"), await _make(client, "D"), await _make(client, "P")
    charpoly = await _make(client, "\\text{Characteristic Polynomial}")
    await _relate(client, charpoly, [a], [p])
    await _relate(client, charpoly, [d], [p])

    assert await _loops(client, a) == []
    assert await _loops(client, p) == []


async def test_a_loop_may_leave_through_any_input(client: AsyncClient) -> None:
    a, p, d = await _make(client, "A"), await _make(client, "P"), await _make(client, "D")
    companion = await _make(client, "\\text{Companion}")
    charpoly = await _make(client, "\\text{Characteristic Polynomial}")
    await _relate(client, companion, [p, a], [d])
    await _relate(client, charpoly, [d], [a])

    assert len(await _loops(client, a)) == 1


async def test_loops_longer_than_six_steps_are_not_followed(client: AsyncClient) -> None:
    step = await _make(client, "\\text{Step}")
    start = await _make(client, "s")
    short = [await _make(client, f"a_{{{index}}}") for index in range(5)]
    long = [await _make(client, f"b_{{{index}}}") for index in range(6)]
    for chain in (short, long):
        nodes = [start, *chain, start]
        for source, target in itertools.pairwise(nodes):
            await _relate(client, step, [source], [target])

    (cycle,) = await _loops(client, start)
    assert len(cycle) == 6


async def test_at_most_three_loops_are_shown(client: AsyncClient) -> None:
    p = await _make(client, "P")
    there = await _make(client, "\\text{There}")
    back = await _make(client, "\\text{Back}")
    for index in range(4):
        middle = await _make(client, f"m_{{{index}}}")
        await _relate(client, there, [p], [middle])
        await _relate(client, back, [middle], [p])

    assert len(await _loops(client, p)) == 3


async def test_loops_can_be_asked_for_through_one_relation(client: AsyncClient) -> None:
    p = await _make(client, "P")
    there = await _make(client, "\\text{There}")
    back = await _make(client, "\\text{Back}")
    firsts = []
    for index in range(4):
        middle = await _make(client, f"m_{{{index}}}")
        firsts.append(await _relate(client, there, [p], [middle]))
        await _relate(client, back, [middle], [p])

    (cycle,) = await _loops(client, p, via=firsts[-1])
    assert cycle[0]["relation"]["id"] == firsts[-1]


async def test_the_map_draws_around_its_focus_and_counts_what_it_leaves_out(
    client: AsyncClient,
) -> None:
    one = await _make(client, "1")
    determinant = await _make(client, "\\text{Determinant}")
    for index in range(80):
        await _relate(client, determinant, [await _make(client, f"M_{{{index}}}")], [one])

    mapped = (await client.get("/relations", params={"focus": one})).json()
    assert 0 < len(mapped["relations"]) < 80
    assert mapped["omitted"] == 80 - len(mapped["relations"])


async def test_the_map_reaches_further_with_depth(client: AsyncClient) -> None:
    determinant = await _make(client, "\\text{Determinant}")
    degree = await _make(client, "\\text{Degree}")
    near, value, far = await _make(client, "A"), await _make(client, "3"), await _make(client, "P")
    await _relate(client, determinant, [near], [value])
    await _relate(client, degree, [far], [value])

    around = (await client.get("/relations", params={"focus": near})).json()
    assert [r["operator"]["id"] for r in around["relations"]] == [determinant]
    wider = (await client.get("/relations", params={"focus": near, "depth": 2})).json()
    assert len(wider["relations"]) == 2


async def test_an_unfocused_map_starts_from_the_busiest_objects(client: AsyncClient) -> None:
    determinant = await _make(client, "\\text{Determinant}")
    one = await _make(client, "1")
    for index in range(3):
        await _relate(client, determinant, [await _make(client, f"M_{{{index}}}")], [one])

    mapped = (await client.get("/relations")).json()
    assert {r["outputs"][0]["object"]["id"] for r in mapped["relations"]} == {one}
    assert len(mapped["relations"]) + mapped["omitted"] == 3


async def test_focusing_on_a_missing_object_is_404(client: AsyncClient) -> None:
    missing = str(uuid.UUID(int=0))
    assert (await client.get("/relations", params={"focus": missing})).status_code == 404
    assert (await client.get(f"/objects/{missing}/loops")).status_code == 404
    assert (
        await client.get(f"/objects/{missing}/relations", params={"side": "input"})
    ).status_code == 404


async def test_the_feed_pages_back_past_events_sharing_a_moment(client: AsyncClient) -> None:
    subject = await _make(client, "A")
    moment = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)
    async with async_session() as session:
        for _ in range(5):
            session.add(Event(at=moment, kind="object_created", subject_id=uuid.UUID(subject)))
        await session.commit()

    seen: list[str] = []
    before: str | None = None
    while True:
        params: dict[str, Any] = {"limit": 2, **({} if before is None else {"before": before})}
        page = (await client.get("/events", params=params)).json()
        if not page:
            break
        seen.extend(entry["id"] for entry in page)
        before = page[-1]["id"]
    assert len(seen) == len(set(seen)) == 6
