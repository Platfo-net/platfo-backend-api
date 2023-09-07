import telegram
from fastapi import (APIRouter, Depends, HTTPException, Request, Security,
                     status)
from sqlalchemy.orm import Session

from app import models, services
from app.api import deps
from app.constants.role import Role
from app.core import support_bot
from app.core.config import settings
from app.core.instagram import tasks
from app.core.telegram.tasks import telegram_support_bot_task

router = APIRouter(prefix='/webhook', tags=['Webhook'],
                   include_in_schema=True if settings.ENVIRONMENT == "dev" else False)


@router.get('/instagram')
def instagram_subscription_webhook(request: Request):
    try:
        _ = request.query_params['hub.mode']
        challenge = request.query_params['hub.challenge']
        token = request.query_params['hub.verify_token']
        if token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
            raise HTTPException(status_code=400, detail='Invalid token')

    except Exception:
        raise HTTPException(status_code=400, detail='Invalid request')

    return int(challenge)


@router.post('/instagram', status_code=status.HTTP_200_OK)
def instagram_webhook_listener(*, facebook_webhook_body: dict):
    tasks.webhook_proccessor.delay(facebook_webhook_body)
    return


@router.post('/telegram/bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_listener(*, request: Request):
    print(await request.json())
    return


@router.post('/telegram/support-bot/set-webhook', status_code=status.HTTP_200_OK)
async def telegram_set_webhook(
    *,
    current_user: models.User = Security(
        deps.get_current_user,
        scopes=[
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    )
):
    try:
        return await support_bot.set_support_bot_webhook()
    except:
        return


@router.post('/telegram/support-bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_support_listener(request: Request):
    data = await request.json()
    telegram_support_bot_task.delay(data)
    return
