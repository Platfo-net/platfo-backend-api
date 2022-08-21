# noqa

# from datetime import timedelta
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import services, models
from app.api import deps
from app.core.tasks import send_message_to_contact_management,\
    send_widget, send_menu,\
    send_text_message, send_batch_text_message
from app.core.cache import commence_redis
from app.core.config import settings
from app.db.session import engine

router = APIRouter(prefix="/webhook", tags=["Webhook"])


class InstagramData:
    def __init__(self,
                 id_sender: str = None,
                 id_recipient: str = None,
                 message_detail: str = None,
                 message_id: str = None,
                 postback: dict = {},
                 payload: dict = {}):

        self.id_sender = id_sender
        self.id_recipient = id_recipient
        self.message_detail = message_detail
        self.message_id = message_id
        self.postback = postback
        self.payload = payload

    def parse(self, body):
        for element in body:
            messaging_list = element['messaging']
            for item in messaging_list:
                self.id_sender = item['sender']['id']
                self.id_recipient = item['recipient']['id']
                try:
                    if item['message']:
                        self.message_id = item['message']['mid']
                        try:
                            self.message_detail = item['message']['text']
                        except Exception:
                            pass
                except Exception:
                    self.message_detail = item['postback']["title"]
                    # print(self.postback)
                    self.payload = item['postback']['payload']


@router.get("/user-subs")
async def user_subscription_webhook(request: Request):
    try:
        _ = request.query_params["hub.mode"]
        challenge = request.query_params["hub.challenge"]
        token = request.query_params["hub.verify_token"]
        if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            raise HTTPException(status_code=400, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")

    return int(challenge)


@router.post("/user-subs")
async def user_listener_webhook(request: Request):
    return Response(status_code=200)


@router.get("/instagram")
async def instagram_subscription_webhook(request: Request):
    try:
        _ = request.query_params["hub.mode"]
        challenge = request.query_params["hub.challenge"]
        token = request.query_params["hub.verify_token"]
        if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            raise HTTPException(status_code=400, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")

    return int(challenge)

session = Session(bind=engine)


@router.post("/instagram")
async def instagram_listener_webhook(request: dict):
    facebook_webhook_body = request['entry']
    print(facebook_webhook_body)
    instagram_data = InstagramData()
    instagram_data.parse(facebook_webhook_body)
    try:
        user_page_data = commence_redis(
            id_recipient=instagram_data.id_recipient)
    except:
        return Response({"error": "Request failed"}, status_code=400)

    # send_message_to_contact_management.delay(
    #     from_page_id=instagram_data.id_sender,
    #     to_page_id=user_page_data["facebook_page_id"],
    #     content={
    #         "message": instagram_data.message_detail
    #     },
    #     user_id=user_page_data["user_id"],
    #     direction="IN"
    # )
    #
    # if instagram_data.payload:
    #     url = "{}/chatflow-services/api/v1/node/{}/next".format(
    #         settings.CHATFLOW_MANAGEMENT_BASE_URL,
    #         instagram_data.payload
    #     )
    #
    #     # get next node
    #     res = requests.get(url=url)
    #
    #     widget = res.json()
    #
    #     send_widget.delay(
    #         widget,
    #         instagram_data.id_sender,
    #         instagram_data.payload,
    #         user_page_data
    #     )
    #
    # else:
    #     # get chatflow from a connection
    #     url = "{}/user-services/api/v1/connection/related_chatflow/{}/{}/{}".format(
    #         settings.USER_MANAGEMENT_BASE_URL,
    #         "BOT_BUILDER",
    #         user_page_data["account_id"],
    #         "MESSAGE"
    #     )
    #     # get chatflow_id
    #     res = requests.get(url)
    #     if res.status_code != 200:
    #         return Response()
    #
    #     chatflow_id = res.json()["chatflow_id"]
    #
    #     res = requests.get("{}/chatflow-services/api/v1/node/{}/head".format(
    #         settings.CHATFLOW_MANAGEMENT_BASE_URL,
    #         chatflow_id
    #     ))
    #
    #     widget = res.json()
    #     send_widget.delay(
    #         widget,
    #         instagram_data.id_sender,
    #         instagram_data.payload,
    #         user_page_data
    #     )
    #
    return Response()


@router.get("/page-subs")
async def page_subscription(request: Request):
    try:
        _ = request.query_params["hub.mode"]
        challenge = request.query_params["hub.challenge"]
        token = request.query_params["hub.verify_token"]
        if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            raise HTTPException(status_code=400, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")

    return int(challenge)


@router.post("/page-subs")
async def page_subscription(request: Request):
    return Response(status_code=200)
