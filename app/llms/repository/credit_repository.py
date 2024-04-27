from datetime import datetime

from sqlalchemy.orm import joinedload

from app.llms.models.credit import ChatbotPlan, ChatbotPlanFeature, PurchasedChatbotPlan
from app.llms.repository.base_repository import CRUDBRepository


class ChatbotPlanRepository(CRUDBRepository):
    model = ChatbotPlan

    def get_by_uuid(self, uuid):
        return self.session.query(self.model).options(
            joinedload(self.model.features),
        ).filter(self.model.uuid == uuid).first()


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
