from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, RedisDsn, validator

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Platfo Backend Api'
    APP_NAME: str
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    USERS_OPEN_REGISTRATION: str

    ENVIRONMENT: Optional[str]
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str
    FIRST_ADMIN_PHONE_NUMBER: str
    FIRST_ADMIN_PHONE_COUNTRY_CODE: str

    FIRST_USER_EMAIL: str = None
    FIRST_USER_PASSWORD: str = None

    DB_HOST: str
    DB_PORT: int = 6432

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
    REDIS_PASSWORD: str
    REDIS_PORT: str
    REDIS_DB_CELERY: str
    REDIS_DB_CACHE: str

    REDIS_RESET_PASSWORD_DB: int = 4
    REDIS_USER_ACTIVATION_DB: int = 5

    CELERY_URI: Optional[str] = None

    S3_ROOT_USER: str
    S3_ROOT_PASSWORD: str
    S3_PORT: str
    S3_HOST: str

    S3_CHATFLOW_MEDIA_BUCKET: str
    S3_CAMPAIGN_BUCKET: str
    S3_USER_PROFILE_BUCKET: str

    CAMPAIGN_INTERVAL_SEND_CONTACT_COUNT: int = 150
    CAMPAIGN_PERIOD_INTERVAL_MINUTES: int = 15

    SAMPLE_FACEBOOK_PAGE_ID: int = 20
    SAMPLE_CONTACT_IGS_ID: int = 10

    SMS_IR_USER_ACTIVATION_TEMPLATE_ID: int
    SMS_IR_USER_RESET_PASSWORD_TEMPLATE_ID: int

    SMS_IR_API_KEY: str
    SMS_IR_LINE_NUMBER: str

    LOKI_LOG_PUSH_URL: str

    OTEL_EXPORTER_OTLP_ENDPOINT: str

    OTEL_SERVICE_NAME: str
    OTEL_EXPORTER_OTLP_INSECURE: str

    @validator('SQLALCHEMY_DATABASE_URI', pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme='postgresql',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('DB_HOST'),
            port=str(values.get('DB_PORT')),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @validator('CELERY_URI', pre=True)
    def assemble_celery_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme='redis',
            host=values.get('REDIS_HOST'),
            port=values.get('REDIS_PORT'),
            password=values.get('REDIS_PASSWORD'),
            path=f"/{values.get('REDIS_DB_CELERY') or ''}",
        )

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
