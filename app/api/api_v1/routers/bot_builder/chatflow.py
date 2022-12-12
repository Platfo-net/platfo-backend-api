from typing import Any
from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from pydantic.types import UUID4

from app.constants.errors import Error
from app.constants.role import Role

router = APIRouter(prefix="/chatflow")


@router.post("", response_model=schemas.bot_builder.Chatflow)
def create_chatflow(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.bot_builder.ChatflowCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    chatflow = services.bot_builder.chatflow.create(
        db, obj_in=obj_in, user_id=current_user.id
    )
    return chatflow


@router.delete("/{chatflow_id}")
def delete_chatflow(
    *,
    db: Session = Depends(deps.get_db),
    chatflow_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    chatflow = services.bot_builder.chatflow.get(
        db, id=chatflow_id, user_id=current_user.id
    )
    if not chatflow:
        raise HTTPException(
            status_code=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID["status_code"],
            detail=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID["text"],
        )

    services.bot_builder.chatflow.delete_chatflow(db, id=chatflow_id)
    return


@router.get("/all", response_model=schemas.bot_builder.ChatflowListApi)
def get_user_chatflows(
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

    pagination, chatflows = services.bot_builder.chatflow.get_multi(
        db, user_id=current_user.id, page=page, page_size=page_size
    )
    items = [
        schemas.bot_builder.Chatflow(
            is_active=chatflow.is_active,
            name=chatflow.name,
            user_id=chatflow.user_id,
            created_at=chatflow.created_at,
            updated_at=chatflow.updated_at,
            id=chatflow.id,
        )
        for chatflow in chatflows
        if len(chatflows) > 0
    ]

    return schemas.bot_builder.ChatflowListApi(items=items, pagination=pagination)
