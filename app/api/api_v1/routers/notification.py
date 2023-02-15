from typing import Any
from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException, Security
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
            deps.get_current_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
) -> Any:
    current_user_role_name = services.role.get(db, current_user.role_id).name
    if current_user_role_name == Role.ADMIN["name"]:
        notifications, pagination = services.notification.get_by_multi(
            db,
            page=page,
            page_size=page_size,
        )
        notifications_dto = [
            schemas.NotificationListItem(
                id=notification.uuid,
                title=notification.title,
                description=notification.description,
                created_at=notification.created_at,
            )
            for notification in notifications
        ]
        notification_list = schemas.NotificationListApi(
            items=notifications_dto, pagination=pagination
        )
        return notification_list

    notifications, pagination = services.notification.get_by_multi_for_user(
        db, page=page, page_size=page_size, user_id=current_user.id
    )
    return schemas.NotificationListApi(items=notifications, pagination=pagination)


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
    return schemas.Notification(
        id=notification.uuid,
        title=notification.title,
        description=notification.description,
        created_at=notification.created_at,
    )


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
    notification = services.notification.get_by_uuid(db, id)
    if not notification:
        raise HTTPException(
            status_code=Error.NOTIFICATON_NOT_FOUND["status_code"],
            detail=Error.NOTIFICATON_NOT_FOUND["text"],
        )
    notification = services.notification.update(db, db_obj=notification, obj_in=obj_in)

    return schemas.Notification(
        id=notification.uuid,
        title=notification.title,
        description=notification.description,
        created_at=notification.created_at,
    )


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
    notification = services.notification.get_by_uuid(db, id)
    if not notification:
        raise HTTPException(
            status_code=Error.NOTIFICATON_NOT_FOUND["status_code"],
            detail=Error.NOTIFICATON_NOT_FOUND["text"],
        )

    services.notification.remove(db, id=notification.id)
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
                Role.ADMIN["name"],
            ],
        ),
):
    notification = services.notification.get_by_uuid(db, id)
    if not notification:
        raise HTTPException(
            status_code=Error.NOTIFICATON_NOT_FOUND["status_code"],
            detail=Error.NOTIFICATON_NOT_FOUND["text"],
        )
    if services.notification_user.get(
            db,
            notification_id=notification.id,
            user_id=current_user.id
    ):
        raise HTTPException(
            status_code=Error.NOTIFICATION_ALREADY_READED["status_code"],
            detail=Error.NOTIFICATION_ALREADY_READED["text"],
        )

    services.notification_user.create(db, notification_id=notification.id, user_id=current_user.id)
    return
