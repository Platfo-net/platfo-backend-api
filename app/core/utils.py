from pydantic import UUID4

from app import models


def chatflow_ui_parse(chatflow_id: UUID4, nodes, edges):
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
        str(edge.from_widget) for edge in edges if edge.to_id == head_node.id
    ]

    obj = models.bot_builder.Node(
        id=head_node.id,
        title=head_node.text,
        chatflow_id=chatflow_id,
        from_widget=from_widget,
        widget=widget,
        quick_replies=quick_replies,
        is_head=True,
    )

    objs.append(obj)

    nodes = [node for node in nodes if node.id not in [start_node.id, head_node.id]]

    for node in nodes:
        widget, quick_replies = widget_mapper(node.data, node.id)
        from_widget = [str(edge.from_widget) for edge in edges if edge.to_id == node.id]

        obj = models.bot_builder.Node(
            id=node.id,
            title=node.text,
            chatflow_id=chatflow_id,
            from_widget=from_widget,
            widget=widget,
            quick_replies=quick_replies,
            is_head=False,
        )

        objs.append(obj)

    return objs


def widget_mapper(data, node_id):
    if data["type"] == "TEXT":
        widget = {
            "widget_type": data["type"],
            "id": str(node_id),
            "message": data["value"],
        }

    if data["type"] == "MENU":
        choices = data["choices"]
        widget = {
            "widget_type": data["type"],
            "id": str(node_id),
            "title": str(data["question"]),
            "choices": [
                {"id": str(choice["value"]), "text": choice["label"]}
                for choice in choices
            ],
        }

    replies = data["quickReplies"] if data["quickReplies"] else []

    quick_replies = [
        {"id": reply["value"], "text": reply["label"]} for reply in replies
    ]
    return widget, quick_replies
