from datetime import timedelta
from typing import Any
import string
import random

from redis.client import Redis

from app import services, models, schemas
from app.api import deps
from app.core import security, cache
from app.core.config import settings
from fastapi import APIRouter, Body, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.constants.errors import Error
from app.core.exception import raise_http_exception

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/access-token", response_model=schemas.Token)
def login_access_token(
        *,
        db: Session = Depends(deps.get_db),
        data: schemas.LoginForm,
) -> Any:
    user = services.user.authenticate(
        db,
        email=data.email,
        password=data.password
    )

    if not user:
        raise_http_exception(Error.USER_PASS_WRONG_ERROR)
    elif not services.user.is_active(user):
        raise_http_exception(Error.INACTIVE_USER)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if not user.role_id:
        role = "GUEST"
    else:
        role = services.role.get(db, id=user.role_id)
        role = role.name
    token_payload = {
        "uuid": str(user.uuid),
        "role": role,
    }
    return {
        "access_token": security.create_access_token(
            token_payload, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/token-swagger", response_model=schemas.Token)
def login_access_token_swagger(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = services.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise_http_exception(Error.USER_PASS_WRONG_ERROR)
    elif not services.user.is_active(user):
        raise_http_exception(Error.INACTIVE_USER)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if not user.role_id:
        role = "GUEST"
    else:
        role = services.role.get(db, id=user.role_id)
        role = role.name
    token_payload = {
        "uuid": str(user.uuid),
        "role": role,
    }
    return {
        "access_token": security.create_access_token(
            token_payload, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/check", response_model=schemas.User)
def test_token(
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Test access token
    """
    current_user.id = current_user.uuid
    return current_user


@router.post("/hash-password", response_model=str)
def hash_password(
        password: str = Body(..., embed=True),
) -> Any:
    """
    Hash a password
    """
    return security.get_password_hash(password)


@router.post("/send-activation-code", response_model=schemas.RegisterCode)
def send_activation_sms(
        db: Session = Depends(deps.get_db),
        redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
        email: str = Body(..., embed=True),
):
    user = services.user.get_by_email(db, email=email)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_registeration_activation_code(redis_client, email)
    if data:
        raise_http_exception(Error.ACTIVATION_CODE_HAVE_BEEN_ALREADY_SENT)
    token = "".join(random.choice(f"{string.ascii_letters}0123456789") for i in range(64))
    code = random.randint(10000, 99999)
    result = cache.set_user_registeration_activation_code(redis_client, email, code, token)
    # TODO send sms
    if not result:
        raise_http_exception(Error.UNEXPECTED_ERROR)

    return schemas.RegisterCode(
        token=token
    )


@router.post("/activate", status_code=status.HTTP_200_OK)
def activate_user(
        *,
        db: Session = Depends(deps.get_db),
        redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
        activation_data: schemas.ActivationData
):
    user = services.user.get_by_email(db, email=activation_data.email)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_registeration_activation_code(redis_client, activation_data.email)
    if not data:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    code = data.get("code", None)
    token = data.get("token", None)
    if not (token and code):
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    if not token == activation_data.token:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)
    if not code == activation_data.code:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)
    services.user.activate(db, user=user)
    cache.remove_data_from_cache(redis_client, activation_data.email)
    return


@router.post("/forgot-password", response_model=schemas.RegisterCode)
def forgot_password(
        db: Session = Depends(deps.get_db),
        redis_client: Redis = Depends(deps.get_redis_client_for_reset_password),
        email: str = Body(..., embed=True),
):
    user = services.user.get_by_email(db, email=email)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_reset_password_code(redis_client, email)
    if data:
        raise_http_exception(Error.RESET_PASSWORD_CODE_HAVE_BEEN_ALREADY_SENT)
    token = "".join(random.choice(f"{string.ascii_letters}0123456789") for i in range(64))
    code = random.randint(10000, 99999)
    result = cache.set_user_reset_password_code(redis_client, email, code, token)
    # TODO send sms
    if not result:
        raise_http_exception(Error.UNEXPECTED_ERROR)

    return schemas.RegisterCode(
        token=token
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
        *,
        db: Session = Depends(deps.get_db),
        redis_client: Redis = Depends(deps.get_redis_client_for_reset_password),
        obj_in: schemas.ChangePassword
):
    user = services.user.get_by_email(db, email=obj_in.email)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_registeration_activation_code(redis_client, obj_in.email)
    if not data:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    code = data.get("code", None)
    token = data.get("token", None)
    if not (token and code):
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    if not token == obj_in.token:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)
    if not code == obj_in.code:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)
    services.user.change_password(db, db_user=user, password=obj_in.password)
    cache.remove_data_from_cache(redis_client, obj_in.email)
    return
