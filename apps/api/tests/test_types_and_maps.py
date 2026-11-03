from typing import Any

from httpx import AsyncClient

from tests.conftest import editor_key


async def make(client: AsyncClient, latex: str, **extra: object) -> str:
    resp = await client.post("/objects", json={"latex": latex, **extra})
    assert resp.status_code == 201, resp.text
    result: str = resp.json()["id"]
    return result


async def detail(client: AsyncClient, object_id: str) -> dict[str, Any]:
    resp = await client.get(f"/objects/{object_id}")
    assert resp.status_code == 200
    result: dict[str, Any] = resp.json()
    return result


async def test_contributing_a_type_an_instance_and_a_map(client: AsyncClient) -> None:
    root = await make(client, "\\text{Mathematical Objects}", as_type={})
    matrices = await make(
        client, "\\text{Matrices}", as_type={"data_kind": "matrix", "supertype_ids": [root]}
    )
    integers = await make(
        client, "\\text{Integers}", as_type={"data_kind": "int", "supertype_ids": [root]}
    )
    noether = await editor_key(client, "Noether", 1)
    created = await client.post(
        "/objects",
        json={"latex": "A", "facets": [{"type_id": matrices, "data": {"matrix": [[{"int": 1}]]}}]},
        headers=noether,
    )
    a = created.json()["id"]
    determinant = await make(
        client,
        "\\text{Determinant}",
        signatures=[{"domain_id": matrices, "codomain_id": integers}],
    )

    as_type = await detail(client, matrices)
    assert as_type["roles"] == ["type"]
    assert as_type["as_type"] == {"data_kind": "matrix", "data_kinds": ["matrix"]}
    assert [o["id"] for o in as_type["supertypes"]] == [root]
    assert as_type["instance_count"] == 1
    assert (await detail(client, root))["as_type"]["data_kinds"] == ["int", "matrix"]
    assert [o["id"] for o in as_type["maps_from"]] == [determinant]
    assert as_type["maps_to"] == []
    assert [o["id"] for o in (await detail(client, integers))["maps_to"]] == [determinant]

    as_map = await detail(client, determinant)
    assert as_map["roles"] == ["map"]
    assert [(s["domain"]["id"], s["codomain"]["id"]) for s in as_map["signatures"]] == [
        (matrices, integers)
    ]

    as_instance = await detail(client, a)
    assert as_instance["roles"] == ["instance"]
    assert [(f["type"]["id"], f["data"]) for f in as_instance["facets"]] == [
        (matrices, {"matrix": [[{"int": 1}]]})
    ]
    assert as_instance["provenance"]["contributor"] == "Noether"

    types = (await client.get("/objects", params={"role": "type"})).json()["items"]
    assert sorted(o["id"] for o in types) == sorted([root, matrices, integers])
    maps = (await client.get("/objects", params={"role": "map"})).json()["items"]
    assert [o["id"] for o in maps] == [determinant]
    instances = (await client.get("/objects", params={"role": "instance"})).json()["items"]
    assert [o["id"] for o in instances] == [a]


async def test_a_map_can_have_several_signatures(client: AsyncClient) -> None:
    polys = await make(client, "\\text{Polynomials}", as_type={"data_kind": "poly"})
    functions = await make(client, "\\text{Holomorphic Functions}", as_type={})
    diff = await make(
        client,
        "\\text{Diff}",
        signatures=[{"domain_id": polys, "codomain_id": polys}],
    )
    resp = await client.post(
        f"/objects/{diff}/signatures", json={"domain_id": functions, "codomain_id": functions}
    )
    assert resp.status_code == 201
    signatures = (await detail(client, diff))["signatures"]
    assert sorted(s["domain"]["id"] for s in signatures) == sorted([polys, functions])

    assert (await client.delete(f"/signatures/{resp.json()['id']}")).status_code == 204
    assert len((await detail(client, diff))["signatures"]) == 1


async def test_an_object_can_hold_a_facet_per_type(client: AsyncClient) -> None:
    data = {"poly": {"var": "x", "degree": 2, "coeffs": {"0": {"int": 1}, "1": {"int": 0}}}}
    polys = await make(client, "\\text{Polynomials}", as_type={"data_kind": "poly"})
    functions = await make(client, "\\text{Real Functions}", as_type={})
    p = await make(client, "x^{2} + 1", facets=[{"type_id": polys, "data": data}])

    resp = await client.put(f"/objects/{p}/facets/{functions}", json={"data": data})
    assert resp.status_code == 200
    assert sorted(f["type"]["id"] for f in (await detail(client, p))["facets"]) == sorted(
        [polys, functions]
    )

    assert (await client.delete(f"/objects/{p}/facets/{functions}")).status_code == 204
    assert [f["type"]["id"] for f in (await detail(client, p))["facets"]] == [polys]


