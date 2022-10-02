
from typing import Any, List
from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, \
    HTTPException, Security
from sqlalchemy.orm import Session
from pydantic.types import UUID4

from app.constants.errors import Error
from app.constants.role import Role

router = APIRouter(prefix="/chatroom", tags=["Chatroom"])


@router.post("", response_model=schemas.live_chat.Chatroom)
def create_chatroom(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.live_chat.ChatroomCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),

) -> Any:

    chatroom = services.live_chat.chatroom.create(
        db,
        obj_in=obj_in,
        user_id=current_user.id
    )

    return chatroom


@router.delete("/{chatroom_id}")
def delete_chatroom(
    *,
    db: Session = Depends(deps.get_db),
    chatroom_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    chatroom = services.live_chat.chatroom.get(
        db,
        id=chatroom_id,
        user_id=current_user.id
    )
    if not chatroom:
        raise HTTPException(
            status_code=404,
            detail='not found',
        )

    services.live_chat.chatroom.remove(db, id=chatroom_id)
    return


@router.get("/all", response_model=List[schemas.live_chat.Chatroom])
def get_user_chatrooms(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    return services.live_chat.chatroom.get_multi(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
