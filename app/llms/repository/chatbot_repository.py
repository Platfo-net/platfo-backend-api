from app.llms.models.chatbot import ChatBot
from app.llms.repository.base_repository import CRUDBRepository


class ChatBotRepository(CRUDBRepository):
    model = ChatBot

    def get_multi_by_user_id(self, user_id, skip=0, limit=100):
        return self.session.query(self.model).\
            filter(self.model.user_id == user_id).offset(skip).limit(limit).all()