from pydantic import BaseModel

from app.llms.schemas.base_schema import ModelBaseInfo


class BaseChatBot(BaseModel):
    name: str
    description: str
    prompt: str
    user_id: int

    class Config:
        orm_mode = True


class ChatBotCreate(BaseChatBot):
    ...


class ChatBot(ModelBaseInfo, BaseChatBot):
    ...
