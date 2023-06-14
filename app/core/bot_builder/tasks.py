
from sqlalchemy.orm import Session

from app.api import deps
from app.constants.webhook_type import WebhookType
from app.core import cache
from app.core.bot_builder.extra_classes import InstagramData
from app.core.celery import celery
from app.db.session import SessionLocal
from app.core.bot_builder.handlers import MessageSeenHandler, CommentHandler, \
    LiveCommentHandler, DeleteMessageHandler, StoryMentionHandler,\
    StoryReplyHandler, ContactMessageHandler


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

    handler = None

    match instagram_data.type:
        case WebhookType.MESSAGE_SEEN:
            handler = MessageSeenHandler(instagram_data, user_page_data, redis_client, db)
        case WebhookType.COMMENT:
            handler = CommentHandler(instagram_data, user_page_data, redis_client, db)
        case WebhookType.LIVE_COMMENT:
            handler = LiveCommentHandler(instagram_data, user_page_data, redis_client, db)

        case WebhookType.DELETE_MESSAGE:
            handler = DeleteMessageHandler(instagram_data, user_page_data, redis_client, db)

        case WebhookType.STORY_MENTION:
            handler = StoryMentionHandler(instagram_data, user_page_data, redis_client, db)

        case WebhookType.STORY_REPLY:
            handler = StoryReplyHandler(instagram_data, user_page_data, redis_client, db)

        case WebhookType.CONTACT_MESSAGE:
            handler = ContactMessageHandler(instagram_data, user_page_data, redis_client, db)

    handler()

    db.close()
    return None


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
