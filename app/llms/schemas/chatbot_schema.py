from typing import Optional

from pydantic import BaseModel, Field

from app.llms.schemas.base_schema import ModelBaseInfo


class BaseChatBot(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None

    class Config:
        orm_mode = True


class ChatBotCreate(BaseChatBot):
    ...


class ChatBotUpdate(BaseChatBot):
    prompt: Optional[str] = None
    temperature: Optional[float] = Field(default=0, ge=0, le=1)


class ChatBot(ModelBaseInfo, ChatBotUpdate):
    ...
