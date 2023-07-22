from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.role import Role
from app.core.utils import chatflow_ui_parse

router = APIRouter(prefix='/chatflow-ui')


@router.get('/nodes/all/{chatflow_id}')
def get_chatflow_nodes_edges(
    *,
    db: Session = Depends(deps.get_db),
    chatflow_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    chatflow: models.bot_builder.Chatflow = services.bot_builder.chatflow.get_by_uuid(
        db, uuid=chatflow_id, user_id=current_user.id
    )

    nodes = services.bot_builder.chatflow_ui.get_node_ui(db, chatflow_id=chatflow.id)
    edges = services.bot_builder.chatflow_ui.get_edge_ui(db, chatflow_id=chatflow.id)

    nodes = [
        schemas.bot_builder.NodeUI(
            id=node.uuid,
            text=node.text,
            width=node.width,
            height=node.height,
            data=node.data,
            ports=node.ports,
            has_delete_action=node.has_delete_action,
            has_edit_action=node.has_edit_action,
        )
        for node in nodes
    ]

    edges = [
        schemas.bot_builder.Edge(
            id=edge.uuid,
            from_id=edge.from_id,
            to_id=edge.to_id,
            from_port=edge.from_port,
            to_port=edge.to_port,
            from_widget=edge.from_widget,
            text=edge.text,
        )
        for edge in edges
    ]

    return schemas.bot_builder.ChatflowUI(
        chatflow_id=chatflow.uuid,
        name=chatflow.name,
        nodes=nodes,
        edges=edges,
    )


@router.post('/{chatflow_id}')
def create_chatflow_nodes_edges(
    *,
    db: Session = Depends(deps.get_db),
    chatflow_id: UUID4,
    obj_in: schemas.bot_builder.ChatflowUI,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    chatflow = services.bot_builder.chatflow.get_by_uuid(
        db, uuid=chatflow_id, user_id=current_user.id)

    db.query(models.bot_builder.NodeUI).filter(
        models.bot_builder.NodeUI.chatflow_id == chatflow.id
    ).delete()

    db.query(models.bot_builder.Edge).filter(
        models.bot_builder.Edge.chatflow_id == chatflow.id
    ).delete()

    services.bot_builder.chatflow.update(
        db,
        db_obj=chatflow,
        obj_in=schemas.bot_builder.ChatflowUpdate(is_active=True, name=obj_in.name),
    )

    new_nodes = []
    for node in obj_in.nodes:
        db_obj = models.bot_builder.NodeUI(
            uuid=node.id,
            text=node.text,
            width=node.width,
            height=node.height,
            data=node.data,
            ports=node.ports,
            has_delete_action=node.has_delete_action,
            has_edit_action=node.has_edit_action,
            chatflow_id=chatflow.id,
        )

        new_nodes.append(db_obj)

    new_edges = []
    for edge in obj_in.edges:
        db_obj = models.bot_builder.Edge(
            uuid=edge.id,
            from_id=edge.from_id,
            to_id=edge.to_id,
            from_port=edge.from_port,
            to_port=edge.to_port,
            chatflow_id=chatflow.id,
            from_widget=edge.from_widget,
            text=edge.text,
        )
        new_edges.append(db_obj)

    services.bot_builder.chatflow_ui.create_bulk_chatflow(
        db, nodes=new_nodes, edges=new_edges
    )

    services.bot_builder.node.delete_chatflow_nodes(db, chatflow_id=chatflow.id)
    nodes = chatflow_ui_parse(
        chatflow_id=chatflow.id, nodes=obj_in.nodes, edges=obj_in.edges
    )

    services.bot_builder.node.create_bulk_nodes(db, nodes=nodes)
    return obj_in
