from functools import lru_cache
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Botinow Backend Api"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    USERS_OPEN_REGISTRATION: str

    ENVIRONMENT: Optional[str]
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str

    DB_HOST: str

    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    S3_ACADEMY_ATTACHMENT_BUCKET: str

    FACEBOOK_APP_ID: str
    FACEBOOK_APP_SECRET: str

    FACEBOOK_GRAPH_BASE_URL: str
    FACEBOOK_GRAPH_VERSION: str

    FACEBOOK_WEBHOOK_VERIFY_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: int

    CELERY_BROKER_URL = "redis://redis:6379/2"
    CELERY_RESULT_BACKEND = "redis://redis:6379/2"

    S3_ROOT_USER: str

    S3_ROOT_PASSWORD: str
    S3_PORT: str
    S3_HOST: str

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
            cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("DB_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
