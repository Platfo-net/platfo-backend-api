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
def telegram_webhook_listener(*, request: Request):
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
    return await support_bot.set_support_bot_webhook()


@router.post('/telegram/support-bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_support_listener(
    *,
    db: Session = Depends(deps.get_db),
        request: Request):
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    data = await request.json()
    update: telegram.Update = telegram.Update.de_json(data, bot=bot)
    if update.message.text == "/start":
        await update.message.reply_text("Enter your code")
    else:
        code = update.message.text.lstrip().rstrip()
        if len(code) != 8:
            await update.message.reply_text(f"Wrong code.")
            return
        shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
            db, support_token=code)
        if not shop_telegram_bot:
            await update.message.reply_text(f"Wrong code.")
            return
        if shop_telegram_bot.is_support_verified:
            await update.message.reply_text(f"Your shop is already connected to an account.")
            return

        await update.message.reply_text(
            f"You are trying to connect your accoutn to {shop_telegram_bot.shop.title} shop,"    
            f"Enter this code in app: {shop_telegram_bot.support_bot_token}" \
            )
        services.shop.shop_telegram_bot.set_support_account_chat_id(
            db, db_obj=shop_telegram_bot, chat_id=update.message.chat_id)
