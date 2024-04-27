from sqlalchemy.orm import Session

from app.llms.repository.credit_repository import PurchasedChatbotPlanRepository
from app.llms.services.credit_service import PurchasedChatbotPlanService


def chatbot_has_chat_credit(db: Session, chatbot_id: int, has_cost=False):
    credit_service = PurchasedChatbotPlanService(PurchasedChatbotPlanRepository(db))

    valid_credits = credit_service.get_valid_chat_credits(chatbot_id)

    if not valid_credits:
        return False

    has_main_credit = False

    for credit in valid_credits:
        if not credit.is_extra:
            has_main_credit = True

    if not has_main_credit:
        return False

    credit_for_decrease = None
    for credit in valid_credits:
        if credit.remaining_chat_count:
            credit_for_decrease = credit

    if not credit_for_decrease:
        return False

    if not has_cost:
        return True

    credit_service.decrease_from_chat_remaining(credit_for_decrease)

    return True
