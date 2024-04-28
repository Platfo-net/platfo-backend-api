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

    credit_service.decrease_chat_cost(credit_for_decrease)

    return True


def chatbot_has_token_credit(db: Session, chatbot_id: int, token_count: int, has_cost=False):
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

    sum_of_token_credit_counts = 0

    for credit in valid_credits:
        sum_of_token_credit_counts += credit.remaining_token_count

    if sum_of_token_credit_counts < token_count:
        return False

    if not has_cost:
        return True

    for credit in valid_credits:
        if credit.remaining_token_count > token_count:
            credit_service.decrease_token_cost(credit, token_count)
            break
        token_count -= credit.remaining_token_count
        credit_service.decrease_token_cost(credit, credit.remaining_token_count)

    return True
