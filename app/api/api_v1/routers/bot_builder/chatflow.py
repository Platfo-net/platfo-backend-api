from typing import Any

from fastapi import APIRouter, Depends, Security
from pydantic.types import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/chatflow')


@router.post('', response_model=schemas.bot_builder.Chatflow)
def create_chatflow(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.bot_builder.ChatflowCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    chatflow = services.bot_builder.chatflow.create(
        db, obj_in=obj_in, user_id=current_user.id
    )
    return schemas.bot_builder.Chatflow(
        id=chatflow.uuid,
        name=chatflow.name,
        created_at=chatflow.created_at,
        updated_at=chatflow.updated_at,
    )


@router.delete('/{id}')
def delete_chatflow(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    chatflow: models.bot_builder.Chatflow = services.bot_builder.chatflow.get_by_uuid(
        db, uuid=id, user_id=current_user.id)
    if not chatflow:
        raise_http_exception(Error.NO_CHATFLOW_WITH_THE_GIVEN_ID)

    services.bot_builder.chatflow.delete(db, id=chatflow.id)
    return


@router.get('/all', response_model=schemas.bot_builder.ChatflowListApi)
def get_user_chatflows(
    *,
    db: Session = Depends(deps.get_db),
    page: int = 1,
    page_size: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    pagination, chatflows = services.bot_builder.chatflow.get_multi(
        db, user_id=current_user.id, page=page, page_size=page_size
    )
    items = [
        schemas.bot_builder.Chatflow(
            is_active=chatflow.is_active,
            name=chatflow.name,
            created_at=chatflow.created_at,
            updated_at=chatflow.updated_at,
            id=chatflow.uuid,
        )
        for chatflow in chatflows
        if len(chatflows) > 0
    ]

    return schemas.bot_builder.ChatflowListApi(items=items, pagination=pagination)
