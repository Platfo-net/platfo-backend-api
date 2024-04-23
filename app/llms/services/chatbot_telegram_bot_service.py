from app.llms.repository.chatbot_telegram_bot_repository import ChatBotTelegramBotRepository
from app.llms.services.base_service import BaseService


class ChatBotTelegramBotService(BaseService):

    def __init__(self, chatbot_telegram_bot_repo: ChatBotTelegramBotRepository):
        self.chatbot_telegram_bot_repo = chatbot_telegram_bot_repo
        super().__init__(chatbot_telegram_bot_repo)

    def get_by_chatbot_id(self, chatbot_id):
        return self.chatbot_telegram_bot_repo.get_by_chatbot_id(chatbot_id)

    def get_by_telegram_bot_id(self, telegram_bot_id):
        return self.chatbot_telegram_bot_repo.get_telegram_bot_id(telegram_bot_id)

    def create(self, chatbot_id, telegram_bot_id):
        return self.chatbot_telegram_bot_repo.create(chatbot_id, telegram_bot_id)
