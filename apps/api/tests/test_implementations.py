from httpx import AsyncClient

DETERMINANT = "def compute(m):\n    return m.det()\n"
CHAR_POLY_OF_A = {
    "poly": {
        "var": "x",
        "degree": 2,
        "coeffs": {"0": {"int": 3}, "1": {"int": -4}, "2": {"int": 1}},
    }
}


async def _operator(client: AsyncClient, latex: str = "\\text{Determinant}") -> str:
    resp = await client.post("/objects", json={"latex": latex})
    return str(resp.json()["id"])


async def test_create_and_list_implementation(client: AsyncClient) -> None:
    operator_id = await _operator(client)

    resp = await client.post(
        "/implementations", json={"operator_id": operator_id, "code": DETERMINANT}
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["operator"]["latex"] == "\\text{Determinant}"
    assert created["code"] == DETERMINANT

    resp = await client.get("/implementations")
    assert [i["id"] for i in resp.json()] == [created["id"]]


async def test_implementation_requires_a_real_operator(client: AsyncClient) -> None:
    resp = await client.post(
        "/implementations",
        json={"operator_id": "00000000-0000-0000-0000-000000000000", "code": ""},
    )
    assert resp.status_code == 404


async def test_an_operator_may_have_several_implementations(client: AsyncClient) -> None:
    operator_id = await _operator(client)
    for code in ("def compute(a):\n    return a\n", "def compute(a, b):\n    return a + b\n"):
        resp = await client.post(
            "/implementations", json={"operator_id": operator_id, "code": code}
        )
        assert resp.status_code == 201

    listed = (await client.get("/implementations")).json()
    assert len(listed) == 2
    assert {i["operator"]["id"] for i in listed} == {operator_id}


async def test_update_and_delete_implementation(client: AsyncClient) -> None:
    operator_id = await _operator(client)
    resp = await client.post("/implementations", json={"operator_id": operator_id, "code": "old"})
    implementation_id = resp.json()["id"]

    resp = await client.patch(
        f"/implementations/{implementation_id}",
        json={"operator_id": operator_id, "code": "new"},
    )
    assert resp.status_code == 200
    assert resp.json()["code"] == "new"

    assert (await client.delete(f"/implementations/{implementation_id}")).status_code == 204
    assert (await client.get(f"/implementations/{implementation_id}")).status_code == 404


async def test_deleting_an_operator_deletes_its_implementation(client: AsyncClient) -> None:
    operator_id = await _operator(client)
    await client.post("/implementations", json={"operator_id": operator_id, "code": DETERMINANT})

    assert (await client.delete(f"/objects/{operator_id}")).status_code == 204
    assert (await client.get("/implementations")).json() == []


async def test_assert_creates_the_output_object_and_relation(client: AsyncClient) -> None:
    operator_id = await _operator(client, "\\text{Characteristic Polynomial}")
    resp = await client.post("/objects", json={"latex": "\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}"})
    matrix_id = resp.json()["id"]

    resp = await client.post(
        "/relations/assert",
        json={
            "operator_id": operator_id,
            "input_object_ids": [matrix_id],
            "outputs": [{"latex": "x^{2} - 4 x + 3", "data": CHAR_POLY_OF_A}],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["created_relation"] is True
    assert len(body["created_object_ids"]) == 1
    assert body["relation"]["outputs"][0]["object"]["latex"] == "x^{2} - 4 x + 3"
    assert body["relation"]["outputs"][0]["object"]["data"] == CHAR_POLY_OF_A


async def test_assert_is_idempotent_and_matches_outputs_by_data(client: AsyncClient) -> None:
    operator_id = await _operator(client, "\\text{Characteristic Polynomial}")
    matrix_id = (await client.post("/objects", json={"latex": "A"})).json()["id"]
    existing = await client.post("/objects", json={"latex": "3 - 4x + x^2", "data": CHAR_POLY_OF_A})
    existing_id = existing.json()["id"]

    payload = {
        "operator_id": operator_id,
        "input_object_ids": [matrix_id],
        "outputs": [{"latex": "x^{2} - 4 x + 3", "data": CHAR_POLY_OF_A}],
    }
    first = (await client.post("/relations/assert", json=payload)).json()
    assert first["created_object_ids"] == []
    assert first["relation"]["outputs"][0]["object"]["id"] == existing_id

    second = (await client.post("/relations/assert", json=payload)).json()
    assert second["created_relation"] is False
    assert second["relation"]["id"] == first["relation"]["id"]
    assert len((await client.get("/relations")).json()) == 1


async def test_assert_never_matches_outputs_by_latex(client: AsyncClient) -> None:
    operator_id = await _operator(client)
    input_id = (await client.post("/objects", json={"latex": "A"})).json()["id"]
    same_latex = await client.post("/objects", json={"latex": "x^{2} - 4 x + 3"})

    for output in (
        {"latex": "x^{2} - 4 x + 3", "data": CHAR_POLY_OF_A},
        {"latex": "x^{2} - 4 x + 3", "data": None},
    ):
        body = (
            await client.post(
                "/relations/assert",
                json={
                    "operator_id": operator_id,
                    "input_object_ids": [input_id],
                    "outputs": [output],
                },
            )
        ).json()
        assert len(body["created_object_ids"]) == 1
        assert body["relation"]["outputs"][0]["object"]["id"] != same_latex.json()["id"]


async def test_assert_rejects_an_empty_output(client: AsyncClient) -> None:
    operator_id = await _operator(client)
    resp = await client.post(
        "/relations/assert",
        json={"operator_id": operator_id, "input_object_ids": [], "outputs": []},
    )
    assert resp.status_code == 400
