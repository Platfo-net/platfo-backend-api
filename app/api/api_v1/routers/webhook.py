import asyncio
from fastapi import APIRouter, HTTPException, Request, Security, status , Depends
from app import models , services
from app.api import deps
from app.constants.role import Role
from app.core import support_bot
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.instagram import tasks
import telegram
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
def telegram_set_webhook(
    *,
    current_user: models.User = Security(
        deps.get_current_user,
        scopes=[
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    )
):
    return asyncio.run(support_bot.set_support_bot_webhook())

@router.post('/telegram/support-bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_support_listener(
    *, 
    db: Session = Depends(deps.get_db),
    request: Request):
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    data = await request.json()
    update:telegram.Update = telegram.Update.de_json(data , bot = bot)
    
    if update.message.text == "/start":
        await update.message.reply_text("Enter your code")
    else:
        code = update.message.text
        shop = services.shop.shop.get_by_support_token(db , support_token=code.replace(" " , ""))
        if not shop :
            await update.message.reply_text(f"Wrong code.")
        
        await update.message.reply_text(f"Enter this code in app: {shop.support_bot_token}")
        services.shop.shop.set_support_account_chat_id(db , db_obj=shop , chat_id=update.message.chat_id)
        print(update.message.chat_id)
            