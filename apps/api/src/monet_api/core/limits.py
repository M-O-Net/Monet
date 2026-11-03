from starlette.types import ASGIApp, Message, Receive, Scope, Send

MAX_BODY_BYTES = 8_000_000
TOO_LARGE: list[Message] = [
    {"type": "http.response.start", "status": 413, "headers": []},
    {"type": "http.response.body", "body": b""},
]


class BodySizeLimit:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        declared = dict(scope["headers"]).get(b"content-length", b"0")
        if not declared.isdigit() or int(declared) > MAX_BODY_BYTES:
            for message in TOO_LARGE:
                await send(message)
            return
        received = 0

        async def counted() -> Message:
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > MAX_BODY_BYTES:
                return {"type": "http.disconnect"}
            return message

        async def refused_if_too_large(message: Message) -> None:
            if received <= MAX_BODY_BYTES:
                await send(message)
            elif message["type"] == "http.response.start":
                for refusal in TOO_LARGE:
                    await send(refusal)

        await self.app(scope, counted, refused_if_too_large)
