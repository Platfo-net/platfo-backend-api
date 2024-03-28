from app.llms.repository.chatbot_repository import ChatBotRepository
from app.llms.services.base_service import BaseService


class ChatBotService(BaseService):

    def __init__(self, chatbot_repo: ChatBotRepository):
        self.chatbot_repo = chatbot_repo
        super().__init__(chatbot_repo)
