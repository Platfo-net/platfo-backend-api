from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4

from app import models
from app.api import deps
from app.constants.role import Role
from app.llms.schemas.chatbot_schema import ChatBot, ChatBotCreate, ChatBotUpdate
from app.llms.services.chatbot_service import ChatBotService
from app.llms.utils.dependencies import get_service

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
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    chatbot = chatbot_service.validator.validate_exists(uuid=id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)
    return chatbot_service.remove(pk=chatbot.id)
