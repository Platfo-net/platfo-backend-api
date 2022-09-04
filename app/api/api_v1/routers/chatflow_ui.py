
from fastapi import APIRouter, Depends, Security, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role

router = APIRouter(prefix="/chatflow-ui", tags=["ChatflowUI"])


@router.get("/ndoes/all/{chatflow_id}")
def get_chatflow_nodes_edges(
        *,
        db: Session = Depends(deps.get_db),
        chatflow_id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
):

    nodes = db.query(models.NodeUI).filter(
        models.NodeUI.chatflow_id == chatflow_id).all()
    edges = db.query(models.Edge).filter(
        models.Edge.chatflow_id == chatflow_id).all()

    nodes = [
        schemas.NodeUI(
            id=node.id,
            text=node.name,
            width=node.width,
            heigth=node.heigth,
            data=node.data,
            ports=node.ports,
            hasDeleteAction=node.hasDeleteAction,
            hasEditAction=node.hasEditAction

        )for node in nodes
    ]

    edges = [
        schemas.Edge(
            id=edge.id,
            from_id=edge.from_id,
            to_id=edge.to_id,
            fromPort=edge.fromPort,
            toPort=edge.toPort
        ) for edge in edges
    ]

    return schemas.ChatflowUI(
        nodes=nodes,
        edges=edges,
    )


@router.post("/{chatflow_id}")
def create_chatflow_nodes_edges(
        *,
        db: Session = Depends(deps.get_db),
        chatflow_id: UUID4,
        obj_in: schemas.ChatflowUI,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
):

    db.query(models.NodeUI).filter(
        models.NodeUI.chatflow_id == chatflow_id).delete()
    db.query(models.Edge).filter(
        models.Edge.chatflow_id == chatflow_id).delete()

    for node in obj_in.nodes:
        db_obj = models.NodeUI(
            id=node.id,
            text=node.text,
            width=node.width,
            heigth=node.heigth,
            data=node.data,
            ports=node.ports,
            hasDeleteAction=node.hasDeleteAction,
            hasEditAction=node.hasEditAction,
            chatflow_id=chatflow_id
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    for edge in obj_in.edges:
        db_obj = models.Edge(
            id=edge.id,
            from_id=edge.from_id,
            to_id=edge.to_id,
            fromPort=edge.fromPort,
            toPort=edge.toPort,
            chatflow_id=chatflow_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return obj_in
