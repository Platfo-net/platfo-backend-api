from typing import Any, List

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session


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

    connections = services.connection.get_by_user_and_account_id(
        db, user_id=current_user.id, account_id=account_id
    )
    new_connections = []

    for connection in connections:
        account = services.instagram_page.get(db, id=connection.account_id)
        new_connections.append(
            schemas.Connection(
                account=schemas.Account(
                    id=account.id,
                    username=account.instagram_username,
                    platform="Instagram",
                    profile_image=account.instagram_profile_picture_url,
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
    """
    Endpoint for creating connection
    detail: [{
        "trigger": "string",
        "chatflow_id": "string"
      }]
    """
    connection = services.connection.get_by_application_name_and_account_id(
        db, application_name=obj_in.application_name, account_id=obj_in.account_id
    )
    if connection:
        raise HTTPException(
            status_code=Error.CONNECTION_EXIST["status_code"],
            detail=Error.CONNECTION_EXIST["text"],
        )

    connection = services.connection.create(
        db, obj_in=obj_in, user_id=current_user.id)

    return connection


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
    """
    Get a connection and it's detail by connecion id.
        all connection chatflows will return in this API

    Be Careful: Send all of connection chatflows in this endpoint

    Args:

    connection_id (UUID4, optional): Id of a connection
    """

    connection = services.connection.get(db, id=connection_id)
    if not connection:
        raise HTTPException(
            status_code=Error.INVALID_CONNECTION_ID["status_code"],
            detail=Error.INVALID_CONNECTION_ID["text"],
        )
    return schemas.Connection(
        id=connection.id,
        name=connection.name,
        description=connection.description,
        account_id=connection.account_id,
        application_name=connection.application_name,
        details=connection.details,
    )


@router.delete("/{connection_id}", status_code=status.HTTP_200_OK)
def delete_connection(
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
    """
    Endpoint for delete a user connection
    Args:
        connection_id (UUID4): Id of a connection related to a user
    """
    connection = services.connection.get(db, id=connection_id)
    if connection.user_id != current_user.id:
        raise HTTPException(
            status_code=Error.CONNECTION_NOT_FOUND["status_code"],
            detail=Error.CONNECTION_NOT_FOUND["detail"],
        )

    services.connection.remove(db, id=connection_id)
    return


@router.put("/{connection_id}", response_model=schemas.Connection)
def update_connection(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.ConnectionUpdate,
    connection_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    """
    Endpoint for update a connection
    Args:
        connection_id (UUID4): Id of a connection related to a user
    """
    connection = services.connection.get_by_application_name_and_account_id(
        db, application_name=obj_in.application_name, account_id=obj_in.account_id
    )
    if connection:
        raise HTTPException(
            status_code=Error.CONNECTION_EXIST["status_code"],
            detail=Error.CONNECTION_EXIST["text"],
        )

    old_connection = services.connection.get(db, id=connection_id)

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

    connection = services.connection.update(
        db, db_obj=old_connection, obj_in=obj_in, user_id=current_user.id
    )

    return connection


@router.put("/chatflow/{state}/{page_id}/")
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
        db,
        account_id=account.id,
        application_name=Application.BOT_BUILDER["name"]
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
