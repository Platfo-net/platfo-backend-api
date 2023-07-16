from typing import Any

from fastapi import APIRouter, Depends, Security, status
from redis import Redis
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/dev', tags=['Dev Tools'])


@router.post('/create-developer', status_code=status.HTTP_201_CREATED)
def create_developer(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.DeveloperCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    user = services.user.get_by_email(db, email=user_in.email)
    if user:
        raise_http_exception(Error.USER_EXIST_ERROR)
    developer_role = services.role.get_by_name(db, name=Role.DEVELOPER["name"])
    obj_in = schemas.UserCreate(
        phone_number=user_in.phone_number,
        phone_country_code=user_in.phone_country_code,
        email=user_in.email,
        is_active=True,
        is_email_verified=True,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        password=user_in.password,
        role_id=developer_role.id,
    )
    services.user.create(db, obj_in=obj_in)

    return


@router.get('/sms-code-delete')
def delete_sms_codes(
    *,
    redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:

    keys = redis_client.keys()
    for key in keys:
        redis_client.delete(key)

    return
