from datetime import datetime

from app.llms.models.credit import PurchasedChatBotPlan
from app.llms.repository.credit_repository import ChatBotPlanFeatureRepository, \
    ChatBotPlanRepository, ChatBotTransactionRepository, PurchasedChatBotPlanRepository
from app.llms.services.base_service import BaseService


class ChatBotPlanService(BaseService):

    def __init__(self, chatbot_plan_repo: ChatBotPlanRepository):
        self.chatbot_plan_repo = chatbot_plan_repo
        super().__init__(chatbot_plan_repo)

    def get_by_uuid_with_features(self, uuid):
        return self.chatbot_plan_repo.get_by_uuid_with_features(uuid)

    def get_multi_with_features(self):
        return self.chatbot_plan_repo.get_multi_with_features()


class ChatBotPlanFeatureService(BaseService):

    def __init__(self, chatbot_plan_feature_repo: ChatBotPlanFeatureRepository):
        self.chatbot_plan_feature_repo = chatbot_plan_feature_repo
        super().__init__(chatbot_plan_feature_repo)


class PurchasedChatbotPlanService(BaseService):

    def __init__(self, purchased_chatbot_plan_repo: PurchasedChatBotPlanRepository):
        self.purchased_chatbot_plan_repo = purchased_chatbot_plan_repo
        super().__init__(purchased_chatbot_plan_repo)

    def get_valid_chat_credits(self, chatbot_id):
        now = datetime.now()
        return self.purchased_chatbot_plan_repo.get_filtered_by_chatbot_id(chatbot_id, now)

    def get_all_by_chatbot_id(self, chatbot_id):
        return self.purchased_chatbot_plan_repo.get_all_by_chatbot_id(chatbot_id)

    def decrease_chat_cost(self, db_obj: PurchasedChatBotPlan, count: int = 1):
        self.purchased_chatbot_plan_repo.update(
            db_obj, {"remaining_chat_count": db_obj.remaining_chat_count - count})

    def decrease_token_cost(self, db_obj: PurchasedChatBotPlan, count):
        self.purchased_chatbot_plan_repo.update(
            db_obj, {"remaining_token_count": db_obj.remaining_token_count - count})


class ChatBotTransactionService(BaseService):

    def __init__(self, chatbot_transaction_repo: ChatBotTransactionRepository):
        self.chatbot_transaction_repo = chatbot_transaction_repo
        super().__init__(chatbot_transaction_repo)

    def get_all_by_chatbot_id(self, chatbot_id):
        return self.chatbot_transaction_repo.get_all_by_chatbot_id(chatbot_id)
