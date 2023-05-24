import logging
import sys
from typing import Generator

import redis
from fastapi import Depends, HTTPException, Request, Security, WebSocket
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db() -> Generator:
    try:
        db = SessionLocal()
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
