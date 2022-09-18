from typing import List
from uuid import uuid4
from app import services, models, schemas
from app.api import deps
from app.constants.message_direction import MessageDirection
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.instagram_graph_api import graph_api
from app.core import tasks
from app.constants.widget_type import WidgetType

router = APIRouter(prefix="/message", tags=["Messages"])


@router.get("/archive/{page_id}/{contact_igs_id}",
            response_model=List[schemas.Message])
def get_archive(
    *,
    db: Session = Depends(deps.get_db),
    contact_igs_id: str,
    page_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):

    messages = services.message.get_pages_messages(
        db,
        contact_igs_id=contact_igs_id,
        page_id=page_id,
        skip=skip,
        limit=limit
    )
    new_messages = []
    messages = reversed(messages)
    for message in list(messages):
        new_message = schemas.Message(
            id=message.id,
            from_page_id=message.from_page_id,
            to_page_id=message.to_page_id,
            content=message.content,
            user_id=message.user_id,
            mid=message.mid,
            send_at=message.send_at
        )
        new_messages.append(new_message)

    return new_messages


@router.post("/send/{from_page_id}/{to_contact_igs_id}")
def send_message(
    *,
    db: Session = Depends(deps.get_db),
    from_page_id: str,
    to_contact_igs_id: str,
    obj_in: schemas.SendMessage,
    backgroud: BackgroundTasks,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):

    instagram_page = services.instagram_page.get_by_page_id(
        db,
        page_id=from_page_id
    )
    backgroud.add_task(graph_api.send_text_message,
                       obj_in.text,
                       from_page_id,
                       to_contact_igs_id,
                       instagram_page.facebook_page_token
                       )
    message_in = dict(
        from_page_id=from_page_id,
        to_page_id=to_contact_igs_id,
        content={
            "message": obj_in.text,
            "widget_type": WidgetType.TEXT["name"],
            "id": str(uuid4()),
        },
        user_id=str(current_user.id),
        direction=MessageDirection.OUT["name"],
        mid=None
    )

    tasks.save_message(
        obj_in=message_in
    )
    return
