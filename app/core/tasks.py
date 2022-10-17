from typing import Any, List
from fastapi.exceptions import HTTPException

from app import schemas, services
from app.constants.message_direction import MessageDirection
from app.core import cache
from app.core.instagram_graph_api import graph_api

from .celery import celery

from app.db.session import SessionLocal

from app.api import deps

from app.constants.widget_type import WidgetType


@celery.task
def save_message(
    from_page_id: str = None,
    to_page_id: str = None,
    mid: str = None,
    content: dict = None,
    user_id: Any = None,
    direction: str = None,
    instagram_page_id: str = None,
):

    db = SessionLocal()
    client = deps.get_redis_client()
    if direction == MessageDirection.IN["name"]:
        contact = services.live_chat.contact.get_contact_by_igs_id(
            db, contact_igs_id=from_page_id
        )
        if not contact:
            contact_in = schemas.live_chat.ContactCreate(
                contact_igs_id=from_page_id, user_page_id=to_page_id, user_id=user_id
            )
            new_contact = services.live_chat.contact.create(db, obj_in=contact_in)

            try:
                user_data = cache.get_user_data(
                    client, db, instagram_page_id=instagram_page_id
                ).to_dict()

            except Exception:
                raise HTTPException(status_code=400)

            information = graph_api.get_contact_information_from_facebook(
                contact_igs_id=new_contact.contact_igs_id,
                page_access_token=user_data["facebook_page_token"],
            )
            services.live_chat.contact.set_information(
                db,
                contact_igs_id=from_page_id,
                information=information,
            )

    if direction == MessageDirection.IN["name"]:
        services.live_chat.contact.update_last_message(
            db, contact_igs_id=from_page_id, last_message=content
        )

    else:
        services.live_chat.contact.update_last_message(
            db, contact_igs_id=to_page_id, last_message=content
        )

    report = services.live_chat.message.create(
        db,
        obj_in=schemas.live_chat.MessageCreate(
            from_page_id=from_page_id,
            to_page_id=to_page_id,
            content=content,
            mid=mid,
            user_id=user_id,
            direction=direction,
        ),
    )
    return report


@celery.task
def send_widget(
    widget: dict,
    quick_replies: List[dict],
    contact_igs_id: str,
    payload: str,
    user_page_data: dict,
):
    db = SessionLocal()

    while widget["widget_type"] in (WidgetType.TEXT["name"], WidgetType.MEDIA["name"]):
        if widget["widget_type"] == WidgetType.MEDIA["name"]:
            graph_api.send_media(
                widget["title"],
                widget["image"],
                from_id=user_page_data["facebook_page_id"],
                to_id=contact_igs_id,
                page_access_token=user_page_data["facebook_page_token"],
            )
        if widget["widget_type"] == WidgetType.TEXT["name"]:
            graph_api.send_text_message(
                text=widget["message"],
                from_id=user_page_data["facebook_page_id"],
                to_id=contact_igs_id,
                page_access_token=user_page_data["facebook_page_token"],
            )

        save_message(
            from_page_id=user_page_data["facebook_page_id"],
            to_page_id=contact_igs_id,
            mid=None,
            content=widget,
            user_id=user_page_data["user_id"],
            direction=MessageDirection.OUT["name"],
        )

        payload = widget["id"]
        node = services.bot_builder.node.get_next_node(db, from_id=payload)
        if node is None:
            break
        widget = node.widget
        quick_replies = node.quick_replies

    if widget["widget_type"] == "MENU":
        graph_api.send_menu(
            widget,
            quick_replies,
            from_id=user_page_data["facebook_page_id"],
            to_id=contact_igs_id,
            page_access_token=user_page_data["facebook_page_token"],
        )
        save_message(
            from_page_id=user_page_data["facebook_page_id"],
            to_page_id=contact_igs_id,
            content=widget,
            user_id=user_page_data["user_id"],
            direction=MessageDirection.OUT["name"],
        )
    return widget
