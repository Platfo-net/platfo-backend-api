from app.llms.repository.credit_repository import ChatBotTransactionRepository, \
    UserChatBotCreditRepository
from app.llms.services.base_service import BaseService


class ChatBotTransactionService(BaseService):

    def __init__(self, chatbot_transaction_repo: ChatBotTransactionRepository):
        self.chatbot_transaction_repo = chatbot_transaction_repo
        super().__init__(chatbot_transaction_repo)

    def get_all_by_user_id(self, chatbot_id):
        return self.chatbot_transaction_repo.get_all_by_user_id(chatbot_id)


class UserChatBotCreditService(BaseService):

    def __init__(self, chatbot_credit_repo: UserChatBotCreditRepository):
        self.chatbot_credit_repo = chatbot_credit_repo
        super().__init__(chatbot_credit_repo)

    def get_by_user_id(self, user_id):
        return self.chatbot_credit_repo.get_by_user_id(user_id)

    def add_credit(self, user_id, amount):
        credit = self.get_by_user_id(user_id)
        return self.update(credit, {"amount": credit.amount + amount})
