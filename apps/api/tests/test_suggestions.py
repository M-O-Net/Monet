import base64

import pytest
from httpx import AsyncClient

from monet_api.core.config import settings

KEY = "review-key-for-tests"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


@pytest.fixture(autouse=True)
def _review_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "suggestions_review_key", KEY)


def screenshot(data: bytes = PNG, media_type: str = "image/png") -> dict[str, str]:
    return {"media_type": media_type, "data": base64.b64encode(data).decode()}


async def suggest(client: AsyncClient, **fields: object) -> dict[str, object]:
    body = {"body": "Add the Leech lattice.", "page_path": "/objects/abc?tab=1", **fields}
    resp = await client.post("/suggestions", json=body)
    assert resp.status_code == 201, resp.text
    result: dict[str, object] = resp.json()
    return result


async def test_a_suggestion_reaches_the_queue_with_its_page_and_screenshots(
    client: AsyncClient,
) -> None:
    created = await suggest(client, contributor="Conway", screenshots=[screenshot()])

    queue = (await client.get("/suggestions", headers={"X-Review-Key": KEY})).json()
    assert len(queue) == 1
    item = queue[0]
    assert item["id"] == created["id"]
    assert item["body"] == "Add the Leech lattice."
    assert item["page_path"] == "/objects/abc?tab=1"
    assert item["contributor"] == "Conway"
    assert [s["media_type"] for s in item["screenshots"]] == ["image/png"]

    image = await client.get(
        f"/suggestions/{item['id']}/screenshots/{item['screenshots'][0]['id']}",
        headers={"X-Review-Key": KEY},
    )
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content == PNG


async def test_the_queue_lists_newest_first(client: AsyncClient) -> None:
    await suggest(client, body="first")
    await suggest(client, body="second")

    queue = (await client.get("/suggestions", headers={"X-Review-Key": KEY})).json()
    assert [item["body"] for item in queue] == ["second", "first"]


async def test_the_queue_and_its_screenshots_need_the_review_key(client: AsyncClient) -> None:
    created = await suggest(client, screenshots=[screenshot()])
    queue = (await client.get("/suggestions", headers={"X-Review-Key": KEY})).json()
    image_url = f"/suggestions/{created['id']}/screenshots/{queue[0]['screenshots'][0]['id']}"

    assert (await client.get("/suggestions")).status_code == 403
    assert (await client.get("/suggestions", headers={"X-Review-Key": "guess"})).status_code == 403
    assert (await client.get(image_url)).status_code == 403
    assert (await client.delete(f"/suggestions/{created['id']}")).status_code == 403


async def test_without_a_key_on_the_server_the_queue_is_closed(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "suggestions_review_key", None)

    assert (
        await client.post("/suggestions", json={"body": "x", "page_path": "/"})
    ).status_code == 201
    assert (await client.get("/suggestions", headers={"X-Review-Key": ""})).status_code == 503


async def test_dismissing_a_suggestion_removes_it_and_its_screenshots(client: AsyncClient) -> None:
    created = await suggest(client, screenshots=[screenshot(), screenshot()])
    headers = {"X-Review-Key": KEY}

    assert (
        await client.delete(f"/suggestions/{created['id']}", headers=headers)
    ).status_code == 204
    assert (await client.get("/suggestions", headers=headers)).json() == []
    assert (
        await client.delete(f"/suggestions/{created['id']}", headers=headers)
    ).status_code == 404


@pytest.mark.parametrize(
    ("fields", "status"),
    [
        ({"body": "   "}, 400),
        ({"page_path": "https://elsewhere.example/"}, 400),
        ({"page_path": "//elsewhere.example/"}, 400),
        ({"screenshots": [screenshot()] * 4}, 422),
        ({"screenshots": [screenshot(media_type="image/svg+xml")]}, 422),
        ({"screenshots": [screenshot(data=b"\0" * 1_500_001)]}, 413),
    ],
)
async def test_bad_suggestions_are_refused(
    client: AsyncClient, fields: dict[str, object], status: int
) -> None:
    body = {"body": "Add the Leech lattice.", "page_path": "/", **fields}
    assert (await client.post("/suggestions", json=body)).status_code == status
    assert (await client.get("/suggestions", headers={"X-Review-Key": KEY})).json() == []