async def test_a_section_is_not_a_type(client: AsyncClient) -> None:
    topic = await make(client, "\\text{Linear Algebra}")
    await make(client, "\\text{Matrix Operations}", sections=[topic])
    assert (await detail(client, topic))["roles"] == ["section"]
    types = (await client.get("/objects", params={"role": "type"})).json()["items"]
    assert topic not in [o["id"] for o in types]
    sections = (await client.get("/objects", params={"role": "section"})).json()["items"]
    assert [o["id"] for o in sections] == [topic]


async def test_creating_with_a_missing_target_creates_nothing(client: AsyncClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    for body in (
        {"latex": "A", "facets": [{"type_id": missing}]},
        {"latex": "A", "as_type": {"supertype_ids": [missing]}},
        {"latex": "A", "signatures": [{"domain_id": missing, "codomain_id": missing}]},
        {"latex": "A", "sections": [missing]},
    ):
        assert (await client.post("/objects", json=body)).status_code == 404
    assert (await client.get("/objects")).json() == {"items": [], "total": 0}


async def test_relations_carry_their_provenance(client: AsyncClient) -> None:
    operator = await make(client, "\\text{Inverse}")
    matrix = await make(client, "B")
    resp = await client.post(
        "/relations",
        json={
            "operator_id": operator,
            "input_object_ids": [matrix],
            "output_object_ids": [matrix],
            "contributor": "someone else",
        },
        headers=await editor_key(client, "Hilbert", 2),
    )
    provenance = resp.json()["provenance"]
    assert provenance["contributor"] == "Hilbert"
    assert provenance["source"] == "manual"
    listed = (await detail(client, matrix))["as_input"][0]["relations"][0]
    assert listed["provenance"]["contributor"] == "Hilbert"


async def test_query_by_description(client: AsyncClient) -> None:
    singular = await make(client, "S", description="Singular: its rows are proportional.")
    await make(client, "A", description="A symmetric matrix.")
    await make(client, "B")
    resp = await client.get("/objects", params={"description_contains": "SINGULAR"})
    assert [o["id"] for o in resp.json()["items"]] == [singular]
    resp = await client.get("/objects", params={"description_contains": "50%_"})
    assert resp.json()["items"] == []


async def test_a_section_nests_its_types_and_lists_its_maps_apart(client: AsyncClient) -> None:
    analysis = await make(client, "\\text{Analysis}")
    algebra = await make(client, "\\text{Algebra}")
    root = await make(client, "\\text{Mathematical Objects}", as_type={})
    real = await make(
        client,
        "\\text{Real Functions}",
        as_type={"supertype_ids": [root]},
        sections=[analysis],
    )
    elementary = await make(
        client, "\\text{Elementary Functions}", as_type={"supertype_ids": [real]}
    )
    rational = await make(
        client,
        "\\text{Rational Functions}",
        as_type={"supertype_ids": [elementary]},
        sections=[analysis],
    )
    polys = await make(
        client,
        "\\text{Polynomials}",
        as_type={"data_kind": "poly", "supertype_ids": [rational]},
        sections=[analysis, algebra],
    )
    operations = await make(client, "\\text{Analysis Operations}", sections=[analysis])
    derivative = await make(client, "\\text{Derivative}", sections=[operations])
    data = {"poly": {"var": "x", "degree": 1, "coeffs": {"1": {"int": 1}}}}
    await make(client, "x", facets=[{"type_id": polys, "data": data}])

    section = (await client.get(f"/objects/{analysis}/section")).json()
    nested = {t["id"]: (t["supertype_ids"], t["instance_count"]) for t in section["types"]}
    assert nested == {real: ([], 1), rational: ([real], 1), polys: ([rational], 1)}
    elsewhere_of = {t["id"]: [e["id"] for e in t["elsewhere"]] for t in section["types"]}
    assert elsewhere_of == {real: [], rational: [elementary], polys: []}
    assert section["entries"] == []
    assert [(s["id"], [e["id"] for e in s["entries"]]) for s in section["subsections"]] == [
        (operations, [derivative])
    ]

    elsewhere = (await client.get(f"/objects/{algebra}/section")).json()["types"]
    assert [[e["id"] for e in t["elsewhere"]] for t in elsewhere] == [[rational]]
    assert (await client.get(f"/objects/{root}/section")).status_code == 200
    missing = "00000000-0000-0000-0000-000000000000"
    assert (await client.get(f"/objects/{missing}/section")).status_code == 404


async def test_an_object_shows_the_types_its_own_imply(client: AsyncClient) -> None:
    root = await make(client, "\\text{Mathematical Objects}", as_type={})
    real = await make(client, "\\text{Real Functions}", as_type={"supertype_ids": [root]})
    rational = await make(client, "\\text{Rational Functions}", as_type={"supertype_ids": [real]})
    polys = await make(
        client, "\\text{Polynomials}", as_type={"data_kind": "poly", "supertype_ids": [rational]}
    )
    data = {"poly": {"var": "x", "degree": 1, "coeffs": {"1": {"int": 1}}}}
    x = await make(client, "x", facets=[{"type_id": polys, "data": data}])

    assert sorted(t["id"] for t in (await detail(client, x))["implied_types"]) == sorted(
        [real, rational]
    )
    assert (await detail(client, real))["instance_count"] == 1
