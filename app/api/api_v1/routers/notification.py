from typing import Any
from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, \
    HTTPException, Security
from sqlalchemy.orm import Session
from pydantic.types import UUID4
from app.constants.errors import Error

from app.constants.role import Role


router = APIRouter(prefix="/notification", tags=["Notification"])


@router.get("/all", response_model=schemas.NotificationListApi)
def get_notifications_list(
    *,
    db: Session = Depends(deps.get_db),
    page: int = 1,
    page_size: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    """
    Get list of notifications based on role,
    if role is user, it will return status of notification
    else status will be always is_readed=true

    Args:
        page (int, optional): current page. Defaults to 1.
        page_size (int, optional): count of items in a page. Defaults to 20.

    Returns:
        List of notifications and pagination data
    """

    if current_user.role.name == Role.ADMIN["name"]:

        notifications, pagination = services.notification.get_by_multi(
            db,
            page=page,
            page_size=page_size,
        )
        notification_list = schemas.NotificationListApi(
            items=notifications,
            pagination=pagination
        )
        return notification_list

    notifications, pagination = services.notification.\
        get_by_multi_for_user(
            db, page=page, page_size=page_size, user_id=current_user.id
        )
    return schemas.NotificationListApi(
        items=notifications,
        pagination=pagination
    )


@router.post("", response_model=schemas.Notification)
def create_notification(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.NotificationCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),

) -> Any:
    """
    Create a notification by admin.

    Returns:
        Created notification
    """
    notification = services.notification.create(
        db,
        obj_in=obj_in,
    )
    return notification


@router.put("/{id}", response_model=schemas.Notification)
def update_notification(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.NotificationUpdate,
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),
):
    """
    Update existed notification by admin

    Raises:
        404: if notificatin not found.

    Returns:
        _type_: _description_
    """
    notification = services.notification.get(db, id=id)
    if not notification:
        raise HTTPException(
            status_code=Error.NOTIFICATON_NOT_FOUND['status_code'],
            detail=Error.NOTIFICATON_NOT_FOUND['text'],
        )
    notification = services.notification.update(
        db, db_obj=notification, obj_in=obj_in)

    return notification


@router.delete("/{id}")
def delete_notification(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    """
    Delete Notification by id

    Args:
        id (UUID4): id of notification in our system

    Raises:
        404: if notificatin not found

    Returns:
        Any: _description_
    """
    if not services.notification.get(
        db,
        id,
    ):
        raise HTTPException(
            status_code=Error.NOTIFICATON_NOT_FOUND['status_code'],
            detail=Error.NOTIFICATON_NOT_FOUND['text'],
        )

    services.notification.remove(db, id=id)
    return


@router.put("/read/{id}")
def read_notification(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
        ],
    ),
) -> Any:
    """

    Args:
        id (UUID4): Notification id

    Raises:
        404: if notificatin not found
        400: if notificatin readed before

    """

    if not services.notification.get(
        db,
        id=id,
    ):
        raise HTTPException(
            status_code=Error.NOTIFICATON_NOT_FOUND['status_code'],
            detail=Error.NOTIFICATON_NOT_FOUND['text'],
        )
    if services.notification_user.get(db,
                                      notification_id=id,
                                      user_id=current_user.id
                                      ):
        raise HTTPException(
            status_code=Error.NOTIFICATION_ALREADY_READED["status_code"],
            detail=Error.NOTIFICATION_ALREADY_READED["text"]
        )

    return services.notification.read(
        db,
        id=id,
        user_id=current_user.id
    )
