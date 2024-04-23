from app.llms.models import ChatBotTelegramBot
from app.llms.repository.base_repository import CRUDBRepository


class ChatBotTelegramBotRepository(CRUDBRepository):
    model = ChatBotTelegramBot

    def get_by_chatbot_id(self, chatbot_id):
        return self.session.query(self.model). \
            filter(self.model.chatbot_id == chatbot_id).all()

    def get_telegram_bot_id(self, telegram_bot_id):
        return self.session.query(self.model). \
            filter(self.model.telegram_bot_id == telegram_bot_id).first()

    def create(self, chatbot_id, telegram_bot_id):
        obj_in = self.model(chatbot_id=chatbot_id, telegram_bot_id=telegram_bot_id)
        return super().create(obj_in)
