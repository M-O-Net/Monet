from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import RequestResponseEndpoint

from monet_api.comments.router import router as comments_router
from monet_api.core.config import settings
from monet_api.core.db import async_session
from monet_api.core.limits import BodySizeLimit
from monet_api.editors import service as editors
from monet_api.editors.router import router as editors_router
from monet_api.events.router import router as events_router
from monet_api.implementations.router import router as implementations_router
from monet_api.objects.router import router as objects_router
from monet_api.stats.router import router as stats_router
from monet_api.suggestions.router import router as suggestions_router

app = FastAPI(title="Monet API")

app.add_middleware(BodySizeLimit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(objects_router)
app.include_router(implementations_router)
app.include_router(comments_router)
app.include_router(events_router)
app.include_router(stats_router)
app.include_router(suggestions_router)
app.include_router(editors_router)


@app.middleware("http")
async def record_changes(request: Request, call_next: RequestResponseEndpoint) -> Response:
    response = await call_next(request)
    editor = getattr(request.state, "editor", None)
    if editor is not None and request.method != "GET":
        async with async_session() as session:
            await editors.record_change(
                session, editor.name, request.method, request.url.path, response.status_code
            )
    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    problems = [
        f"{'.'.join(str(part) for part in error['loc'][1:]) or 'request'}: {error['msg']}"
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": "; ".join(problems)})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409, content={"detail": "this conflicts with what is already stored"}
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


@app.get("/health", operation_id="health")
async def health() -> dict[str, bool]:
    return {"ok": True}
