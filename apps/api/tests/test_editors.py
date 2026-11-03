import pytest
from httpx import AsyncClient

from monet_api.core.config import settings
from tests.conftest import editor_key

NO_KEY = {"X-Editor-Key": ""}


async def test_without_a_key_one_can_read_and_comment_but_not_write(client: AsyncClient) -> None:
    obj = (await client.post("/objects", json={"latex": "x"})).json()["id"]
    assert (await client.get(f"/objects/{obj}", headers=NO_KEY)).status_code == 200
    refused = await client.post("/objects", json={"latex": "y"}, headers=NO_KEY)
    assert refused.status_code == 401
    assert refused.json()["detail"] == "this needs an editor key"
    comment = await client.post(f"/objects/{obj}/comments", json={"body": "Nice."}, headers=NO_KEY)
    assert comment.status_code == 201
    removal = await client.delete(f"/comments/{comment.json()['id']}", headers=NO_KEY)
    assert removal.status_code == 401


async def test_level_one_adds_instances_and_results_only(client: AsyncClient) -> None:
    ints = (
        await client.post("/objects", json={"latex": "Z", "as_type": {"data_kind": "int"}})
    ).json()["id"]
    square = (await client.post("/objects", json={"latex": "\\text{Square}"})).json()["id"]
    adder = await editor_key(client, "Gauss", 1)

    instance = await client.post(
        "/objects",
        json={"latex": "3", "facets": [{"type_id": ints, "data": {"int": 3}}]},
        headers=adder,
    )
    assert instance.status_code == 201
    computed = await client.post(
        "/relations/assert",
        json={
            "operator_id": square,
            "input_object_ids": [instance.json()["id"]],
            "outputs": [{"latex": "9", "data": {"int": 9}}],
        },
        headers=adder,
    )
    assert computed.status_code == 200
    assert computed.json()["relation"]["provenance"]["contributor"] == "Gauss"

    a_type = await client.post("/objects", json={"latex": "T", "as_type": {}}, headers=adder)
    assert a_type.status_code == 403
    by_hand = await client.post(
        "/relations",
        json={"operator_id": square, "input_object_ids": [ints], "output_object_ids": [ints]},
        headers=adder,
    )
    assert by_hand.status_code == 403
    assert (await client.delete(f"/objects/{ints}", headers=adder)).status_code == 403
    edit = await client.patch(f"/objects/{ints}", json={"latex": "N"}, headers=adder)
    assert edit.status_code == 403


async def test_level_two_adds_types_and_maps_but_changes_nothing(client: AsyncClient) -> None:
    builder = await editor_key(client, "Noether", 2)
    ring = await client.post("/objects", json={"latex": "R", "as_type": {}}, headers=builder)
    assert ring.status_code == 201
    a_map = await client.post(
        "/objects",
        json={
            "latex": "f",
            "signatures": [{"domain_id": ring.json()["id"], "codomain_id": ring.json()["id"]}],
        },
        headers=builder,
    )
    assert a_map.status_code == 201
    code = await client.post(
        "/implementations", json={"operator_id": a_map.json()["id"], "code": ""}, headers=builder
    )
    assert code.status_code == 201
    implementation = code.json()["id"]
    rewrite = await client.patch(
        f"/implementations/{implementation}",
        json={"operator_id": a_map.json()["id"], "code": "x"},
        headers=builder,
    )
    assert rewrite.status_code == 403
    assert (
        await client.delete(f"/objects/{ring.json()['id']}", headers=builder)
    ).status_code == 403


async def test_level_three_may_delete(client: AsyncClient) -> None:
    keeper = await editor_key(client, "Hilbert", 3)
    obj = (await client.post("/objects", json={"latex": "x"})).json()["id"]
    assert (await client.delete(f"/objects/{obj}", headers=keeper)).status_code == 204


async def test_a_wrong_or_revoked_key_is_refused(client: AsyncClient) -> None:
    wrong = await client.post("/objects", json={"latex": "x"}, headers={"X-Editor-Key": "nope"})
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "this editor key is not valid"

    key = await editor_key(client, "Weyl", 1)
    me = (await client.get("/editors/me", headers=key)).json()
    assert (me["name"], me["email"], me["level"]) == ("Weyl", "weyl@example.org", 1)
    assert (await client.delete(f"/editors/{me['id']}")).status_code == 204
    assert (await client.get("/editors/me", headers=key)).status_code == 401


async def test_only_the_top_level_manages_keys(client: AsyncClient) -> None:
    builder = await editor_key(client, "Noether", 2)
    assert (await client.get("/editors", headers=builder)).status_code == 403
    listed = (await client.get("/editors")).json()
    assert [(editor["name"], editor["level"]) for editor in listed] == [("Noether", 2)]
    assert "key" not in listed[0]


async def test_keyed_writes_are_logged(client: AsyncClient) -> None:
    adder = await editor_key(client, "Gauss", 1)
    created = await client.post("/objects", json={"latex": "x"}, headers=adder)
    await client.delete(f"/objects/{created.json()['id']}", headers=adder)
    changes = (await client.get("/changes")).json()
    gauss = [(c["method"], c["path"], c["status"]) for c in changes if c["editor"] == "Gauss"]
    assert gauss == [
        ("DELETE", f"/objects/{created.json()['id']}", 403),
        ("POST", "/objects", 201),
    ]


async def test_an_editor_needs_an_email(client: AsyncClient) -> None:
    for email in (None, "", "weyl"):
        body = {"name": "Weyl", "email": email, "level": 1}
        assert (await client.post("/editors", json=body)).status_code == 422


async def test_keyed_writes_are_credited_with_the_editors_email(client: AsyncClient) -> None:
    adder = await editor_key(client, "Gauss", 1)
    body = {"latex": "x", "contributor": "Someone else", "email": "else@example.org"}
    created = (await client.post("/objects", json=body, headers=adder)).json()
    [event] = (await client.get("/events")).json()
    assert (event["contributor"], event["email"]) == ("Gauss", "gauss@example.org")
    provenance = (await client.get(f"/objects/{created['id']}")).json()["provenance"]
    assert (provenance["contributor"], provenance["email"]) == ("Gauss", "gauss@example.org")


async def test_the_owner_is_credited_with_the_configured_email(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "admin_email", "owner@example.org")
    me = (await client.get("/editors/me")).json()
    assert (me["name"], me["email"]) == (settings.admin_name, "owner@example.org")
