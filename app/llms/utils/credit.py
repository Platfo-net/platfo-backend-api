from sqlalchemy.orm import Session

from app.llms.repository.credit_repository import PurchasedChatBotPlanRepository
from app.llms.services.credit_service import PurchasedChatbotPlanService


def chatbot_has_chat_credit(db: Session, chatbot_id: int, has_cost=False):
    purchased_chatbot_plan_service = PurchasedChatbotPlanService(
        PurchasedChatBotPlanRepository(db))
    valid_credits = purchased_chatbot_plan_service.get_valid_chat_credits(chatbot_id)

    if not valid_credits or not any(not credit.is_extra for credit in valid_credits):
        return False

    credit_for_decrease = None
    for credit in valid_credits:
        if credit.remaining_chat_count:
            credit_for_decrease = credit

    if not credit_for_decrease:
        return False

    if has_cost:
        purchased_chatbot_plan_service.decrease_chat_cost(credit_for_decrease)

    return True


def chatbot_has_token_credit(db: Session, chatbot_id: int, token_count: int, has_cost=False):
    purchased_chatbot_plan_service = PurchasedChatbotPlanService(
        PurchasedChatBotPlanRepository(db))
    valid_credits = purchased_chatbot_plan_service.get_valid_chat_credits(chatbot_id)

    if not valid_credits or not any(not credit.is_extra for credit in valid_credits):
        return False

    sum_of_token_credit_counts = sum(credit.remaining_token_count for credit in valid_credits)

    if sum_of_token_credit_counts < token_count:
        return False

    if not has_cost:
        return True

    for credit in valid_credits:
        if credit.remaining_token_count >= token_count:
            purchased_chatbot_plan_service.decrease_token_cost(credit, token_count)
            break
        token_count -= credit.remaining_token_count
        purchased_chatbot_plan_service.decrease_token_cost(credit, credit.remaining_token_count)

    return True
