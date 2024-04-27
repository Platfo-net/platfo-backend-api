from datetime import datetime

from app.llms.models.credit import PurchasedChatbotPlan
from app.llms.repository.credit_repository import ChatbotPlanFeatureRepository, \
    ChatbotPlanRepository, PurchasedChatbotPlanRepository
from app.llms.services.base_service import BaseService


class ChatbotPlanService(BaseService):

    def __init__(self, repo: ChatbotPlanRepository):
        self.repo = repo
        super().__init__(repo)


class ChatbotPlanFeatureService(BaseService):

    def __init__(self, repo: ChatbotPlanFeatureRepository):
        self.repo = repo
        super().__init__(repo)


class PurchasedChatbotPlanService(BaseService):

    def __init__(self, repo: PurchasedChatbotPlanRepository):
        self.repo = repo
        super().__init__(repo)

    def get_valid_chat_credits(self, chatbot_id):
        now = datetime.now()
        return self.repo.get_filtered_by_chatbot_id(chatbot_id, now)

    def decrease_from_remaining_cost(self, db_obj: PurchasedChatbotPlan, count: int = 1):
        self.repo.update(db_obj, {"remaining_chat_count": db_obj.remaining_chat_count - count})
