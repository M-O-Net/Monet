import json
import uuid
from typing import Any

from httpx import AsyncClient
from sqlalchemy import text

from monet_api.core.db import engine

Data = dict[str, Any]


def matrix(rows: list[list[int]]) -> Data:
    return {"matrix": [[{"int": cell} for cell in row] for row in rows]}


def square_plus(constant: int, var: str) -> Data:
    coeffs = {"0": {"int": constant}, "1": {"int": 0}, "2": {"int": 1}}
    return {"poly": {"var": var, "degree": 2, "coeffs": coeffs}}


async def make(client: AsyncClient, latex: str, **extra: object) -> str:
    resp = await client.post("/objects", json={"latex": latex, **extra})
    assert resp.status_code == 201, resp.text
    result: str = resp.json()["id"]
    return result


async def make_type(client: AsyncClient, latex: str, kind: str | None, *above: str) -> str:
    return await make(client, latex, as_type={"data_kind": kind, "supertype_ids": list(above)})


async def make_instance(client: AsyncClient, latex: str, type_id: str, data: Data) -> str:
    return await make(client, latex, facets=[{"type_id": type_id, "data": data}])


async def relate(client: AsyncClient, operator: str, inputs: list[str], outputs: list[str]) -> str:
    resp = await client.post(
        "/relations",
        json={"operator_id": operator, "input_object_ids": inputs, "output_object_ids": outputs},
    )
    assert resp.status_code == 201
    result: str = resp.json()["id"]
    return result


async def query(client: AsyncClient, **params: str | bool) -> list[str]:
    resp = await client.get("/objects/query", params=params)
    assert resp.status_code == 200, resp.text
    return sorted(o["id"] for o in resp.json())


async def taxonomy(client: AsyncClient) -> dict[str, str]:
    matrices = await make_type(client, "\\text{Matrices}", "matrix")
    symmetric = await make_type(client, "\\text{Symmetric Matrices}", "matrix", matrices)
    diagonal = await make_type(client, "\\text{Diagonal Matrices}", "matrix", symmetric)
    return {
        "matrices": matrices,
        "symmetric": symmetric,
        "diagonal": diagonal,
        "identity": await make_instance(client, "I", diagonal, matrix([[1, 0], [0, 1]])),
        "swap": await make_instance(client, "D", symmetric, matrix([[0, 1], [1, 0]])),
        "shear": await make_instance(client, "N", matrices, matrix([[1, 1], [0, 1]])),
    }


async def test_objects_sharing_latex_are_distinct(client: AsyncClient) -> None:
    polys = await make_type(client, "\\text{Polynomials}", "poly")
    first = await make_instance(client, "x^{2} + 1", polys, square_plus(1, "x"))
    second = await make_instance(client, "x^{2} + 1", polys, square_plus(1, "z"))
    third = await make(client, "x^{2} + 1")
    assert len({first, second, third}) == 3


async def test_data_belongs_to_one_object(client: AsyncClient) -> None:
    integers = await make_type(client, "\\text{Integers}", "int")
    numbers = await make_type(client, "\\text{Numbers}", None)
    held = await make_instance(client, "17", integers, {"int": 17})

    resp = await client.post(
        "/objects",
        json={"latex": "17", "facets": [{"type_id": numbers, "data": {"int": 17}}]},
    )
    assert resp.status_code == 409
    assert held in resp.json()["detail"]

    resp = await client.put(f"/objects/{held}/facets/{numbers}", json={"data": {"int": 17}})
    assert resp.status_code == 200
    assert sorted(f["type_id"] for f in resp.json()["facets"]) == sorted([integers, numbers])


async def test_a_facet_must_fit_its_type(client: AsyncClient) -> None:
    integers = await make_type(client, "\\text{Integers}", "int")
    plain = await make(client, "A")
    resp = await client.post(
        "/objects", json={"latex": "x", "facets": [{"type_id": integers, "data": {"poly": {}}}]}
    )
    assert resp.status_code == 400
    resp = await client.post(
        "/objects",
        json={"latex": "x", "facets": [{"type_id": integers, "data": {"int": 1, "poly": {}}}]},
    )
    assert resp.status_code == 400
    resp = await client.post(
        "/objects", json={"latex": "x", "facets": [{"type_id": plain, "data": {"int": 1}}]}
    )
    assert resp.status_code == 404
    assert len((await client.get("/objects")).json()) == 2


