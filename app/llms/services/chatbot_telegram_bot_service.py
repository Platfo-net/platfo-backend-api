from app.llms.models import ChatBot
from app.llms.repository.chatbot_telegram_bot_repository import ChatBotTelegramBotRepository
from app.llms.schemas.chatbot_telegram_bot_schema import ChatbotConnectTelegramBot
from app.llms.services.base_service import BaseService


class ChatBotTelegramBotService(BaseService):

    def __init__(self, chatbot_telegram_bot_repo: ChatBotTelegramBotRepository):
        self.chatbot_telegram_bot_repo = chatbot_telegram_bot_repo
        super().__init__(chatbot_telegram_bot_repo)

    def get_multi_by_chatbot_id(self, chatbot_id):
        return self.chatbot_telegram_bot_repo.get_multi_by_chatbot_id(chatbot_id)

    def get_by_telegram_bot_id(self, telegram_bot_id):
        return self.chatbot_telegram_bot_repo.get_telegram_bot_id(telegram_bot_id)

    def create(self, schema, telegram_bot, current_user):
        chatbot = self.validator.validate_generic_exists(uuid=schema.chatbot_id, model=ChatBot)
        self.validator.validate_user_ownership(obj=chatbot, current_user=current_user)

        new_schema = ChatbotConnectTelegramBot(chatbot_id=chatbot.id,
                                               telegram_bot_id=telegram_bot.id)

        new_chatbot_telegram_bot = self.chatbot_telegram_bot_repo.create(new_schema)

        return new_chatbot_telegram_bot
