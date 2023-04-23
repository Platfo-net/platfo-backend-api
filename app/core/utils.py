from datetime import timedelta
import random
import re
import string
from pydantic import UUID4
from sqlalchemy.orm import Session
from app import models, services, schemas
from app.constants.message_type import MessageType
from app.core import security
from app.core.bot_builder.extra_classes import SavedMessage
from app.core.config import settings


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


def save_message(
        db: Session,
        saved_message: SavedMessage
):
    services.live_chat.contact.update_last_message(
        db, contact_igs_id=saved_message.to_page_id,
        last_message=saved_message.content.get("text", None)
    )
    report = services.live_chat.message.create(
        db,
        obj_in=schemas.live_chat.MessageCreate(
            from_page_id=saved_message.from_page_id,
            to_page_id=saved_message.to_page_id,
            content=saved_message.content,
            mid=saved_message.mid,
            user_id=saved_message.user_id,
            direction=saved_message.direction,
            type=MessageType.TEXT
        ),
    )
    return report


def create_token(db: Session, *, user: models.User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if not user.role_id:
        role = "GUEST"
    else:
        role = services.role.get(db, id=user.role_id)
        role = role.name
    token_payload = {
        "id": user.id,
        "role": role,
    }
    access_token = security.create_access_token(
        token_payload, expires_delta=access_token_expires
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )


def normalize_phone_number(phone_number):
    if not phone_number:
        return phone_number
    new_phone_number = phone_number
    if phone_number[0] == "0":
        new_phone_number = phone_number[1:]
    return new_phone_number


def normalize_phone_country_code(phone_country_code):
    if not phone_country_code:
        return phone_country_code

    new_phone_country_code = phone_country_code
    if phone_country_code[0:2] == "00":
        new_phone_country_code = phone_country_code[2:]
    if phone_country_code[0] == "+":
        new_phone_country_code = phone_country_code[1:]
    return new_phone_country_code


def validate_password(password) -> bool:
    if len(password) < 8:
        return False
    elif re.search('[0-9]', password) is None:
        return False
    elif re.search('[A-Z]', password) is None:
        return False
    elif re.search('[a-z]', password) is None:
        return False
    return True


def generate_random_token(length: int) -> str:
    return "".join(random.choice(f"{string.ascii_letters}0123456789") for _ in range(64))


def generate_random_code(length: int) -> int:
    return random.randint(10**length, (10**(length + 1)) - 1)
