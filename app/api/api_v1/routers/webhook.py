# noqa

# from datetime import timedelta
from redis.client import Redis
from fastapi import APIRouter, HTTPException, Response, Request, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import services, models, schemas
from app.api import deps
from app.core import cache, tasks
from app.core.config import settings
from app.constants.message_direction import MessageDirection


from app.core.extra_classes import InstagramData


router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.get("/user")
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
    request: dict,
    background_tasks: BackgroundTasks
):
    facebook_webhook_body = request['entry']
    instagram_data = InstagramData()
    instagram_data.parse(facebook_webhook_body)
    # try:
    user_page_data = cache.get_user_data(
            redis_client,
            db,
            instagram_page_id=instagram_data.id_recipient)
    # except:
        # raise HTTPException(status_code=400, detail="Error getting user data")

    message_in = schemas.MessageCreate(
        from_page_id=instagram_data.id_sender,
        to_page_id=user_page_data.facebook_page_id,
        content={
            "message": instagram_data.message_detail
        },
        user_id=user_page_data.user_id,
        direction=MessageDirection.IN["name"]
    )
    print("--------------------------------")
    print("--------------------------------")
    print(message_in)
    print("--------------------------------")
    background_tasks.add_task(tasks.save_message,
                              db,
                              redis_client,
                              obj_in=message_in,
                              instagram_page_id = instagram_data.id_recipient)
    if instagram_data.payload:

        node = services.node.get_next_node(db, from_id=instagram_data.payload)

        background_tasks.add_task(tasks.send_widget,
                                  db,
                                  redis_client,
                                  widget=node.widget,
                                  contact_igs_id=instagram_data.id_sender,
                                  payload=instagram_data.payload,
                                  user_page_data=user_page_data
                                  )

    else:
        # get chatflow from a connection

        chatflow_id = None
        trigger = services.trigger.get_by_name(db, name="MESSAGE")
        connections = services.connection.get_page_connection(
            db,
            account_id=user_page_data.account_id,
            application_name="BOT_BUILDER"
        )

        if connections is None:
            return None
        
        for connection in connections:
            connection_chatflow = services.connection_chatflow\
                .get_connection_chatflow_by_connection_and_trigger(
                    db, connection_id=connection.id, trigger_id=trigger.id)
            if connection_chatflow:
                chatflow_id = connection_chatflow.chatflow_id

        if chatflow_id is None:
            return None

        print(chatflow_id)
        node = services.node.get_chatflow_head_node(db , chatflow_id = chatflow_id)
        background_tasks.add_task(tasks.send_widget,
                                  db,
                                  redis_client,
                                  widget=node.widget,
                                  contact_igs_id=instagram_data.id_sender,
                                  payload=instagram_data.payload,
                                  user_page_data=user_page_data
                                  )
    return Response(status_code = 200)


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
