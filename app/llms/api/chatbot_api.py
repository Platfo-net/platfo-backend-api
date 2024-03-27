from fastapi import Depends, Security, APIRouter

from app import models
from app.api import deps
from app.constants.role import Role
from app.llms.schemas.chatbot_schema import ChatBot, ChatBotCreate
from app.llms.services.chatbot_service import ChatBotService
from app.llms.utils.dependencies import get_service

router = APIRouter(
    prefix="/chatbot",
    tags=["ChatBot"],
)


@router.post('', response_model=ChatBot)
def create_chatbot(
        obj_in: ChatBotCreate,
        chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER['name'],
                Role.ADMIN['name'],
                Role.DEVELOPER['name'],
            ],
        ),
):
    obj_in.user_id = current_user.id
    return chatbot_service.add(obj_in)
