from typing import Any

from httpx import AsyncClient


async def make(client: AsyncClient, latex: str, **extra: object) -> str:
    resp = await client.post("/objects", json={"latex": latex, **extra})
    assert resp.status_code == 201, resp.text
    result: str = resp.json()["id"]
    return result


async def flag(client: AsyncClient, operator: str, flag_name: str) -> None:
    resp = await client.put(
        f"/operator-displays/{operator}",
        json={"template": None, "hidden_by_default": False, "is_membership": False}
        | {flag_name: True},
    )
    assert resp.status_code == 200


async def detail(client: AsyncClient, object_id: str) -> dict[str, Any]:
    resp = await client.get(f"/objects/{object_id}")
    assert resp.status_code == 200
    result: dict[str, Any] = resp.json()
    return result


async def structure(client: AsyncClient) -> dict[str, str]:
    ids = {
        "element_of": await make(client, "\\text{Element Of}"),
        "subset_of": await make(client, "\\text{Subset Of}"),
        "signature": await make(client, "\\text{Signature}"),
        "root": await make(client, "\\text{Mathematical Objects}"),
    }
    await flag(client, ids["element_of"], "is_membership")
    await flag(client, ids["subset_of"], "is_subtype")
    await flag(client, ids["signature"], "is_signature")
    return ids


async def test_contributing_a_type_an_instance_and_a_map(client: AsyncClient) -> None:
    ids = await structure(client)
    matrices = await make(client, "\\text{Matrices}", subtype_of=[ids["root"]])
    integers = await make(client, "\\text{Integers}", subtype_of=[ids["root"]])
    matrix = await make(
        client, "A", data={"matrix": [[{"int": 1}]]}, member_of=[matrices], contributor="Noether"
    )
    determinant = await make(
        client,
        "\\text{Determinant}",
        signature={"domain_id": matrices, "codomain_id": integers},
    )

    as_type = await detail(client, matrices)
    assert as_type["role"] == "type"
    assert [o["id"] for o in as_type["supertypes"]] == [ids["root"]]
    assert [o["id"] for o in as_type["members"]] == [matrix]
    assert [o["id"] for o in as_type["maps_from"]] == [determinant]
    assert as_type["maps_to"] == []
    assert [o["id"] for o in (await detail(client, integers))["maps_to"]] == [determinant]

    as_map = await detail(client, determinant)
    assert as_map["role"] == "map"
    assert as_map["signature"]["domain"]["id"] == matrices
    assert as_map["signature"]["codomain"]["id"] == integers

    as_instance = await detail(client, matrix)
    assert as_instance["role"] == "instance"
    assert [o["id"] for o in as_instance["sections"]] == [matrices]
    assert as_instance["provenance"]["contributor"] == "Noether"
    assert as_instance["provenance"]["source"] == "manual"

    types = (await client.get("/types")).json()
    assert sorted(o["id"] for o in types) == sorted([ids["root"], matrices, integers])


async def test_structural_relations_stay_out_of_the_ordinary_lists(client: AsyncClient) -> None:
    ids = await structure(client)
    matrices = await make(client, "\\text{Matrices}", subtype_of=[ids["root"]])
    trace = await make(
        client, "\\text{Trace}", signature={"domain_id": matrices, "codomain_id": matrices}
    )
    for object_id in (matrices, trace):
        found = await detail(client, object_id)
        assert found["as_input"] == []
        assert found["as_output"] == []


async def test_a_section_is_not_a_type(client: AsyncClient) -> None:
    ids = await structure(client)
    topic = await make(client, "\\text{Linear Algebra}")
    await make(client, "\\text{Matrix Operations}", member_of=[topic])
    assert (await detail(client, topic))["role"] == "section"
    assert topic not in [o["id"] for o in (await client.get("/types")).json()]
    assert (await detail(client, ids["root"]))["role"] == "instance"


async def test_creating_with_structure_needs_the_structural_operator(client: AsyncClient) -> None:
    target = await make(client, "\\text{Matrices}")
    resp = await client.post("/objects", json={"latex": "A", "member_of": [target]})
    assert resp.status_code == 400
    assert "membership" in resp.json()["detail"]
    assert len((await client.get("/objects")).json()) == 1


async def test_creating_with_a_missing_target_creates_nothing(client: AsyncClient) -> None:
    await structure(client)
    before = len((await client.get("/objects")).json())
    missing = "00000000-0000-0000-0000-000000000000"
    resp = await client.post("/objects", json={"latex": "A", "member_of": [missing]})
    assert resp.status_code == 404
    assert len((await client.get("/objects")).json()) == before


async def test_relations_carry_their_provenance(client: AsyncClient) -> None:
    operator = await make(client, "\\text{Inverse}")
    matrix = await make(client, "B")
    resp = await client.post(
        "/relations",
        json={
            "operator_id": operator,
            "input_object_ids": [matrix],
            "output_object_ids": [matrix],
            "contributor": "Hilbert",
        },
    )
    provenance = resp.json()["provenance"]
    assert provenance["contributor"] == "Hilbert"
    assert provenance["source"] == "manual"
    listed = (await detail(client, matrix))["as_input"][0]
    assert listed["provenance"]["contributor"] == "Hilbert"


async def test_query_by_description(client: AsyncClient) -> None:
    singular = await make(client, "S", description="Singular: its rows are proportional.")
    await make(client, "A", description="A symmetric matrix.")
    await make(client, "B")
    resp = await client.get("/objects/query", params={"description_contains": "SINGULAR"})
    assert [o["id"] for o in resp.json()] == [singular]
    resp = await client.get("/objects/query", params={"description_contains": "50%_"})
    assert resp.json() == []
