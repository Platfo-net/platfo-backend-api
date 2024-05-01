from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel


class ChatBotCreditSchema(BaseModel):
    from_datetime: Optional[datetime]
    to_datetime: Optional[datetime]
    is_extra: Optional[bool]
    remaining_chat_count: Optional[int]
    remaining_token_count: Optional[int]

    class Config:
        orm_mode = True


class ChatBotPlanFeature(BaseModel):
    title: Optional[str] = None

    class Config:
        orm_mode = True


class ChatBotPlan(BaseModel):
    uuid: Optional[UUID4]
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_extra: Optional[bool] = None
    extend_days: Optional[int] = None
    extend_chat_count: Optional[int] = None
    extend_token_count: Optional[int] = None
    original_price: Optional[float] = None
    currency: Optional[str] = None

    features: List[ChatBotPlanFeature]

    class Config:
        orm_mode = True


class ChatBotTransaction(BaseModel):
    uuid: Optional[UUID4]
    amount: Optional[float] = None
    title: Optional[str] = None
    currency: Optional[str] = None
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    is_paid: Optional[bool] = None
    is_extra: Optional[bool] = None
    extend_days: Optional[int] = 0
    extend_chat_count: Optional[int] = 0
    extend_token_count: Optional[int] = 0


class ChatBotTransactionCreate(BaseModel):
    chatbot_id: int
    amount: float
    title: str
    is_extra: Optional[bool] = None
    extend_days: Optional[int] = 0
    extend_chat_count: Optional[int] = 0
    extend_token_count: Optional[int] = 0


class PurchasedChatBotPlanCreate(BaseModel):
    chatbot_id: int
    from_datetime: Optional[datetime] = None
    to_datetime: Optional[datetime] = None
    is_extra: Optional[bool] = False
    remaining_chat_count: Optional[int] = 0
    remaining_token_count: Optional[int] = 0
