
from sqlalchemy.orm import Session

from app.api import deps
from app.constants.webhook_type import WebhookType
from app.core import cache
from app.core.bot_builder.extra_classes import InstagramData
from app.core.bot_builder.handlers import (CommentHandler,
                                           ContactMessageHandler,
                                           DeleteMessageHandler,
                                           LiveCommentHandler,
                                           MessageSeenHandler,
                                           StoryMentionHandler,
                                           StoryReplyHandler)
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
