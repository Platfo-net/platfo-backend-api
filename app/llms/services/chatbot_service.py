from app.llms.repository.chatbot_repository import ChatBotRepository
from app.llms.services.base_service import BaseService


class ChatBotService(BaseService):

    def __init__(self, chatbot_repo: ChatBotRepository):
        self.chatbot_repo = chatbot_repo
        super().__init__(chatbot_repo)

    def get_list_by_user_id(self, user_id):
        return self.chatbot_repo.get_multi_by_user_id(user_id=user_id)