async def test_subtypes_and_supertypes(client: AsyncClient) -> None:
    ids = await taxonomy(client)
    matrices, symmetric, diagonal = ids["matrices"], ids["symmetric"], ids["diagonal"]

    direct = (await client.get(f"/objects/{matrices}/subtypes")).json()
    assert [o["id"] for o in direct] == [symmetric]

    every = (await client.get(f"/objects/{matrices}/subtypes", params={"transitive": True})).json()
    assert sorted(o["id"] for o in every) == sorted([symmetric, diagonal])

    above = await client.get(f"/objects/{diagonal}/supertypes", params={"transitive": True})
    assert sorted(o["id"] for o in above.json()) == sorted([symmetric, matrices])


async def test_query_by_membership_walks_subtypes(client: AsyncClient) -> None:
    ids = await taxonomy(client)
    every = await query(client, member_of=ids["matrices"])
    assert every == sorted([ids["identity"], ids["swap"], ids["shear"]])

    only_direct = await query(client, member_of=ids["matrices"], transitive=False)
    assert only_direct == [ids["shear"]]

    assert await query(client, member_of=ids["symmetric"]) == sorted([ids["identity"], ids["swap"]])


async def test_query_by_data(client: AsyncClient) -> None:
    ids = await taxonomy(client)
    equal = matrix([[1, 0], [0, 1]])
    assert await query(client, data_equals=json.dumps(equal)) == [ids["identity"]]
    assert await query(client, member_of=ids["symmetric"], data_equals=json.dumps(equal)) == [
        ids["identity"]
    ]


async def test_query_by_polynomial_ignoring_its_variable(client: AsyncClient) -> None:
    polys = await make_type(client, "\\text{Polynomials}", "poly")
    in_x = await make_instance(client, "x^{2} + 1", polys, square_plus(1, "x"))
    in_z = await make_instance(client, "z^{2} + 1", polys, square_plus(1, "z"))
    await make_instance(client, "x^{2} + 2", polys, square_plus(2, "x"))

    any_variable = square_plus(1, "x")
    del any_variable["poly"]["var"]
    assert await query(client, data_contains=json.dumps(any_variable)) == sorted([in_x, in_z])
    assert await query(client, data_equals=json.dumps(square_plus(1, "z"))) == [in_z]


async def test_query_by_property(client: AsyncClient) -> None:
    ids = await taxonomy(client)
    integers = await make_type(client, "\\text{Integers}", "int")
    determinant = await make(client, "\\text{Determinant}")
    one = await make_instance(client, "1", integers, {"int": 1})
    minus_one = await make_instance(client, "-1", integers, {"int": -1})
    await relate(client, determinant, [ids["identity"]], [one])
    await relate(client, determinant, [ids["shear"]], [one])
    await relate(client, determinant, [ids["swap"]], [minus_one])

    assert await query(client, where=f"{determinant}:{one}") == sorted(
        [ids["identity"], ids["shear"]]
    )
    assert await query(client, member_of=ids["symmetric"], where=f"{determinant}:{one}") == [
        ids["identity"]
    ]


async def test_query_rejects_malformed_filters(client: AsyncClient) -> None:
    for params in (
        {"data_equals": "{not json"},
        {"data_contains": "[1, 2]"},
        {"where": "not-a-pair"},
    ):
        assert (await client.get("/objects/query", params=params)).status_code == 400
    plain = await make(client, "A")
    assert (await client.get("/objects/query", params={"member_of": plain})).status_code == 404


async def test_roles_are_a_set(client: AsyncClient) -> None:
    ids = await taxonomy(client)
    polys = await make_type(client, "\\text{Polynomials}", "poly")
    p = await make_instance(client, "x^{2} + 1", polys, square_plus(1, "x"))
    three = await make_instance(client, "M", ids["matrices"], matrix([[3]]))
    ten = await make_instance(client, "M'", ids["matrices"], matrix([[10]]))
    await relate(client, p, [three], [ten])

    def roles(object_id: str) -> list[str]:
        return detail[object_id]["roles"]

    detail = {
        object_id: (await client.get(f"/objects/{object_id}")).json()
        for object_id in (ids["matrices"], ids["identity"], p)
    }
    assert roles(ids["matrices"]) == ["type"]
    assert roles(ids["identity"]) == ["instance"]
    assert roles(p) == ["map", "instance"]

    lonely_map = await make(client, "\\text{Trace}")
    await client.post("/implementations", json={"operator_id": lonely_map, "code": ""})
    assert (await client.get(f"/objects/{lonely_map}")).json()["roles"] == ["map"]


