from sqlalchemy import desc

from app.llms.models.credit import ChatBotTransaction, UserChatBotCredit
from app.llms.repository.base_repository import CRUDBRepository


class UserChatBotCreditRepository(CRUDBRepository):
    model = UserChatBotCredit

    def get_by_user_id(self, user_id):
        return self.session.query(self.model).filter(self.model.user_id == user_id).first()

    def decrease_amount(self, db_obj, amount):
        db_obj.amount = db_obj.amount - amount
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj


class ChatBotTransactionRepository(CRUDBRepository):
    model = ChatBotTransaction

    def get_all_by_user_id(self, user_id):
        return self.session.query(self.model).filter(self.model.user_id == user_id).order_by(
            desc(self.model.created_at)).all()
