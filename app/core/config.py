from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Platfo Backend Api'
    VERSION: str = None
    APP_NAME: str
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    USERS_OPEN_REGISTRATION: str
    SERVER_ADDRESS_NAME: str

    ENVIRONMENT: Optional[str]
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str
    FIRST_ADMIN_PHONE_NUMBER: str
    FIRST_ADMIN_PHONE_COUNTRY_CODE: str

    FIRST_DEVELOPER_EMAIL: str
    FIRST_DEVELOPER_PASSWORD: str
    FIRST_DEVELOPER_PHONE_NUMBER: str
    FIRST_DEVELOPER_PHONE_COUNTRY_CODE: str

    SHOP_USER_EMAIL: str
    SHOP_USER_PASSWORD: str
    SHOP_USER_PHONE_NUMBER: str
    SHOP_USER_PHONE_COUNTRY_CODE: str

    FIRST_USER_EMAIL: Optional[str] = None
    FIRST_USER_PASSWORD: Optional[str] = None

    DB_HOST: Optional[str] = None
    DB_PORT: int = 6432

    DB_PASSWORD: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_NAME: Optional[str] = None

    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None

    FACEBOOK_GRAPH_BASE_URL: Optional[str] = None
    FACEBOOK_GRAPH_VERSION: Optional[str] = None

    FACEBOOK_WEBHOOK_VERIFY_TOKEN: str = None

    REDIS_HOST: str
    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_DB_CELERY: str = None
    REDIS_DB_CACHE: str = None

    REDIS_RESET_PASSWORD_DB: int = 4
    REDIS_USER_ACTIVATION_DB: int = 5

    CELERY_URI: Optional[RedisDsn] = None

    S3_ROOT_USER: Optional[str] = None
    S3_ROOT_PASSWORD: Optional[str] = None
    S3_PORT: Optional[str] = None
    S3_HOST: Optional[str] = None

    S3_ACADEMY_ATTACHMENT_BUCKET: str = "academy_attachment_bucket"
    S3_CHATFLOW_MEDIA_BUCKET: str = "chatflow_media_bucket"
    S3_CAMPAIGN_BUCKET: str = "notifier_campaign_bucket"
    S3_USER_PROFILE_BUCKET: str = 'user_profile_bucket'
    S3_SHOP_PRODUCT_IMAGE_BUCKET: str = 'shop_product_image_bucket'
    S3_TELEGRAM_BOT_IMAGES_BUCKET: str = 'telegram_bot_image_bucket'
    S3_PAYMENT_RECEIPT_IMAGE: str = 'payment_receipt_image_bucket'

    CAMPAIGN_INTERVAL_SEND_LEAD_COUNT: Optional[int] = None
    CAMPAIGN_PERIOD_INTERVAL_MINUTES: Optional[int] = None

    SAMPLE_FACEBOOK_PAGE_ID: Optional[int] = None
    SAMPLE_LEAD_IGS_ID: Optional[int] = None

    SMS_IR_USER_ACTIVATION_TEMPLATE_ID: Optional[int] = None
    SMS_IR_USER_RESET_PASSWORD_TEMPLATE_ID: Optional[int] = None

    SMS_IR_API_KEY: Optional[str] = None
    SMS_IR_LINE_NUMBER: Optional[str] = None

    LOKI_LOG_PUSH_URL: Optional[str] = None

    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None

    OTEL_SERVICE_NAME: Optional[str] = None
    OTEL_EXPORTER_OTLP_INSECURE: Optional[str] = None

    SUPPORT_BOT_TOKEN: Optional[str] = None
    PLATFO_SHOPS_BASE_URL: Optional[str] = None

    TELEGRAM_TOKEN_ENCRYPTION_KEY: Optional[str] = None

    @validator('SQLALCHEMY_DATABASE_URI', pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme='postgresql',
            username=values.get('DB_USER'),
            password=values.get('DB_PASSWORD'),
            host=values.get('DB_HOST'),
            port=values.get('DB_PORT'),
            path=values.get('DB_NAME'),
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
            path=f"{values.get('REDIS_DB_CELERY') or ''}",
        )

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
