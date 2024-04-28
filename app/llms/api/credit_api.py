from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Security
from fastapi.responses import RedirectResponse
from pydantic import UUID4
from suds.client import Client

from app import models
from app.api import deps
from app.constants.role import Role
from app.core.config import settings
from app.llms.schemas.chatbot_schema import ChatBot
from app.llms.schemas.credit_schema import ChatbotCreditSchema, Plan, PurchasedPlanCreate, \
    Transaction, TransactionCreate
from app.llms.services.chatbot_service import ChatBotService
from app.llms.services.credit_service import ChatbotPlanService, ChatbotTransactionService, \
    PurchasedChatbotPlanService
from app.llms.utils.dependencies import get_service
from app.llms.utils.exceptions import BusinessLogicError

router = APIRouter(
    prefix="/chatbot-credit",
    tags=["Chatbot Credit"],
)


@router.get('/plans', response_model=List[Plan])
def get_plans(
    plan_service: ChatbotPlanService = Depends(get_service(ChatbotPlanService)),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    return plan_service.get_list()


@router.get('/{chatbot_id}/credits', response_model=List[ChatbotCreditSchema])
def get_chatbot_credits(
    chatbot_id: UUID4,
    is_valid: bool = False,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    purchased_plan_service: PurchasedChatbotPlanService = Depends(
        get_service(PurchasedChatbotPlanService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)

    if is_valid:
        return purchased_plan_service.get_valid_chat_credits(chatbot.id)
    return purchased_plan_service.get_all_by_chatbot_id(chatbot.id)


@router.get('/{chatbot_id}/transaction', response_model=List[Transaction])
def get_chatbot_transactions(
    chatbot_id: UUID4,
    is_valid: bool = False,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    transaction_service: ChatbotTransactionService = Depends(
        get_service(ChatbotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)

    return transaction_service.get_list(chatbot.id)


@router.get('/{chatbot_id}/plans/{plan_uuid}/buy', response_class=Transaction)
def buy_plan(
    chatbot_id: UUID4,
    plan_id: UUID4,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    plan_service: ChatbotPlanService = Depends(get_service(ChatbotPlanService)),
    transaction_service: ChatbotTransactionService = Depends(
        get_service(ChatbotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)\

    plan = plan_service.validator.validate_exists(uuid=plan_id, model=Plan)

    return transaction_service.add(
        TransactionCreate(chatbot_id=chatbot.id, price=plan.price, title=plan.title,
                          extend_chat_count=plan.extend_chat_count, extend_days=plan.extend_days,
                          extend_token_count=plan.extend_token_count, is_extra=plan.is_extra))


@router.get('/{chatbot_id}/transaction/{transaction_id}/pay')
def pay_plan(
    chatbot_id: UUID4,
    transaction_id: UUID4,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    transaction_service: ChatbotTransactionService = Depends(
        get_service(ChatbotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)\

    transaction = transaction_service.validator.validate_exists(uuid=transaction_id,
                                                                model=Transaction)

    if transaction.is_paid:
        raise BusinessLogicError(detail="Transaction has been already paid.")

    zarrin_client = Client(settings.ZARINPAL_WEBSERVICE)
    callback = f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/chatbot-credit/transaction/{transaction.uuid}/verify"  # noqa
    result = zarrin_client.service.PaymentRequest(
        settings.ZARINPAL_MERCHANT_ID,
        transaction.amount,
        "",
        "",
        "",
        callback,
    )

    transaction_service.update(transaction, {"payment_authority": result.Authority})

    return RedirectResponse(url=f"{settings.ZARINPAL_BASE_URL}/{result.Authority}")


@router.get('/transaction/{transaction_id}/verify')
def verify_payment(
    transaction_id: UUID4,
    transaction_service: ChatbotTransactionService = Depends(
        get_service(ChatbotTransactionService)),
    purchased_plan_service: PurchasedChatbotPlanService = Depends(
        get_service(ChatbotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    from app.llms.models.credit import ChatbotTransaction

    transaction: ChatbotTransaction = transaction_service.validator.validate_exists(
        uuid=transaction_id, model=Transaction)

    if transaction.is_paid:
        raise BusinessLogicError(detail="Transaction has been already paid.")

    zarrin_client = Client(settings.ZARINPAL_WEBSERVICE)
    result = zarrin_client.service.PaymentVerification(
        settings.ZARINPAL_MERCHANT_ID,
        transaction.payment_authority,
        transaction.amount,
    )

    if result.Status not in [100, 101]:
        raise BusinessLogicError("Invalid payment")

    if result.Status == 101:
        return
    now = datetime.utcnow()

    purchased_plan_service.add(
        PurchasedPlanCreate(
            chatbot_id=transaction.chatbot_id,
            from_datetime=now,
            to_datetime=now + timedelta(days=transaction.extend_days),
            is_extra=transaction.is_extra,
            remaining_chat_count=transaction.extend_chat_count,
            remaining_token_count=transaction.extend_token_count,
        ))
