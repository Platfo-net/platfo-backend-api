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
from app.llms.schemas.credit_schema import ChatBotCreditSchema, ChatBotPlan, ChatBotTransaction, \
    ChatBotTransactionCreate, PurchasedChatBotPlanCreate
from app.llms.services.chatbot_service import ChatBotService
from app.llms.services.credit_service import ChatBotPlanService, ChatBotTransactionService, \
    PurchasedChatbotPlanService
from app.llms.utils.dependencies import get_service
from app.llms.utils.exceptions import BusinessLogicError

router = APIRouter(
    prefix="/chatbot-credit",
    tags=["Chatbot Credit"],
)


@router.get('/plans', response_model=List[ChatBotPlan])
def get_plans(
    chatbot_plan_service: ChatBotPlanService = Depends(get_service(ChatBotPlanService)),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    return chatbot_plan_service.get_list()


@router.get('/{chatbot_id}/credits', response_model=List[ChatBotCreditSchema])
def get_chatbot_credits(
    chatbot_id: UUID4,
    is_valid: bool = False,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    purchased_chatbot_plan_service: PurchasedChatbotPlanService = Depends(
        get_service(PurchasedChatbotPlanService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)

    if is_valid:
        return purchased_chatbot_plan_service.get_valid_chat_credits(chatbot.id)
    return purchased_chatbot_plan_service.get_all_by_chatbot_id(chatbot.id)


@router.get('/{chatbot_id}/transaction', response_model=List[ChatBotTransaction])
def get_chatbot_transactions(
    chatbot_id: UUID4,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)

    return chatbot_transaction_service.get_all_by_chatbot_id(chatbot.id)


@router.get('/{chatbot_id}/plans/{plan_uuid}/buy', response_model=ChatBotTransaction)
def buy_plan(
    chatbot_id: UUID4,
    chatbot_plan_id: UUID4,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    chatbot_plan_service: ChatBotPlanService = Depends(get_service(ChatBotPlanService)),
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)\

    chatbot_plan = chatbot_plan_service.validator.validate_exists(uuid=chatbot_plan_id,
                                                                  model=ChatBotPlan)

    return chatbot_transaction_service.add(
        ChatBotTransactionCreate(chatbot_id=chatbot.id, price=chatbot_plan.price,
                                 title=chatbot_plan.title,
                                 extend_chat_count=chatbot_plan.extend_chat_count,
                                 extend_days=chatbot_plan.extend_days,
                                 extend_token_count=chatbot_plan.extend_token_count,
                                 is_extra=chatbot_plan.is_extra))


@router.get('/{chatbot_id}/transaction/{transaction_id}/pay')
def pay_plan(
    chatbot_id: UUID4,
    transaction_id: UUID4,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id, model=ChatBot)
    chatbot_service.validator.validate_user_ownership(chatbot, current_user)

    transaction = chatbot_transaction_service.validator.validate_exists(
        uuid=transaction_id, model=ChatBotTransaction)

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

    chatbot_transaction_service.update(transaction, {"payment_authority": result.Authority})

    return RedirectResponse(url=f"{settings.ZARINPAL_BASE_URL}/{result.Authority}")


@router.get('/transaction/{transaction_id}/verify')
def verify_payment(
    transaction_id: UUID4,
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
    purchased_chatbot_plan_service: PurchasedChatbotPlanService = Depends(
        get_service(ChatBotTransactionService)),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    from app.llms.models.credit import ChatBotTransaction

    transaction: ChatBotTransaction = chatbot_transaction_service.validator.validate_exists(
        uuid=transaction_id, model=ChatBotTransaction)

    if transaction.is_paid:
        raise BusinessLogicError(detail="Transaction has been already paid.")

    zarin_client = Client(settings.ZARINPAL_WEBSERVICE)
    result = zarin_client.service.PaymentVerification(
        settings.ZARINPAL_MERCHANT_ID,
        transaction.payment_authority,
        transaction.amount,
    )

    if result.Status not in [100, 101]:
        raise BusinessLogicError("Invalid payment")

    if result.Status == 101:
        return
    now = datetime.utcnow()

    purchased_chatbot_plan_service.add(
        PurchasedChatBotPlanCreate(
            chatbot_id=transaction.chatbot_id,
            from_datetime=now,
            to_datetime=now + timedelta(days=transaction.extend_days),
            is_extra=transaction.is_extra,
            remaining_chat_count=transaction.extend_chat_count,
            remaining_token_count=transaction.extend_token_count,
        ))
