from datetime import datetime
import json
import logging
import redis
import sys

from typing import Generator, Optional

from app import services, models, schemas
from app.constants.role import Role
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from sqlalchemy.orm import Session
from app.constants.errors import Error
from fastapi import WebSocket, Request
from redis.client import Redis
from app.core.cache import get_data_from_cache, set_data_to_cache
from pydantic import UUID4


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(
        self,
        request: Request = None,
        websocket: WebSocket = None
    ):
        return await super().__call__(websocket or request)


reusable_oauth2 = CustomOAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token-swagger",
    scopes={
        Role.ADMIN["name"]: Role.ADMIN["description"],
        Role.USER["name"]: Role.USER["description"],
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
            db=1,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)


def get_user_from_cache(
    redis_client: Redis,
    db: Session,
    id: UUID4
) -> Optional[models.User]:
    user = get_data_from_cache(redis_client, key=str(id))
    if user is None:
        user = services.user.get(db, id)
        if not user:
            return None
        data = dict(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            role_id=str(user.role_id),
            created_at=str(user.created_at),
            updated_at=str(user.updated_at)
        )
        data = json.dumps(data)
        state = set_data_to_cache(redis_client, str(user.id), data)
        if state:
            user = get_data_from_cache(redis_client, str(user.id))

    user = json.loads(user)
    return models.User(
        id=UUID4(user.get('id')),
        first_name=user.get('first_name', None),
        last_name=user.get('last_name', None),
        email=user.get('email', None),
        phone_number=user.get('phone_number', None),
        hashed_password=user.get('hashed_password'),
        is_active=user.get('is_active'),
        role_id=UUID4(user.get('role_id')),
        created_at=user.get('created_at'),
        updated_at=user.get('updated_at'),
    )


def get_current_user(
    security_scopes: SecurityScopes,
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
    redis_client: Redis = Depends(get_redis_client)
) -> models.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=Error.USER_PASS_WRONG_ERROR["code"],
        detail=Error.USER_PASS_WRONG_ERROR["text"],
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if payload.get("id") is None:
            raise credentials_exception
        token_data = schemas.TokenPayload(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=Error.TOKEN_NOT_EXIST_OR_EXPIRATION_ERROR
            ["status_code"],
            detail=Error.TOKEN_NOT_EXIST_OR_EXPIRATION_ERROR
            ["text"],
        )

    user = get_user_from_cache(redis_client, db, token_data.id)

    if not user:
        raise credentials_exception
    if security_scopes.scopes and not token_data.role:
        raise HTTPException(
            status_code=Error.PERMISSION_DENIED_ERROR["status_code"],
            detail=Error.PERMISSION_DENIED_ERROR["text"],
            headers={"WWW-Authenticate": authenticate_value},
        )
    if (
        security_scopes.scopes
        and token_data.role not in security_scopes.scopes
    ):
        raise HTTPException(
            status_code=Error.PERMISSION_DENIED_ERROR["status_code"],
            detail=Error.PERMISSION_DENIED_ERROR["text"],
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user


def get_current_active_user(
    current_user: models.User = Security(get_current_user, scopes=[],),
) -> models.User:
    if not services.user.is_active(current_user):
        raise HTTPException(
            status_code=Error.INACTIVE_USER["status_code"],
            detail=Error.INACTIVE_USER["text"]
        )
    return current_user
