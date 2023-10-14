import telegram
from fastapi import (APIRouter, Depends, HTTPException, Request, Security,
                     status)
from sqlalchemy.orm import Session

from app import models, services
from app.api import deps
from app.api.api_v1.routers.telegram_bot import set_webhook
from app.constants.role import Role
from app.core import support_bot
from app.core.config import settings
from app.core.instagram import tasks
from app.core.telegram import tasks as telegram_tasks

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
    tasks.webhook_processor.delay(facebook_webhook_body)
    return


@router.post('/telegram/bot/{bot_id}', status_code=status.HTTP_200_OK)
async def telegram_webhook_listener(*, bot_id: int, request: Request):
    try:
        data = await request.json()
        print(data)
        d = telegram.Message.de_json(data)
        print(d)
        # telegram_tasks.telegram_webhook_task.delay(data, bot_id, "fa")
    except Exception as e:
        print(e)
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


@router.post('/telegram/telegram-bot/set-webhook', status_code=status.HTTP_200_OK)
async def telegram_bot_set_webhook(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_user,
        scopes=[
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    )
):
    bots = services.telegram_bot.all(db)
    for bot in bots:
        await set_webhook(bot.bot_token, bot.bot_id)


@router.post('/telegram/support-bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_support_listener(request: Request):
    data = await request.json()
    telegram_tasks.telegram_support_bot_task.delay(data, "fa")
    return