async def test_feed_records_who_did_what(client: AsyncClient) -> None:
    resp = await client.post("/objects", json={"latex": "A", "contributor": "  Noether "})
    obj = resp.json()["id"]
    await client.post("/objects", json={"latex": "B", "contributor": "   "})
    comment = await client.post(
        f"/objects/{obj}/comments", json={"body": "A nice one.", "contributor": "Noether"}
    )
    assert comment.status_code == 201

    feed = (await client.get("/events")).json()
    assert [entry["kind"] for entry in feed] == [
        "comment_created",
        "object_created",
        "object_created",
    ]
    assert [entry["contributor"] for entry in feed] == ["Noether", None, "Noether"]
    assert feed[2]["object"]["id"] == obj
    assert feed[2]["source"] == "manual"
    assert feed[0]["comment"]["body"] == "A nice one."

    mine = (await client.get("/events", params={"contributor": "Noether"})).json()
    assert len(mine) == 2


async def test_assert_records_its_implementation_as_the_source(client: AsyncClient) -> None:
    await make_type(client, "\\text{Integers}", "int")
    operator = await make(client, "\\text{Determinant}")
    implementation = await client.post(
        "/implementations", json={"operator_id": operator, "code": ""}
    )
    implementation_id = implementation.json()["id"]
    matrix_id = await make(client, "A")
    resp = await client.post(
        "/relations/assert",
        json={
            "operator_id": operator,
            "input_object_ids": [matrix_id],
            "outputs": [{"latex": "3", "data": {"int": 3}}],
            "implementation_id": implementation_id,
        },
    )
    assert resp.status_code == 200, resp.text
    feed = (await client.get("/events")).json()
    computed = [entry for entry in feed if entry["source"] == f"implementation:{implementation_id}"]
    assert sorted(entry["kind"] for entry in computed) == ["object_created", "relation_created"]


async def test_deleting_an_object_clears_its_events(client: AsyncClient) -> None:
    operator = await make(client, "\\text{Inverse}")
    matrix_id = await make(client, "A")
    await relate(client, operator, [matrix_id], [matrix_id])
    await client.post(f"/objects/{matrix_id}/comments", json={"body": "Self-inverse."})

    assert (await client.delete(f"/objects/{matrix_id}")).status_code == 204
    feed = (await client.get("/events")).json()
    assert [entry["object"]["id"] for entry in feed] == [operator]

    async with engine.connect() as connection:
        remaining = (await connection.execute(text("SELECT count(*) FROM events"))).scalar_one()
    assert remaining == 1


async def test_comments(client: AsyncClient) -> None:
    obj = await make(client, "A")
    first = (await client.post(f"/objects/{obj}/comments", json={"body": "First"})).json()
    await client.post(f"/objects/{obj}/comments", json={"body": "Second"})
    assert (await client.post(f"/objects/{obj}/comments", json={"body": "  "})).status_code == 400

    listed = (await client.get(f"/objects/{obj}/comments")).json()
    assert [c["body"] for c in listed] == ["First", "Second"]

    assert (await client.delete(f"/comments/{first['id']}")).status_code == 204
    assert [c["body"] for c in (await client.get(f"/objects/{obj}/comments")).json()] == ["Second"]
    feed = (await client.get("/events")).json()
    assert [e["kind"] for e in feed] == ["comment_created", "object_created"]


async def test_queries_can_use_their_indexes() -> None:
    plans = {
        "ix_memberships_data_equality": "SELECT id FROM memberships WHERE data = '{\"int\": 3}'",
        "ix_memberships_data_containment": (
            "SELECT id FROM memberships WHERE data @> '{\"int\": 3}'"
        ),
        "ix_memberships_type_id": "SELECT object_id FROM memberships WHERE type_id = :nothing",
        "ix_relation_input_object_id": (
            "SELECT relation_id FROM relation_input WHERE object_id = :nothing"
        ),
        "ix_relations_operator_id": "SELECT id FROM relations WHERE operator_id = :nothing",
    }
    async with engine.connect() as connection:
        await connection.execute(text("SET LOCAL enable_seqscan = off"))
        for index, sql in plans.items():
            explained = await connection.execute(
                text(f"EXPLAIN {sql}"), {"nothing": uuid.UUID(int=0)}
            )
            plan = explained.scalars().all()
            assert any(index in line for line in plan), (index, plan)
