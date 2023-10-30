from typing import Any

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core import storage, utils
from app.core.config import settings
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/user', tags=['User'])


@router.post('/register-by-phone-number', status_code=status.HTTP_201_CREATED)
def register_user_by_phone_number(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserRegisterByPhoneNumber,
):
    user = services.user.get_by_phone_number(
        db,
        phone_number=user_in.phone_number,
        phone_country_code=user_in.phone_country_code,
    )

    if user and user.is_active:
        raise_http_exception(Error.USER_EXIST_ERROR)
    if user and not user.is_active:
        raise_http_exception(Error.INACTIVE_USER)
    if not utils.validate_password(user_in.password):
        raise_http_exception(Error.NOT_ACCEPTABLE_PASSWORD)

    obj_in = schemas.UserRegister(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
        phone_country_code=user_in.phone_country_code,
        password=user_in.password,
    )
    services.user.register(db, obj_in=obj_in)
    return


@router.post('/register-by-email', status_code=status.HTTP_201_CREATED)
def register_user_by_email(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserRegisterByEmail,
):
    user = services.user.get_by_email(db, email=user_in.email)

    if user and user.is_active:
        raise_http_exception(Error.USER_EXIST_ERROR)
    if user and not user.is_active:
        raise_http_exception(Error.INACTIVE_USER)
    if not utils.validate_password(user_in.password):
        raise_http_exception(Error.NOT_ACCEPTABLE_PASSWORD)
    obj_in = schemas.UserRegister(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        password=user_in.password,
    )
    services.user.register(db, obj_in=obj_in)
    return


@router.put('/me', status_code=status.HTTP_200_OK)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    user = services.user.get(db, id=current_user.id)
    services.user.update(db, db_obj=user, obj_in=user_in)

    return


@router.put('/me/change-password', response_model=schemas.User)
def change_password_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdatePassword,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    user = services.user.get(db, id=current_user.id)
    if not utils.validate_password(user_in.password):
        raise_http_exception(Error.NOT_ACCEPTABLE_PASSWORD)
    user = services.user.change_password(db, user_id=user.id, obj_in=user_in)

    return user


@router.get('/me', response_model=schemas.User)
def get_user_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    user = services.user.get(db, id=current_user.id)
    role = services.role.get(db, user.role_id)
    return schemas.User(
        id=user.uuid,
        email=user.email,
        is_active=user.is_active,
        phone_number=user.phone_number,
        phone_country_code=user.phone_country_code,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role=schemas.Role(
            name=role.name,
            description=role.description,
            id=role.uuid,
        ),
        profile_image=storage.get_file(
            user.profile_image, settings.S3_USER_PROFILE_BUCKET
        ),
    )
