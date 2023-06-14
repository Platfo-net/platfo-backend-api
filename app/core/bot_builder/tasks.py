
from sqlalchemy.orm import Session

from app.api import deps
from app.constants.application import Application
from app.constants.trigger import Trigger
from app.constants.webhook_type import WebhookType
from app.core import cache
from app.core.bot_builder.extra_classes import InstagramData
from app.core.bot_builder.handlers import (CommentHandler,
                                           ContactMessageBotHandler,
                                           ContactMessageHandler,
                                           DeleteMessageHandler,
                                           LiveCommentHandler,
                                           MessageSeenHandler,
                                           StoryMentionHandler,
                                           StoryReplyBotHandler,
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
            handler()

        case WebhookType.COMMENT:
            handler = CommentHandler(instagram_data, user_page_data, redis_client, db)
            handler()

        case WebhookType.LIVE_COMMENT:
            handler = LiveCommentHandler(instagram_data, user_page_data, redis_client, db)
            handler()

        case WebhookType.DELETE_MESSAGE:
            handler = DeleteMessageHandler(instagram_data, user_page_data, redis_client, db)
            handler()

        case WebhookType.STORY_MENTION:
            handler = StoryMentionHandler(instagram_data, user_page_data, redis_client, db)
            handler()

        case WebhookType.STORY_REPLY:
            handler = StoryReplyHandler(instagram_data, user_page_data, redis_client, db)
            handler()

            bot = StoryReplyBotHandler(instagram_data, user_page_data, redis_client, db)
            bot.run(Trigger.STORY_REPLY, Application.BOT_BUILDER)

        case WebhookType.CONTACT_MESSAGE:
            handler = ContactMessageHandler(instagram_data, user_page_data, redis_client, db)
            handler()

            bot = ContactMessageBotHandler(instagram_data, user_page_data, redis_client, db)
            bot.run(Trigger.MESSAGE, Application.BOT_BUILDER)
    db.close()
    return None


#
# @celery.task
