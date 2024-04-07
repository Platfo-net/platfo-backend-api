import ipaddress

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
from app.core.telegram import tasks as telegram_tasks
from app.core.telegram.handlers import telegram_message_builder_bot_handler
from app.llms.utils.langchain.pipeline import get_question_and_answer

router = APIRouter(prefix='/webhook', tags=['Webhook'],
                   include_in_schema=True if settings.ENVIRONMENT == "dev" else False)


@router.get('/instagram', include_in_schema=False)
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


@router.post('/instagram', status_code=status.HTTP_200_OK, include_in_schema=False)
def instagram_webhook_listener(*, facebook_webhook_body: dict):
    # tasks.webhook_processor.delay(facebook_webhook_body)
    return


@router.post('/telegram/bot/{bot_id}', status_code=status.HTTP_200_OK)
async def telegram_webhook_listener(*, bot_id: int, request: Request):
    try:
        if settings.ENVIRONMENT == "prod":

            real_ip = request.headers.get("x-real-ip")
        # forward_for = request.headers.get("x-forwarded-for")
            if not (
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('91.108.4.0/22')
                or
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('149.154.160.0/20')
            ):
                return

        data = await request.json()
        telegram_tasks.telegram_webhook_task.delay(data, bot_id, "fa")
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
    try:
        if settings.ENVIRONMENT == "prod":
            real_ip = request.headers.get("x-real-ip")
            # forward_for = request.headers.get("x-forwarded-for")
            if not (
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('91.108.4.0/22')
                or
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('149.154.160.0/20')
            ):
                return
        data = await request.json()
        telegram_tasks.telegram_support_bot_task.delay(data, "fa")
        return
    except Exception as e:
        print(e)
    return


@router.post('/telegram/admin-bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_admin_listener(request: Request):
    try:
        if settings.ENVIRONMENT == "prod":

            real_ip = request.headers.get("x-real-ip")
        # forward_for = request.headers.get("x-forwarded-for")
            if not (
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('91.108.4.0/22')
                or
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('149.154.160.0/20')
            ):
                return
        data = await request.json()
        telegram_tasks.telegram_admin_bot_task.delay(data, "fa")
        return
    except Exception as e:
        print(e)
    return


@router.post('/telegram/chat-bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_chatbot_listener(request: Request):
    try:
        data = await request.json()
        bot = telegram.Bot(settings.CHAT_BOT_TOKEN)
        update = telegram.Update.de_json(bot=bot, data=data)
        answer = get_question_and_answer(update.message.text)
        await update.message.reply_text(text=answer)

        return
    except Exception as e:
        print(e)
    return


from app.db.session import SessionLocal


@router.post('/telegram/message-builder-bot', status_code=status.HTTP_200_OK)
async def telegram_webhook_message_builder_bot_listener(request: Request):
    try:
        if settings.ENVIRONMENT == "prod":

            real_ip = request.headers.get("x-real-ip")
            if not (
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('91.108.4.0/22')
                or
                ipaddress.ip_address(real_ip) in ipaddress.ip_network('149.154.160.0/20')
            ):
                return
        data = await request.json()
        # telegram_tasks.telegram_message_builder_bot_task.delay(data, "fa")
        # return
        db = SessionLocal()
        await telegram_message_builder_bot_handler(db ,data , "fa" )
        db.close()
    except Exception as e:
        print(e)
    return




@router.post('/telegram/message-builder-bot/set-webhook', status_code=status.HTTP_200_OK)
async def telegram_webhook_message_builder_bot_set_webhook(request: Request):
    bot = telegram.Bot(token=settings.MESSAGE_BUILDER_BOT_TOKEN)

    await bot.set_webhook(
        f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/webhook/telegram/message-builder-bot"
    )