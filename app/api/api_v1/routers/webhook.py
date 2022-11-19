from fastapi import APIRouter, HTTPException, Request, status
from app.core.bot_builder import tasks
from app.core.config import settings


router = APIRouter(prefix="/webhook", tags=["Webhook"] , include_in_schema=False)


# @router.get("/d2774e8d-a1df-4f86-bb13-ad223537c64f")
# def instagram_subscription_webhook(request: Request):
#     try:
#         _ = request.query_params["hub.mode"]
#         challenge = request.query_params["hub.challenge"]
#         token = request.query_params["hub.verify_token"]
#         if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
#             raise HTTPException(status_code=400, detail="Invalid token")

#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid request")

#     return int(challenge)


# @router.post("/d2774e8d-a1df-4f86-bb13-ad223537c64f", status_code=status.HTTP_200_OK)
# async def instagram_webhook_listener(
#     *,
#     facebook_webhook_body: dict
# ):
#     print('wwwwwwwwwwwwwwww', facebook_webhook_body)
#     tasks.webhook_proccessor.delay(facebook_webhook_body)
#     return
