import uuid
from fastapi.encoders import jsonable_encoder
from typing import Any, List

from pydantic import UUID4

from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from app.constants.errors import Error
from app.constants.widget_type import WidgetType
from app.constants.role import Role


router = APIRouter(prefix="/node", tags=["Node"])


@router.get("/all/{chatflow_id}", response_model=List[schemas.Node])
def get_all_nodes(
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
        db, id=chatflow_id, user_id=current_user.id)

    if not chatflow:
        raise HTTPException(
            status_code=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID['status_code'],
            detail=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID['text'],
        )

    nodes = services.node.get_nodes(db, chatflow_id=chatflow_id)
    return nodes


@router.post("/full", response_model=schemas.Node)
def create_full_node(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.FullNodeCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    chatflow = services.chatflow.get(
        db, id=obj_in.chatflow_id, user_id=current_user.id)

    if not chatflow:
        raise HTTPException(
            status_code=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID['status_code'],
            detail=Error.NO_CHATFLOW_WITH_THE_GIVEN_ID['text'],
        )
    node_in = schemas.NodeCreate(
        title=obj_in.title,
        chatflow_id=obj_in.chatflow_id,
        is_head=obj_in.is_head
    )
    quick_replies = jsonable_encoder(obj_in.quick_replies)

    node = services.node.create(db, obj_in=node_in)

    if obj_in.widget_type == WidgetType.TEXT["name"]:
        obj_in = dict(id=str(uuid.uuid4()),
                      widget_type=WidgetType.TEXT["name"],
                      **jsonable_encoder(obj_in.widget))

    elif obj_in.widget_type == WidgetType.MEDIA["name"]:
        obj_in = dict(id=str(uuid.uuid4()),
                      widget_type=WidgetType.MEDIA["name"],
                      title=obj_in.widget["title"],
                      image=obj_in.widget["image"]
                      )

    elif obj_in.widget_type == WidgetType.MENU["name"]:
        obj_in = jsonable_encoder(obj_in.widget)
        obj_in["widget_type"] = WidgetType.MENU["name"]
        obj_in["choices"] = [dict(id=str(uuid.uuid4()), text=ch["text"])
                             for ch in obj_in["choices"]]

    node = services.node.add_widget(db, obj_in=obj_in, node_id=node.id)
    node = services.node.add_quick_reply(
        db, obj_in=quick_replies, node_id=node.id)
    return node


@router.get("/connect/{node_id}/{from_id}", response_model=schemas.Node)
def connect_widget_to_node(
    *,
    db: Session = Depends(deps.get_db),
    node_id: UUID4,
    from_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    node = services.node.get(db, id=node_id)

    if not node:
        raise HTTPException(
            status_code=Error.NO_NODE_WITH_THE_GIVEN_ID['status_code'],
            detail=Error.NO_NODE_WITH_THE_GIVEN_ID['text'],
        )

    chatflow = services.chatflow.get(
        db, id=node.chatflow_id, user_id=current_user.id)

    if not chatflow:
        raise HTTPException(
            status_code=Error.NO_CHATFLOW_RELATED_TO_THIS_NODE['status_code'],
            detail=Error.NO_CHATFLOW_RELATED_TO_THIS_NODE['text'],
        )

    return services.node.connect(db, from_id=from_id, node_id=node_id)
