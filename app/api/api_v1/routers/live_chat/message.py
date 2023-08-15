from typing import List
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, Security
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.message_direction import MessageDirection
from app.constants.role import Role
from app.constants.widget_type import WidgetType
from app.core.instagram import tasks
from app.core.instagram.graph_api import graph_api
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/message')


@router.get(
    '/archive/{page_id}/{lead_igs_id}',
    response_model=List[schemas.live_chat.Message],
)
def get_archive(
    *,
    db: Session = Depends(deps.get_db),
    lead_igs_id: int,
    page_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    messages = services.live_chat.message.get_page_messages(
        db,
        lead_igs_id=lead_igs_id,
        page_id=page_id,
        skip=skip,
        limit=limit,
    )
    new_messages = []
    messages = reversed(messages)
    for message in list(messages):
        new_message = schemas.live_chat.Message(
            id=message.uuid,
            from_page_id=message.from_page_id,
            to_page_id=message.to_page_id,
            content=message.content,
            user_id=message.user_id,
            mid=message.mid,
            send_at=message.send_at,
        )
        new_messages.append(new_message)

    return new_messages


@router.post('/send/{from_page_id}/{to_lead_igs_id}', deprecated=True)
def send_message(
    *,
    db: Session = Depends(deps.get_db),
    from_page_id: int,
    to_lead_igs_id: int,
    obj_in: schemas.live_chat.MessageSend,
    backgroud: BackgroundTasks,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=from_page_id
    )
    if not instagram_page:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND['status_code'])
    backgroud.add_task(
        graph_api.send_text_message,
        obj_in.text,
        from_page_id,
        to_lead_igs_id,
        instagram_page.facebook_page_token,
    )
    message_in = dict(
        from_page_id=from_page_id,
        to_page_id=to_lead_igs_id,
        content={
            'message': obj_in.text,
            'widget_type': WidgetType.TEXT,
            'id': str(uuid4()),
        },
        user_id=current_user.id,
        direction=MessageDirection.OUT,
        mid=None,
    )

    tasks.save_message(**message_in)
    return
