from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from redis.client import Redis
from sqlalchemy.orm import Session

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.cache import remove_data_from_cache
import copy
router = APIRouter(prefix="/connection", tags=["Connection"])


@router.get("/all", response_model=List[schemas.Connection])
def get_list_of_connections(
    *,
    db: Session = Depends(deps.get_db),
    account_id: UUID4 = None,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    """
    Endpoint for getting list of a user connections.

    Args:

        skip (int, optional): Defaults to 0.

        limit (int, optional): Defaults to 20.

        account_id (UUID4, optional): id of account in our system.
        Defaults to None.

    Returns:

        List of a user connection
    """
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
                    platform="Instagram",
                    profile_image=account.profile_picture_url,
                    page_id=account.facebook_page_id,
                ),
                **jsonable_encoder(connection),
            )
        )
    return new_connections


@router.post("/", response_model=schemas.Connection)
def create_connection(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.ConnectionCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    account = services.instagram_page.get_by_uuid(db, obj_in.account_id)
    if not account:
        raise HTTPException(
            status_code=Error.ACCOUNT_NOT_FOUND["status_code"],
            detail=Error.ACCOUNT_NOT_FOUND["text"],
        )
    connection = services.connection.get_by_application_name_and_account_id(
        db, application_name=obj_in.application_name, account_id=account.id
    )
    if connection:
        raise HTTPException(
            status_code=Error.CONNECTION_EXIST["status_code"],
            detail=Error.CONNECTION_EXIST["text"],
        )

    changed_detail_chatflow_id_obj_in = []
    try:
        details = copy.deepcopy(obj_in.details)
        for detail in details:
            chatflow = services.bot_builder.chatflow.get_by_uuid(db, detail["chatflow_id"])
            detail["chatflow_id"] = chatflow.id

    except KeyError:
        raise HTTPException(
            status_code=Error.INVALID_DETAILS["status_code"],
            detail=Error.INVALID_DETAILS["text"],
        )
    connection = services.connection.create(
        db,
        obj_in=obj_in,
        account_id=account.id,
        details=details,
        user_id=current_user.id
    )

    return schemas.Connection(
        id=connection.uuid,
        name=connection.name,
        description=connection.description,
        application_name=connection.application_name,
        details=obj_in.details,
        account_id=obj_in.account_id
    )


@router.get("/{connection_id}", response_model=schemas.Connection)
def get_connection_by_id(
    *,
    db: Session = Depends(deps.get_db),
    connection_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):

    connection = services.connection.get_by_uuid(db, connection_id)

    if not connection:
        raise HTTPException(
            status_code=Error.INVALID_CONNECTION_ID["status_code"],
            detail=Error.INVALID_CONNECTION_ID["text"],
        )
    changed_detail_chatflow_id = []

    for detail in connection.details:
        chatflow = services.bot_builder.chatflow.get(
            db, id=detail["chatflow_id"], user_id=current_user.id)
        detail["chatflow_id"] = chatflow.uuid

    account = services.instagram_page.get(db, connection.account_id)
    return schemas.Connection(
        id=connection.uuid,
        name=connection.name,
        description=connection.description,
        account_id=account.uuid,
        application_name=connection.application_name,
        details=connection.details,
    )


@router.delete("/{connection_id}", status_code=status.HTTP_200_OK)
def delete_connection(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client),
    connection_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    connection = services.connection.get_by_uuid(db, connection_id)
    key = f"{connection.application_name}+{str(connection.account_id)}"

    remove_data_from_cache(redis_client, key=key)

    if connection.user_id != current_user.id:
        raise HTTPException(
            status_code=Error.CONNECTION_NOT_FOUND["status_code"],
            detail=Error.CONNECTION_NOT_FOUND["detail"],
        )

    services.connection.remove(db, id=connection.id)
    return


@router.put("/{connection_id}", response_model=schemas.Connection)
def update_connection(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.ConnectionUpdate,
    redis_client: Redis = Depends(deps.get_redis_client),
    connection_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    account = services.instagram_page.get_by_uuid(db, obj_in.account_id)
    if not account:
        raise HTTPException(
            status_code=Error.ACCOUNT_NOT_FOUND["status_code"],
            detail=Error.ACCOUNT_NOT_FOUND["text"],
        )
    connection = services.connection.get_by_application_name_and_account_id(
        db, application_name=obj_in.application_name, account_id=account.id
    )

    if connection and connection.uuid != connection_id:
        raise HTTPException(
            status_code=Error.CONNECTION_EXIST["status_code"],
            detail=Error.CONNECTION_EXIST["text"],
        )

    old_connection = services.connection.get_by_uuid(db, connection_id)
    key = f"{old_connection.application_name}+{str(old_connection.account_id)}"

    if old_connection.user_id != current_user.id:
        raise HTTPException(
            status_code=Error.CONNECTION_NOT_FOUND["status_code"],
            detail=Error.CONNECTION_NOT_FOUND["detail"],
        )
    if not old_connection:
        raise HTTPException(
            status_code=Error.CONNECTION_NOT_FOUND["status_code"],
            detail=Error.CONNECTION_NOT_FOUND["text"],
        )
    remove_data_from_cache(redis_client, key=key)

    obj_in.account_id = account.id
    details = copy.deepcopy(obj_in.details)

    for detail in obj_in.details:
        chatflow = services.bot_builder.chatflow.get_by_uuid(db, detail["chatflow_id"])
        detail["chatflow_id"] = chatflow.id

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


# @router.put("/chatflow/{state}/{page_id}/" , deprecated=True)
def disable_chatflow_for_page(
    *,
    db: Session = Depends(deps.get_db),
    page_id: str,
    state: str = None,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    """
    Args:
        page_id (UUID4): _description_
        state (str, optional): Options: enable, disable
    """
    from app.constants.application import Application

    account = services.instagram_page.get_by_page_id(db, page_id=page_id)
    connections = services.connection.get_page_connections(
        db, account_id=account.id, application_name=Application.BOT_BUILDER["name"]
    )
    if not len(connections):
        return
    connection = connections[0]
    connection_chatflow = (
        db.query(models.ConnectionChatflow)
        .filter(models.ConnectionChatflow.connection_id == connection.id)
        .first()
    )
    connection_chatflow_status = True if state == "enable" else False
    connection_chatflow.is_active = connection_chatflow_status

    db.add(connection_chatflow)
    db.commit()
    db.refresh(connection_chatflow)
    return
