from app.constants.currency import Currency
from app.core.config import settings
from app.llms.repository.credit_repository import ChatBotTransactionRepository, \
    UserChatBotCreditRepository
from app.llms.schemas.credit_schema import ChatBotCreditCreate
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

    def get_or_create_by_user_id(self, user_id):
        db_obj = self.chatbot_credit_repo.get_by_user_id(user_id)
        if not db_obj:
            db_obj = self.add(
                ChatBotCreditCreate(amount=settings.INITIAL_CHATBOT_CREDIT_AMOUNT,
                                    currency=Currency.IRT["value"], user_id=user_id))
        return db_obj

    def add_credit(self, user_id, amount):
        credit = self.get_or_create_by_user_id(user_id)
        return self.update(credit, {"amount": credit.amount + amount})

    def decrease_credit(self, db_obj, amount):
        return self.chatbot_credit_repo.decrease_amount(db_obj, amount)
