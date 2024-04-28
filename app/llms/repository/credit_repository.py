from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from app.llms.models.credit import ChatbotPlan, ChatbotPlanFeature, ChatbotTransaction, \
    PurchasedChatbotPlan
from app.llms.repository.base_repository import CRUDBRepository


class ChatbotPlanRepository(CRUDBRepository):
    model = ChatbotPlan

    def get_by_uuid(self, uuid):
        return self.session.query(self.model).options(
            joinedload(self.model.features),
        ).filter(self.model.uuid == uuid).first()

    def get_multi(self):
        return self.session.query(self.model).options(
            joinedload(self.model.features),
        ).all()


class ChatbotPlanFeatureRepository(CRUDBRepository):
    model = ChatbotPlanFeature


class PurchasedChatbotPlanRepository(CRUDBRepository):
    model = PurchasedChatbotPlan

    def get_filtered_by_chatbot_id(self, chatbot_id: int, now: datetime):
        return self.session.query(self.model).filter(
            self.model.chatbot_id == chatbot_id,
            self.model.from_datetime <= now,
            self.model.to_datetime >= now,
        ).order_by(self.model.to_datetime).all()

    def get_all_by_chatbot_id(self, chatbot_id):
        self.session.query(self.model).filter(
            self.model.chatbot_id == chatbot_id,
        ).order_by(self.model.to_datetime).all()


class ChatbotTransactionRepository(CRUDBRepository):
    model = ChatbotTransaction

    def get_list_by_chatbot_id(self, chatbot_id):
        return self.session.query(self.model).filter(self.model.chatbot_id == chatbot_id).order_by(
            desc(self.model.created_at)).all()
