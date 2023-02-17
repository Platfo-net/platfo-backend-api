from datetime import timedelta
from typing import Any

from app import services, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from fastapi import APIRouter, Body, Depends, HTTPException
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
    user = services.user.authenticate(db, email=data.email, password=data.password)
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
        raise HTTPException(
            status_code=Error.INACTIVE_USER["status_code"],
            detail=Error.INACTIVE_USER["text"],
        )
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
