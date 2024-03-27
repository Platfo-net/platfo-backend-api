from app.llms.models.chatbot import ChatBot
from app.llms.repository.base_repository import CRUDBRepository


class ChatBotRepository(CRUDBRepository):
    model = ChatBot
