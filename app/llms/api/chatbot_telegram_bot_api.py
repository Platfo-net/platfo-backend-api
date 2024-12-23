from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception
from app.llms.schemas.chatbot_schema import ChatBot
from app.llms.schemas.chatbot_telegram_bot_schema import ChatbotConnectTelegramBotRequest
from app.llms.services.chatbot_service import ChatBotService
from app.llms.services.chatbot_telegram_bot_service import ChatBotTelegramBotService
from app.llms.utils.dependencies import get_service
from app.llms.utils.exceptions import BusinessLogicError, NotFoundError
from app.llms.utils.response import ok_response

router = APIRouter(
    prefix="/telegram-bot",
    tags=["ChatBot Telegram Bot"],
)


@router.get('/{telegram_bot_id}/chatbot', response_model=ChatBot)
def get_telegram_bot_chatbot(
    telegram_bot_id: UUID4,
    chatbot_telegram_bot_service: ChatBotTelegramBotService = Depends(
        get_service(ChatBotTelegramBotService)),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    telegram_bot = services.telegram_bot.get_by_uuid(db, uuid=telegram_bot_id)
    _validate_telegram_bot(telegram_bot, current_user)

    chatbot_telegram_bot = chatbot_telegram_bot_service.get_by_telegram_bot_id(telegram_bot.id)
    if chatbot_telegram_bot:
        return chatbot_telegram_bot.chatbot

    raise NotFoundError(detail="Chatbot not found")


@router.post('/{telegram_bot_id}/chatbot/{chatbot_id}/connect', status_code=status.HTTP_200_OK)
def add_chatbot_to_telegram_bot_connection(
    telegram_bot_id: UUID4,
    chatbot_id: UUID4,
    chatbot_telegram_bot_service: ChatBotTelegramBotService = Depends(
        get_service(ChatBotTelegramBotService)),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    telegram_bot = services.telegram_bot.get_by_uuid(db, uuid=telegram_bot_id)
    _validate_telegram_bot(telegram_bot, current_user)

    chatbot_telegram_bot = chatbot_telegram_bot_service.get_by_telegram_bot_id(telegram_bot.id)
    if chatbot_telegram_bot:
        raise BusinessLogicError(detail="You already have a chatbot connected to this bot.")

    chatbot_telegram_bot_service.create(
        ChatbotConnectTelegramBotRequest(chatbot_id=chatbot_id), telegram_bot, current_user)
    return ok_response()


@router.delete('/{telegram_bot_id}/chatbot/{chatbot_id}/disconnect',
               status_code=status.HTTP_204_NO_CONTENT)
def delete_telegram_bot_chatbot(
    telegram_bot_id: UUID4,
    chatbot_id: UUID4,
    chatbot_telegram_bot_service: ChatBotTelegramBotService = Depends(
        get_service(ChatBotTelegramBotService)),
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    telegram_bot = services.telegram_bot.get_by_uuid(db, uuid=telegram_bot_id)
    _validate_telegram_bot(telegram_bot, current_user)

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)

    chatbot_telegram_bot = chatbot_telegram_bot_service.get_by_telegram_bot_id_and_chatbot_id(
        telegram_bot.id, chatbot.id)

    if chatbot_telegram_bot:
        return chatbot_telegram_bot_service.remove(chatbot_telegram_bot.id)

    raise NotFoundError(detail="ChatBot TelegramBot not found")


def _validate_telegram_bot(telegram_bot, current_user):
    if not telegram_bot:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUND)
    if not telegram_bot.user_id == current_user.id:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUND_ACCESS_DENIED)
