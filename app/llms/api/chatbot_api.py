from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4

from app import models
from app.api import deps
from app.constants.role import Role
from app.llms.schemas.chatbot_schema import ChatBot, ChatBotCreate, ChatBotUpdate
from app.llms.services.chatbot_service import ChatBotService
from app.llms.services.chatbot_telegram_bot_service import ChatBotTelegramBotService
from app.llms.utils.dependencies import get_service
from app.schemas.telegram_bot import TelegramBotItem

router = APIRouter(
    prefix="/chatbot",
    tags=["ChatBot"],
)


@router.get('', response_model=List[ChatBot])
def get_chatbots(
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    return chatbot_service.get_list_by_user_id(user_id=current_user.id)


@router.get('/{id}', response_model=ChatBot)
def get_chatbot(
    id: UUID4,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    chatbot = chatbot_service.validator.validate_exists(uuid=id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)
    return chatbot_service.get_by_uuid(uuid=id)


@router.get('/{id}/telegram-bots', response_model=List[TelegramBotItem])
def get_chatbot_telegram_bots(
    id: UUID4,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    chatbot_telegram_bot_service: ChatBotTelegramBotService = Depends(
        get_service(ChatBotTelegramBotService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    chatbot = chatbot_service.validator.validate_exists(uuid=id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)

    chatbot_telegram_bots = chatbot_telegram_bot_service.get_multi_by_chatbot_id(chatbot.id)

    return [c.telegram_bot for c in chatbot_telegram_bots]


@router.post('', response_model=ChatBot)
def create_chatbot(
    obj_in: ChatBotCreate,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    obj_in.user_id = current_user.id
    return chatbot_service.add(schema=obj_in)


@router.put('/{id}', response_model=ChatBot)
def update_chatbot(
    id: UUID4,
    obj_in: ChatBotUpdate,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    chatbot = chatbot_service.validator.validate_exists(uuid=id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)
    obj_in.user_id = current_user.id
    return chatbot_service.update(chatbot, obj_in)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_chatbot(
    id: UUID4,
    chatbot_telegram_bot_service: ChatBotTelegramBotService = Depends(
        get_service(ChatBotTelegramBotService)),
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    chatbot = chatbot_service.validator.validate_exists(uuid=id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)
    if chatbot_telegram_bots := chatbot_telegram_bot_service.get_multi_by_chatbot_id(chatbot.id):
        for c in chatbot_telegram_bots:
            chatbot_telegram_bot_service.remove(c.id)

    return chatbot_service.remove(pk=chatbot.id)
