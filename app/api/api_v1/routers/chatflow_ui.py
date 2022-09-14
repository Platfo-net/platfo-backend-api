
from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import services, models, schemas
from app.api import deps
from app.constants.role import Role

router = APIRouter(prefix="/chatflow-ui", tags=["ChatflowUI"])


@router.get("/nodes/all/{chatflow_id}")
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
    chatflow = db.query(models.Chatflow).filter(
        models.Chatflow.id == chatflow_id).first()

    nodes = db.query(models.NodeUI).filter(
        models.NodeUI.chatflow_id == chatflow_id).all()
    edges = db.query(models.Edge).filter(
        models.Edge.chatflow_id == chatflow_id).all()

    nodes = [
        schemas.NodeUI(
            id=node.id,
            text=node.text,
            width=node.width,
            height=node.height,
            data=node.data,
            ports=node.ports,
            has_delete_action=node.has_delete_action,
            has_edit_action=node.has_edit_action

        )for node in nodes
    ]

    edges = [
        schemas.Edge(
            id=edge.id,
            from_id=edge.from_id,
            to_id=edge.to_id,
            from_port=edge.from_port,
            to_port=edge.to_port,
            from_widget=edge.from_widget,
            text=edge.text,
        ) for edge in edges
    ]

    return schemas.ChatflowUI(
        chatflow_id=chatflow_id,
        name=chatflow.name,
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

    chatflow = services.chatflow.get(db, chatflow_id, current_user.id)

    services.chatflow.update(
        db,
        db_obj=chatflow,
        obj_in=schemas.ChatflowUpdate(
            is_active=True,
            name=obj_in.name
        ))

    new_nodes = []
    for node in obj_in.nodes:
        db_obj = models.NodeUI(
            id=node.id,
            text=node.text,
            width=node.width,
            height=node.height,
            data=node.data,
            ports=node.ports,
            has_delete_action=node.has_delete_action,
            has_edit_action=node.has_edit_action,
            chatflow_id=chatflow_id
        )

        new_nodes.append(db_obj)

    new_edges = []
    for edge in obj_in.edges:
        db_obj = models.Edge(
            id=edge.id,
            from_id=edge.from_id,
            to_id=edge.to_id,
            from_port=edge.from_port,
            to_port=edge.to_port,
            chatflow_id=chatflow_id,
            from_widget=edge.from_widget,
            text=edge.text
        )
        new_edges.append(db_obj)

    services.chatflow_ui.create_bulk_chatflow(
        db, nodes=new_nodes, edges=new_edges
    )

    services.node.delete_chatflow_nodes(db, chatflow_id=chatflow_id)
    nodes = chatflow_ui_parse(chatflow_id=chatflow_id,
                              nodes=obj_in.nodes, edges=obj_in.edges)

    services.node.create_bulk_nodes(db, nodes=nodes)
    return obj_in


def chatflow_ui_parse(
        chatflow_id: UUID4,
        nodes,
        edges
):

    objs = []
    start_node = None
    for node in nodes:
        if node.data["type"] == "START":
            start_node = node

    head_node = None
    for edge in edges:
        if edge.from_id == start_node.id:
            head_node_id = edge.to_id

    for node in nodes:
        if node.id == head_node_id:
            head_node = node

    widget, quick_replies = widget_mapper(head_node.data, head_node.id)
    from_widget = [
        str(edge.from_widget) for edge in edges if edge.to_id == head_node.id]

    obj = models.Node(
        id=head_node.id,
        title=head_node.text,
        chatflow_id=chatflow_id,
        from_widget=from_widget,
        widget=widget,
        quick_replies=quick_replies,
        is_head=True)

    objs.append(obj)

    nodes = [node for node in nodes if node.id not in [
        start_node.id, head_node.id]]

    for node in nodes:
        widget, quick_replies = widget_mapper(node.data, node.id)
        from_widget = [
            str(edge.from_widget) for edge in edges if edge.to_id == node.id]

        obj = models.Node(
            id=node.id,
            title=node.text,
            chatflow_id=chatflow_id,
            from_widget=from_widget,
            widget=widget,
            quick_replies=quick_replies,
            is_head=False)

        objs.append(obj)

    return objs


def widget_mapper(data, node_id):
    if data["type"] == "TEXT":
        widget = {
            "widget_type": data["type"],
            "id": str(node_id),
            "message": data["value"]
        }

    if data["type"] == "MENU":
        choices = data["choices"]
        widget = {
            "widget_type": data["type"],
            "id": str(node_id),
            "title": str(data["question"]),
            "choices": [{
                "id": str(choice["value"]),
                "text":choice["label"]
            }
                for choice in choices
            ]
        }

    replies = data["quickReplies"] if data["quickReplies"] else []

    quick_replies = [
        {
            "id": reply["value"],
            "text": reply["label"]
        }for reply in replies
    ]
    return widget, quick_replies
