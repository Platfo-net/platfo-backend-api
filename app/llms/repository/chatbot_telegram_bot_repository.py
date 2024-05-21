from sqlalchemy.orm import joinedload

from app.llms.models import ChatBotTelegramBot
from app.llms.repository.base_repository import CRUDBRepository


class ChatBotTelegramBotRepository(CRUDBRepository):
    model = ChatBotTelegramBot

    def get_multi_by_chatbot_id(self, chatbot_id):
        return (self.session.query(self.model).options(joinedload(
            self.model.telegram_bot)).filter(self.model.chatbot_id == chatbot_id).all())

    def get_telegram_bot_id(self, telegram_bot_id):
        return self.session.query(self.model). \
            filter(self.model.telegram_bot_id == telegram_bot_id).first()

    def get_by_telegram_bot_id_and_chatbot_id(self, telegram_bot_id, chatbot_id):
        return self.session.query(self.model). \
            filter(self.model.telegram_bot_id == telegram_bot_id,
                   self.model.chatbot_id == chatbot_id).first()
