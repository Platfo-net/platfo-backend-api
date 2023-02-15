from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=False if settings.ENVIRONMENT == "prod" else True,
    docs_url=None if settings.ENVIRONMENT == "prod" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "prod" else "/redoc",
)

app.include_router(api_router, prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health-check"])
async def health():
    return {"message": "ok!"}


if not settings.ENVIRONMENT == "test":
    Instrumentator().instrument(app).expose(app)
