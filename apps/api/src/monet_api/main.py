from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from monet_api.core.config import settings
from monet_api.implementations.router import router as implementations_router
from monet_api.objects.router import router as objects_router

app = FastAPI(title="Monet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(objects_router)
app.include_router(implementations_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


@app.get("/health", operation_id="health")
async def health() -> dict[str, bool]:
    return {"ok": True}
