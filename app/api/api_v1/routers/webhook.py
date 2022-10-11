# noqa

# from datetime import timedelta
from uuid import uuid4
from redis.client import Redis
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from sqlalchemy.orm import Session

from app import services
from app.api import deps
from app.constants.webhook_type import WebhookType
from app.constants.widget_type import WidgetType
from app.core import cache, tasks
from app.core.config import settings
from app.constants.message_direction import MessageDirection


from app.core.extra_classes import InstagramData


router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.get("/user", )
def user_webhook_subscription(request: Request):
    try:
        _ = request.query_params["hub.mode"]
        challenge = request.query_params["hub.challenge"]
        token = request.query_params["hub.verify_token"]
        if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            raise HTTPException(status_code=400, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")

    return int(challenge)


@router.post("/user")
def user_webhook_listener(request: Request):
    return Response(status_code=200)


@router.get("/instagram")
def instagram_subscription_webhook(request: Request):
    try:
        _ = request.query_params["hub.mode"]
        challenge = request.query_params["hub.challenge"]
        token = request.query_params["hub.verify_token"]
        if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            raise HTTPException(status_code=400, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")

    return int(challenge)


@router.post("/instagram")
def webhook_instagram_listener(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client),
    facebook_webhook_body: dict,
):

    instagram_data = InstagramData()
    instagram_data.parse(facebook_webhook_body)
    print('------------------', instagram_data.sender_id)

    # try:
    user_page_data = cache.get_user_data(
        redis_client,
        db,
        instagram_page_id=instagram_data.recipient_id)
    print('uuuuuuuuuuuuuu', user_page_data)

    # except:
    #     pass
        # raise HTTPException(status_code=400, detail="Error getting user data")

    match instagram_data.type:
        case WebhookType.CONTACT_MESSAGE_ECHO:
            return None

        case WebhookType.DELETE_MESSAGE:
            return services.live_chat.message.remove_message_by_mid(db, mid=instagram_data.mid)

        case WebhookType.STORY_MENTION:
            saved_data = {
                "url": instagram_data.url,
                "widget_type": "STORY_MENTION",
                "id": str(uuid4())
            }

            tasks.save_message(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                mid=instagram_data.mid,
                content=saved_data,
                user_id=user_page_data.user_id,
                direction=MessageDirection.IN["name"],
                instagram_page_id=instagram_data.recipient_id
            )
            return None
        case WebhookType.STORY_REPLY:
            saved_data = {
                "url": instagram_data.story_url,
                "widget_type": "STORY_REPLY",
                "message": instagram_data.message_detail,
                "id": str(uuid4())
            }
            tasks.save_message(
                from_page_id=instagram_data.sender_id,
                to_page_id=user_page_data.facebook_page_id,
                mid=instagram_data.mid,
                content=saved_data,
                user_id=user_page_data.user_id,
                direction=MessageDirection.IN["name"],
                instagram_page_id=instagram_data.recipient_id
            )
            return

    saved_data = {
        "message": instagram_data.text,
        "widget_type": WidgetType.TEXT["name"],
        "id": str(uuid4())
    }

    tasks.save_message(
        from_page_id=instagram_data.sender_id,
        to_page_id=user_page_data.facebook_page_id,
        mid=instagram_data.mid,
        content=saved_data,
        user_id=user_page_data.user_id,
        direction=MessageDirection.IN["name"],
        instagram_page_id=instagram_data.recipient_id
    )
    if instagram_data.payload:
        node = services.bot_builder.node.get_next_node(
            db, from_id=instagram_data.payload)
        tasks.send_widget.delay(
            widget=node.widget,
            quick_replies=node.quick_replies,
            contact_igs_id=instagram_data.sender_id,
            payload=instagram_data.payload,
            user_page_data=user_page_data.to_dict()
        )

    else:
        # get chatflow from a connection
        chatflow_id = None
        connections = services.connection.get_page_connections(
            db,
            account_id=user_page_data.account_id,
            application_name="BOT_BUILDER"
        )

        if connections is None:
            return None
        from app.constants.trigger import Trigger
        for connection in connections:
            details = connection.details
            for detail in details:
                if detail["trigger"] == Trigger.Message["name"]:
                    chatflow_id = detail["chatflow_id"]

        if chatflow_id is None:
            return None

        try:
            node = services.bot_builder.node.get_chatflow_head_node(
                db, chatflow_id=chatflow_id)
            tasks.send_widget.delay(
                widget=node.widget,
                quick_replies=node.quick_replies,
                contact_igs_id=instagram_data.sender_id,
                payload=instagram_data.payload,
                user_page_data=user_page_data.to_dict()
            )
        except Exception as e:
            pass
    return Response(status_code=200)


@router.get("/page")
def page_subscription(request: Request):
    try:
        _ = request.query_params["hub.mode"]
        challenge = request.query_params["hub.challenge"]
        token = request.query_params["hub.verify_token"]
        if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            raise HTTPException(status_code=400, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")

    return int(challenge)


@router.post("/page")
def page_subscription(request: Request):
    return Response(status_code=200)
