from typing import Any, List
from uuid import uuid4
from app import schemas, services
from app.api import deps
from app.constants.impression import Impression
from app.db.session import SessionLocal
from app.core import cache
from app.core.bot_builder.instagram_graph_api import graph_api
from app.core.bot_builder.extra_classes import InstagramData
from app.constants.message_direction import MessageDirection
from app.constants.widget_type import WidgetType
from app.constants.webhook_type import WebhookType
from app.constants.trigger import Trigger
from app.constants.application import Application
from app.core.celery import celery
from sqlalchemy.orm import Session

@celery.task
def webhook_proccessor(facebook_webhook_body):
    db : Session = SessionLocal()
    redis_client = deps.get_redSessionLocalis_client()
    instagram_data = InstagramData()
    instagram_data.parse(facebook_webhook_body)

    try:
        user_page_data = cache.get_user_data(
            redis_client, db, instagram_page_id=instagram_data.recipient_id
        )
    except Exception:
        db.close()
        return 0

    match instagram_data.type:
        case WebhookType.CONTACT_MESSAGE_ECHO:
            return None
        case WebhookType.MESSAGE_SEEN:
            services.postman.campaign_contact.seen_message(db, mid=instagram_data.mid)
            db.close()
            return None
        case WebhookType.COMMENT:
            save_comment(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                user_id=user_page_data.user_id,
                instagram_page_id=instagram_data.recipient_id,
            )
            db.close()
            return None

        case WebhookType.LIVE_COMMENT:
            save_comment(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                user_id=user_page_data.user_id,
                instagram_page_id=instagram_data.recipient_id,
            )
            db.close()
            return None

        case WebhookType.DELETE_MESSAGE:
            return services.live_chat.message.remove_message_by_mid(
                db, mid=instagram_data.mid
            )

        case WebhookType.STORY_MENTION:
            saved_data = {
                "url": instagram_data.url,
                "widget_type": "STORY_MENTION",
                "id": str(uuid4()),
            }

            save_message(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                mid=instagram_data.mid,
                content=saved_data,
                user_id=user_page_data.user_id,
                direction=MessageDirection.IN["name"],
                instagram_page_id=instagram_data.recipient_id,
            )
            db.close()
            return None
        case WebhookType.STORY_REPLY:
            saved_data = {
                "url": instagram_data.story_url,
                "widget_type": "STORY_REPLY",
                "message": instagram_data.message_detail,
                "id": str(uuid4()),
            }
            save_message(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                mid=instagram_data.mid,
                content=saved_data,
                user_id=user_page_data.user_id,
                direction=MessageDirection.IN["name"],
                instagram_page_id=instagram_data.recipient_id,
            )
            db.close()
            return None

    saved_data = {
        "message": instagram_data.text,
        "widget_type": WidgetType.TEXT["name"],
        "id": str(uuid4()),
    }

    save_message(
        from_page_id=instagram_data.sender_id,
        to_page_id=user_page_data.facebook_page_id,
        mid=instagram_data.mid,
        content=saved_data,
        user_id=user_page_data.user_id,
        direction=MessageDirection.IN["name"],
        instagram_page_id=instagram_data.recipient_id,
    )
    if instagram_data.payload:
        chatflow_id = cache.get_node_chatflow_id(
            db, redis_client, widget_id=instagram_data.payload
        )
        if not chatflow_id:
            db.close()
            return None
        connection = cache.get_connection_data(
            db,
            redis_client,
            application_name=Application.BOT_BUILDER["name"],
            account_id=user_page_data.account_id,
        )
        if not connection:
            db.close()
            return None
        connection_exist = False
        for detail in connection.details:
            if detail["chatflow_id"] == chatflow_id:
                connection_exist = True
        if not connection_exist:
            db.close()
            return None

        node = services.bot_builder.node.get_next_node(
            db, from_id=instagram_data.payload
        )
        send_widget.delay(
            widget=node.widget,
            quick_replies=node.quick_replies,
            contact_igs_id=instagram_data.sender_id,
            payload=instagram_data.payload,
            user_page_data=user_page_data.to_dict(),
        )
    else:
        chatflow_id = None
        connections = services.connection.get_page_connections(
            db, account_id=user_page_data.account_id, application_name="BOT_BUILDER"
        )
        if connections is None:
            db.close()
            return None

        for connection in connections:
            details = connection.details
            for detail in details:
                if detail["trigger"] == Trigger.Message["name"]:
                    chatflow_id = detail["chatflow_id"]

        if chatflow_id is None:
            db.close()
            return None
        try:
            node = services.bot_builder.node.get_chatflow_head_node(
                db, chatflow_id=chatflow_id
            )
            send_widget.delay(
                widget=node.widget,
                quick_replies=node.quick_replies,
                contact_igs_id=instagram_data.sender_id,
                payload=instagram_data.payload,
                user_page_data=user_page_data.to_dict(),
            )
        except Exception:
            pass
    db.close()
    return 0


