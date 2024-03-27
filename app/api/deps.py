import logging
import socket
import sys
from typing import Generator

import logging_loki
import redis
from fastapi import (APIRouter, Depends, HTTPException, Request, Security,
                     WebSocket)
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, ResourceDetector
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import Tracer
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.constants.errors import Error
from app.constants.role import Role
from app.core import security
from app.core.config import settings
from app.core.exception import raise_http_exception
from app.db.session import SessionLocal


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(websocket or request)


reusable_oauth2 = CustomOAuth2PasswordBearer(
    tokenUrl=f'{settings.API_V1_STR}/auth/token-swagger',
    scopes={
        Role.ADMIN['name']: Role.ADMIN['description'],
        Role.USER['name']: Role.USER['description'],
    },
)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis_client():
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB_CACHE,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print('AuthenticationError')
        sys.exit(1)


def get_redis_client_for_user_activation():
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_USER_ACTIVATION_DB,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print('AuthenticationError')
        sys.exit(1)


def get_redis_client_for_reset_password():
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_RESET_PASSWORD_DB,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print('AuthenticationError')
        sys.exit(1)


def get_current_user(
        security_scopes: SecurityScopes,
        db: Session = Depends(get_db),
        token: str = Depends(reusable_oauth2),
) -> models.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = 'Bearer'
    credentials_exception = HTTPException(
        status_code=Error.USER_PASS_WRONG_ERROR['code'],
        detail=Error.USER_PASS_WRONG_ERROR['text'],
        headers={'WWW-Authenticate': authenticate_value},
    )
    token_data = None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if payload.get('id') is None:
            raise credentials_exception
        payload['id'] = int(payload['id'])
        token_data = schemas.TokenPayload(**payload)
    except Exception:
        raise_http_exception(Error.TOKEN_NOT_EXIST_OR_EXPIRATION_ERROR)

    user = services.user.get(db, int(token_data.id))

    if not user:
        raise credentials_exception
    if security_scopes.scopes and not token_data.role:
        raise_http_exception(
            Error.PERMISSION_DENIED_ERROR, {'WWW-Authenticate': authenticate_value}
        )
    if security_scopes.scopes and token_data.role not in security_scopes.scopes:
        raise_http_exception(
            Error.PERMISSION_DENIED_ERROR, {'WWW-Authenticate': authenticate_value}
        )
    return user


def get_current_active_user(
        current_user: models.User = Security(
            get_current_user,
            scopes=[],
        ),
) -> models.User:
    if not current_user.is_active:
        raise_http_exception(Error.INACTIVE_USER)

    return current_user


def logger_factory(router: APIRouter):
    def dependency() -> logging.Logger:

        handler = logging_loki.LokiHandler(
            url=settings.LOKI_LOG_PUSH_URL,
            tags={
                "application": settings.APP_NAME,
                "module": router.tags[0]
            },
            version="1",
        )
        logger = logging.getLogger(settings.PROJECT_NAME)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    return dependency


class LocalResourceDetector(ResourceDetector):
    def detect(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return Resource.create(
            {
                "net.host.name": hostname,
                "net.host.ip": ip_address,
            }
        )


def tracer_factory(router: APIRouter):
    def dependency() -> Tracer:
        exporter = OTLPSpanExporter()
        # exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(exporter)
        local_resource = LocalResourceDetector().detect()

        resource = local_resource.merge(
            Resource.create(
                {
                    ResourceAttributes.SERVICE_NAME: router.tags[0],
                    ResourceAttributes.SERVICE_VERSION: settings.VERSION,
                }
            )
        )
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)
        return trace.get_tracer(router.tags[0], settings.VERSION)
    return dependency
