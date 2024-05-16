from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from suds.client import Client

from app import models
from app.api import deps
from app.constants.currency import Currency
from app.constants.role import Role
from app.core.config import settings
from app.llms.models.credit import ChatBotTransaction
from app.llms.schemas.credit_schema import ChatBotCreditCreate, ChatBotCreditSchema, \
    ChatBotTransactionCreate, ChatBotTransactionItem, TransactionUpdate
from app.llms.services.credit_service import ChatBotTransactionService, UserChatBotCreditService
from app.llms.utils.dependencies import get_service
from app.llms.utils.exceptions import BusinessLogicError

router = APIRouter(
    prefix="/chatbot-credit",
    tags=["Chatbot Credit"],
)


@router.get('/credit', response_model=ChatBotCreditSchema)
def get_chatbot_credit(
    chatbot_credit_service: UserChatBotCreditService = Depends(
        get_service(UserChatBotCreditService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    user_credit = chatbot_credit_service.get_by_user_id(current_user.id)
    if not user_credit:
        user_credit = chatbot_credit_service.add(
            ChatBotCreditCreate(
                amount=0,
                currency=Currency.IRT["value"],
                user_id=current_user.id,
            ))

    return user_credit


@router.get('/transactions', response_model=List[ChatBotTransactionItem])
def get_transactions(
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    transactions = chatbot_transaction_service.get_all_by_user_id(current_user.id)
    return transactions


@router.get('/buy', response_model=ChatBotTransactionItem)
def buy_credit(
    amount: int,
    currency: str,
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    if currency not in Currency.items.keys():
        raise BusinessLogicError("Invalid currency")

    return chatbot_transaction_service.add(
        ChatBotTransactionCreate(amount=amount, currency=currency, user_id=current_user.id))


@router.get('/{transaction_id}/pay')
def pay_transaction(
    transaction_id: UUID4,
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):

    transaction: ChatBotTransaction = chatbot_transaction_service.validator.validate_exists(
        uuid=transaction_id, model=ChatBotTransaction)

    if transaction.is_paid:
        raise BusinessLogicError(detail="Transaction has been already paid.")

    d = datetime.now() - timedelta(days=2)
    if transaction.created_at < d:
        raise BusinessLogicError(detail="Old Transaction.")

    zarrin_client = Client(settings.ZARINPAL_WEBSERVICE)
    callback = f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/chatbot-credit/transaction/{transaction.uuid}/verify"  # noqa
    result = zarrin_client.service.PaymentRequest(
        settings.ZARINPAL_MERCHANT_ID,
        transaction.amount,
        f"پرداخت بابت خرید پلن {transaction.title}",
        "",
        "",
        callback,
    )

    chatbot_transaction_service.update(transaction, {"payment_authority": result.Authority})

    return {"redirect_url": f"{settings.ZARINPAL_BASE_URL}/{result.Authority}"}
    # RedirectResponse(url=f"{settings.ZARINPAL_BASE_URL}/{result.Authority}")


@router.get('/transaction/{transaction_id}/verify', status_code=status.HTTP_200_OK)
def verify_payment(
    transaction_id: UUID4,
    chatbot_credit_service: UserChatBotCreditService = Depends(
        get_service(UserChatBotCreditService)),
    chatbot_transaction_service: ChatBotTransactionService = Depends(
        get_service(ChatBotTransactionService)),
):

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
    chatbot_transaction_service.update(transaction, TransactionUpdate(
        is_paid=True,
        payed_at=now,
    ))

    chatbot_credit_service.add_credit(transaction.user_id, transaction.amount)