@celery.task
def save_comment(
    from_page_id: str = None,
    to_page_id: str = None,
    user_id: Any = None,
    instagram_page_id: str = None,
):
    db = SessionLocal()

    contact = services.live_chat.contact.get_contact_by_igs_id(
        db, contact_igs_id=from_page_id
    )
    if not contact:
        contact_in = schemas.live_chat.ContactCreate(
            contact_igs_id=from_page_id,
            user_page_id=to_page_id,
            user_id=user_id,
            comment_count=1,
            first_impression=Impression.COMMENT,
        )
        services.live_chat.contact.create(db, obj_in=contact_in)

        information = {
            "username": "unknown",
            "profile_image": "404",
            "name": "unknown",
            "followers_count": 0,
            "is_verified_user": False,
            "is_user_follow_business": False,
            "is_business_follow_user": False,
        }
        services.live_chat.contact.set_information(
            db,
            contact_igs_id=from_page_id,
            information=information,
        )
        db.close()
        return 0

    services.live_chat.contact.update_last_comment_count(
        db, contact_igs_id=contact.contact_igs_id
    )
    db.close()
    return 0


@celery.task
def save_live_comment(
    from_page_id: str = None,
    to_page_id: str = None,
    user_id: Any = None,
    instagram_page_id: str = None,
):
    db = SessionLocal()
    client = deps.get_redis_client()

    contact = services.live_chat.contact.get_contact_by_igs_id(
        db, contact_igs_id=from_page_id
    )
    if not contact:
        contact_in = schemas.live_chat.ContactCreate(
            contact_igs_id=from_page_id,
            user_page_id=to_page_id,
            user_id=user_id,
            live_comment_count=1,
            first_impression=Impression.LIVE_COMMENT,
        )
        new_contact = services.live_chat.contact.create(db, obj_in=contact_in)

        try:
            user_data = cache.get_user_data(
                client, db, instagram_page_id=instagram_page_id
            ).to_dict()

        except Exception:
            db.close()
            return 0

        information = graph_api.get_contact_information_from_facebook(
            contact_igs_id=new_contact.contact_igs_id,
            page_access_token=user_data["facebook_page_token"],
        )
        services.live_chat.contact.set_information(
            db,
            contact_igs_id=from_page_id,
            information=information,
        )
        db.close()
        return 0

    services.live_chat.contact.update_last_live_comment_count(
        db, contact_igs_id=contact.contact_igs_id
    )
    db.close()
    return 0


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
                contact_igs_id=from_page_id,
                user_page_id=to_page_id,
                user_id=user_id,
                message_count=1,
                first_impression=Impression.MESSAGE,
            )
            new_contact = services.live_chat.contact.create(db, obj_in=contact_in)

            try:
                user_data = cache.get_user_data(
                    client, db, instagram_page_id=instagram_page_id
                ).to_dict()

            except Exception:
                db.close()
                return 0

            information = graph_api.get_contact_information_from_facebook(
                contact_igs_id=new_contact.contact_igs_id,
                page_access_token=user_data["facebook_page_token"],
            )
            services.live_chat.contact.set_information(
                db,
                contact_igs_id=from_page_id,
                information=information,
            )
        else:
            services.live_chat.contact.update_last_message_count(
                db, contact_igs_id=from_page_id
            )

    if direction == MessageDirection.IN["name"]:
        services.live_chat.contact.update_last_message(
            db, contact_igs_id=from_page_id, last_message=str(content)
        )

    else:
        services.live_chat.contact.update_last_message(
            db, contact_igs_id=to_page_id, last_message=str(content)
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
    db.close()
    return report


@celery.task
def send_widget(
    widget: dict,
    quick_replies: List[dict],
    contact_igs_id: str,
    payload: str,
    user_page_data: dict,
):
    db :Session = SessionLocal()

    while widget["widget_type"] in (WidgetType.TEXT["name"], WidgetType.MEDIA["name"]):
        if widget["widget_type"] == WidgetType.MEDIA["name"]:
            mid = graph_api.send_media(
                widget["title"],
                widget["image"],
                from_id=user_page_data["facebook_page_id"],
                to_id=contact_igs_id,
                page_access_token=user_page_data["facebook_page_token"],
            )
        if widget["widget_type"] == WidgetType.TEXT["name"]:
            mid = graph_api.send_text_message(
                text=widget["message"],
                from_id=user_page_data["facebook_page_id"],
                to_id=contact_igs_id,
                page_access_token=user_page_data["facebook_page_token"],
                quick_replies=quick_replies,
            )
        save_message(
            from_page_id=user_page_data["facebook_page_id"],
            to_page_id=contact_igs_id,
            mid=mid,
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
        mid = graph_api.send_menu(
            widget,
            quick_replies,
            from_id=user_page_data["facebook_page_id"],
            to_id=contact_igs_id,
            page_access_token=user_page_data["facebook_page_token"],
        )
        save_message(
            from_page_id=user_page_data["facebook_page_id"],
            to_page_id=contact_igs_id,
            mid=mid,
            content=widget,
            user_id=user_page_data["user_id"],
            direction=MessageDirection.OUT["name"],
        )
    db.close()
    return widget
