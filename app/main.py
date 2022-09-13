import sqltap
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings


settings.ENVIRONMENT

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=False if settings.ENVIRONMENT == "prod" else True,
    docs_url= None if settings.ENVIRONMENT == "prod" else "/docs",
    redoc_url= None if settings.ENVIRONMENT == "prod" else "/redoc",
)


@app.middleware("http")
async def add_sql_tap(request: Request, call_next):
    profiler = sqltap.start()
    response = await call_next(request)
    statistics = profiler.collect()
    sqltap.report(statistics, "report.txt", report_format="text")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health-check"])
async def health():
    return {"message": "ok!"}
