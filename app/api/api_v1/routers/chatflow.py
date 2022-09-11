from typing import Any, List
from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, \
    HTTPException, Security
from sqlalchemy.orm import Session
from pydantic.types import UUID4

from app.constants.errors import Error
from app.constants.role import Role

router = APIRouter(prefix="/chatflow", tags=["Chatflow"])


@router.post("", response_model=schemas.Chatflow)
def create_chatflow(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.ChatflowCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),

) -> Any:

    chatflow = services.chatflow.create(
        db,
        obj_in=obj_in,
        user_id=current_user.id
    )
    # node = services.node.create(db, obj_in=schemas.NodeCreate(
    #     title="Start",
    #     chatflow_id=chatflow.id,
    #     is_head=True
    # ))
    # services.node.add_widget(db, obj_in=dict(
    #     widget_type="START"), node_id=node.id)
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
    chatflow = services.chatflow.get(
        db,
        id=chatflow_id,
        user_id=current_user.id
    )
    if not chatflow:
        raise HTTPException(
            status_code=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID['status_code'],
            detail=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID['text'],
        )

    services.chatflow.remove(db, id=chatflow_id)
    return


@router.get("/all", response_model=List[schemas.Chatflow])
def get_user_chatflows(
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

    return services.chatflow.get_multi(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
