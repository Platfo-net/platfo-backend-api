from uuid import uuid4

from sqlalchemy.orm import Session

from app import schemas, services
from app.api import deps
from app.constants.impression import Impression
from app.constants.message_direction import MessageDirection
from app.constants.webhook_type import WebhookType
from app.constants.widget_type import WidgetType
from app.core import cache
from app.core.bot_builder.extra_classes import InstagramData, SavedMessage, UserData
from app.core.bot_builder.instagram_graph_api import graph_api
from app.core.celery import celery
from app.db.session import SessionLocal


@celery.task
def webhook_proccessor(facebook_webhook_body):
    db: Session = SessionLocal()
    redis_client = deps.get_redis_client()
    instagram_data = InstagramData(facebook_webhook_body)

    try:
        user_page_data = cache.get_user_data(
            redis_client, db, instagram_page_id=instagram_data.recipient_id
        )
    except Exception:
        db.close()
        return None

    match instagram_data.type:
        case WebhookType.MESSAGE_SEEN:
            services.notifier.campaign_contact.seen_message(db, mid=instagram_data.mid)
        case WebhookType.COMMENT:
            save_comment(
                db=db,
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                user_id=user_page_data.user_id,
            )

        case WebhookType.LIVE_COMMENT:
            save_comment(
                db=db,
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                user_id=user_page_data.user_id,
            )

        case WebhookType.DELETE_MESSAGE:
            services.live_chat.message.remove_message_by_mid(db, mid=instagram_data.mid)

        case WebhookType.STORY_MENTION:
            saved_data = {
                "url": instagram_data.url,
                "widget_type": "STORY_MENTION",
                "id": str(uuid4()),
            }
            saved_message = SavedMessage(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                mid=instagram_data.mid,
                content=saved_data,
                user_id=user_page_data.user_id,
                direction=MessageDirection.IN,
                instagram_page_id=instagram_data.recipient_id,
            )
            save_message(db, saved_message, user_page_data)
        case WebhookType.STORY_REPLY:
            saved_data = {
                "url": instagram_data.story_url,
                "widget_type": "STORY_REPLY",
                "message": instagram_data.message_detail,
                "id": str(uuid4()),
            }
            saved_message = SavedMessage(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                mid=instagram_data.mid,
                content=saved_data,
                user_id=user_page_data.user_id,
                direction=MessageDirection.IN,
                instagram_page_id=instagram_data.recipient_id,
            )
            save_message(db, saved_message, user_page_data)
        case WebhookType.CONTACT_MESSAGE:
            saved_data = {
                "message": instagram_data.text,
                "widget_type": WidgetType.TEXT,
                "id": str(uuid4()),
            }
            saved_message = SavedMessage(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                mid=instagram_data.mid,
                content=saved_data,
                user_id=user_page_data.user_id,
                direction=MessageDirection.IN,
                instagram_page_id=instagram_data.recipient_id,
            )

            save_message(db, saved_message, user_page_data)
    db.close()
    return None


def save_comment(
    db: Session,
    from_page_id: int = None,
    to_page_id: int = None,
    user_id: int = None,
):
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
            "username": "",
            "profile_image": "",
            "name": "",
            "followers_count": 0,
            "is_verified_user": True,
            "is_user_follow_business": True,
            "is_business_follow_user": False,
        }
        services.live_chat.contact.set_information(
            db,
            contact_igs_id=from_page_id,
            information=information,
        )
        return 0

    services.live_chat.contact.update_last_comment_count(
        db, contact_igs_id=contact.contact_igs_id
    )
    return 0


def save_message(db: Session, message: SavedMessage, user_data: UserData):
    if message.direction == MessageDirection.IN:
        contact = services.live_chat.contact.get_contact_by_igs_id(
            db, contact_igs_id=message.from_page_id
        )
        if not contact:
            contact_in = schemas.live_chat.ContactCreate(
                contact_igs_id=message.from_page_id,
                user_page_id=message.to_page_id,
                user_id=message.user_id,
                message_count=1,
                first_impression=Impression.MESSAGE,
            )
            new_contact = services.live_chat.contact.create(db, obj_in=contact_in)

            information = graph_api.get_contact_information_from_facebook(
                contact_igs_id=new_contact.contact_igs_id,
                page_access_token=user_data.facebook_page_token,
            )
            services.live_chat.contact.set_information(
                db,
                contact_igs_id=message.from_page_id,
                information=information,
            )
        else:
            services.live_chat.contact.update_last_message_count(
                db, contact_igs_id=message.from_page_id
            )

    if message.direction == MessageDirection.IN:
        services.live_chat.contact.update_last_message(
            db, contact_igs_id=message.from_page_id, last_message=str(message.content)
        )

    else:
        services.live_chat.contact.update_last_message(
            db, contact_igs_id=message.to_page_id, last_message=str(message.content)
        )

    report = services.live_chat.message.create(
        db,
        obj_in=schemas.live_chat.MessageCreate(
            from_page_id=message.from_page_id,
            to_page_id=message.to_page_id,
            content=message.content,
            mid=message.mid,
            user_id=message.user_id,
            direction=message.direction,
        ),
    )
    return report


#
# @celery.task
# def send_widget(
#         widget: dict,
#         quick_replies: List[dict],
#         contact_igs_id: int,
#         user_page_data: dict,
# ):
#     db: Session = SessionLocal()
#     redis_client = deps.get_redis_client()
#
#     while widget["widget_type"] in (WidgetType.TEXT, WidgetType.MEDIA):
#         mid = None
#         if widget["widget_type"] == WidgetType.MEDIA:
#             mid = graph_api.send_media(
#                 widget["title"],
#                 widget["image"],
#                 from_id=user_page_data["facebook_page_id"],
#                 to_id=contact_igs_id,
#                 page_access_token=user_page_data["facebook_page_token"],
#             )
#         if widget["widget_type"] == WidgetType.TEXT:
#             mid = graph_api.send_text_message(
#                 text=widget["message"],
#                 from_id=user_page_data["facebook_page_id"],
#                 to_id=contact_igs_id,
#                 page_access_token=user_page_data["facebook_page_token"],
#                 quick_replies=quick_replies,
#             )
#         saved_message = SavedMessage(
#             from_page_id=user_page_data["facebook_page_id"],
#             to_page_id=contact_igs_id,
#             mid=mid,
#             content=widget,
#             user_id=user_page_data["user_id"],
#             direction=MessageDirection.OUT
#         )
#         save_message(
#             db, redis_client, saved_message
#         )
#
#         payload = widget["id"]
#         node = services.bot_builder.node.get_next_node(db, from_id=payload)
#         if node is None:
#             break
#         widget = node.widget
#         quick_replies = node.quick_replies
#
#     if widget["widget_type"] == "MENU":
#         mid = graph_api.send_menu(
#             widget,
#             quick_replies,
#             from_id=user_page_data["facebook_page_id"],
#             to_id=contact_igs_id,
#             page_access_token=user_page_data["facebook_page_token"],
#         )
#         saved_message = SavedMessage(
#             from_page_id=user_page_data["facebook_page_id"],
#             to_page_id=contact_igs_id,
#             mid=mid,
#             content=widget,
#             user_id=user_page_data["user_id"],
#             direction=MessageDirection.OUT,
#         )
#         save_message(db, redis_client, saved_message)
#     db.close()
#     return widget
