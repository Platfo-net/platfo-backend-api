from fastapi import APIRouter, HTTPException, Response, Request, status
from app.core.bot_builder import tasks
from app.core.config import settings


router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/instagram", status_code=status.HTTP_200_OK)
def instagram_webhook_listener(
    *,
    facebook_webhook_body: dict,
):

    tasks.webhook_proccessor.delay(facebook_webhook_body)
    return
