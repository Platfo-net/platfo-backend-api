from typing import Optional

from pydantic import BaseModel

from app.llms.schemas.base_schema import ModelBaseInfo


class BaseChatBot(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    user_id: Optional[int] = None

    class Config:
        orm_mode = True


class ChatBotCreate(BaseChatBot):
    ...


class ChatBotUpdate(BaseChatBot):
    ...


class ChatBot(ModelBaseInfo, BaseChatBot):
    ...
