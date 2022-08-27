from typing import Any, List
from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, \
    HTTPException, Security, status
from sqlalchemy.orm import Session
from pydantic.types import UUID4

from app.constants.errors import Error
from app.constants.role import Role
from app.models.notification import Notification
from app.models.notification_user import NotificationUser


router = APIRouter(prefix="/notification", tags=["Notification"])


@router.get("/all", response_model=schemas.NotificationListApi)
def get_notifications_list(
    *,
    db: Session = Depends(deps.get_db),
    page: int = 0,
    page_size: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    notifications = services.notification.get_by_multi(
        db,
        skip=page,
        limit=page_size
    )
    return notifications


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

    notification = services.notification.create(
        db,
        obj_in=obj_in,
    )
    return notification


@router.put("/{notification_id}", response_model=schemas.Notification)
def update_connection(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.NotificationUpdate,
    notification_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),
):

    old_notification = services.notification.get(db, id=notification_id)

    if old_notification.id != notification_id:
        raise HTTPException(
            status_code=400,
        )

    if not old_notification:  # todo
        raise HTTPException(
            status_code=404)

    notification = services.notification.update(
        db, db_obj=old_notification, obj_in=obj_in)

    return notification


@router.delete("/{notification_id}")
def delete_notification(
    *,
    db: Session = Depends(deps.get_db),
    notification_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    old_notification = services.notification.get(
        db,
        id=notification_id,
    )
    if old_notification.id != notification_id:
        raise HTTPException(
            status_code=400,
        )
    if not old_notification:
        raise HTTPException(
            status_code=404
        )

    services.notification.remove(db, id=notification_id)
    return


@router.get("/test-get-all")
def delete_notification(
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    notification_user = db.query(models.NotificationUser
                                 ).filter(
        models.NotificationUser.user_id == "a862d48c-c69a-429b-9ea7-8922fb12a3fb"
    ).with_entities(models.NotificationUser.notification_id).all()

    readed_notifications = [
        n.notification_id for n in notification_user if len(notification_user)]

    notifications = db.query(models.Notification).filter(
        models.Notification.is_visible == True).all()

    return [schemas.NotificationList(
        id = notification.id,
        title=notification.title,
        description=notification.description,
        created_at=notification.created_at,
        is_readed=True if notification.id in readed_notifications else False
    )
        for notification in notifications
    ]
