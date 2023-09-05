import copy
from typing import Any, List

from fastapi import APIRouter, Depends, Security, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from redis.client import Redis
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.platform import Platform
from app.constants.role import Role
from app.core.cache import remove_data_from_cache
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/connection', tags=['Connection'])


@router.get('/all', response_model=List[schemas.Connection])
def get_list_of_connections(
    *,
    db: Session = Depends(deps.get_db),
    account_id: UUID4 = None,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    account = services.instagram_page.get_by_uuid(db, account_id)

    connections = services.connection.get_by_user_and_account_id(
        db, user_id=current_user.id, account_id=account.id
    )
    new_connections = []

    for connection in connections:
        account = services.instagram_page.get(db, id=connection.account_id)
        new_connections.append(
            schemas.Connection(
                account=schemas.Account(
                    id=account.id,
                    username=account.username,
                    platform='Instagram',
                    profile_image=account.profile_picture_url,
                    page_id=account.facebook_page_id,
                ),
                **jsonable_encoder(connection),
            )
        )
    return new_connections


@router.post('/', response_model=schemas.Connection)
def create_connection(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.ConnectionCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    account = None

    match obj_in.platform:
        case Platform.INSTAGRAM.get("name"):
            account = services.instagram_page.get_by_uuid(db, uuid=obj_in.account_id)

        case Platform.TELEGRAM.get("name"):
            account = services.telegram_bot.get_by_uuid(db, uuid=obj_in.account_id)

    if not account:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    connection = services.connection.get_by_application_name_and_account_id(
        db, application_name=obj_in.application_name, account_id=account.id
    )
    if connection:
        raise_http_exception(Error.CONNECTION_EXIST)
    details = None

    match obj_in.platform:
        case Platform.INSTAGRAM.get("name"):
            try:
                details = copy.deepcopy(obj_in.details)
                for detail in details:
                    chatflow = services.bot_builder.chatflow.get_by_uuid(
                        db, uuid=detail['chatflow_id'], user_id=current_user.id
                    )
                    detail['chatflow_id'] = chatflow.id

            except KeyError:
                raise_http_exception(Error.INVALID_DETAILS)

        case Platform.TELEGRAM.get("name"):
            try:
                details = copy.deepcopy(obj_in.details)
                for detail in details:
                    shop = services.shop.shop.get_user_shop_by_uuid(
                        db, uuid=detail['shop_id'], user_id=current_user.id,
                    )
                    if not shop:
                        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

                    detail['shop_id'] = shop.id

            except KeyError:
                raise_http_exception(Error.INVALID_DETAILS)

    connection = services.connection.create(
        db,
        obj_in=obj_in,
        account_id=account.id,
        details=details,
        user_id=current_user.id,
    )

    return schemas.Connection(
        id=connection.uuid,
        name=connection.name,
        description=connection.description,
        application_name=connection.application_name,
        details=obj_in.details,
        account_id=obj_in.account_id,
    )


@router.get('/{connection_id}', response_model=schemas.Connection)
def get_connection_by_id(
    *,
    db: Session = Depends(deps.get_db),
    connection_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    connection = services.connection.get_by_uuid(db, connection_id)

    if not connection:
        raise_http_exception(Error.INVALID_CONNECTION_ID)

    for detail in connection.details:
        chatflow = services.bot_builder.chatflow.get(
            db, id=detail['chatflow_id'], user_id=current_user.id
        )
        detail['chatflow_id'] = chatflow.uuid

    account = services.instagram_page.get(db, connection.account_id)
    return schemas.Connection(
        id=connection.uuid,
        name=connection.name,
        description=connection.description,
        account_id=account.uuid,
        application_name=connection.application_name,
        details=connection.details,
    )


@router.delete('/{connection_id}', status_code=status.HTTP_200_OK)
def delete_connection(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client),
    connection_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    connection = services.connection.get_by_uuid(db, connection_id)
    key = f'{connection.application_name}+{str(connection.account_id)}'

    remove_data_from_cache(redis_client, key=key)

    if connection.user_id != current_user.id:
        raise_http_exception(Error.CONNECTION_NOT_FOUND)

    services.connection.remove(db, id=connection.id)
    return


@router.put('/{connection_id}', response_model=schemas.Connection)
def update_connection(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.ConnectionUpdate,
    redis_client: Redis = Depends(deps.get_redis_client),
    connection_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    account = services.instagram_page.get_by_uuid(db, obj_in.account_id)
    if not account:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    connection = services.connection.get_by_application_name_and_account_id(
        db, application_name=obj_in.application_name, account_id=account.id
    )

    if connection and connection.uuid != connection_id:
        raise_http_exception(Error.CONNECTION_EXIST)

    old_connection = services.connection.get_by_uuid(db, connection_id)
    key = f'{old_connection.application_name}+{str(old_connection.account_id)}'

    if old_connection.user_id != current_user.id:
        raise_http_exception(Error.CONNECTION_NOT_FOUND)
    if not old_connection:
        raise_http_exception(Error.CONNECTION_NOT_FOUND)

    remove_data_from_cache(redis_client, key=key)

    obj_in.account_id = account.id
    details = copy.deepcopy(obj_in.details)

    for detail in obj_in.details:
        chatflow = services.bot_builder.chatflow.get_by_uuid(db, detail['chatflow_id'])
        detail['chatflow_id'] = chatflow.id

    connection = services.connection.update(
        db, db_obj=old_connection, obj_in=obj_in, user_id=current_user.id
    )

    return schemas.Connection(
        id=connection.uuid,
        name=obj_in.name,
        description=obj_in.description,
        application_name=obj_in.application_name,
        details=details,
        account_id=account.uuid,
    )
