from pydantic import UUID4, BaseModel


class ChatbotConnectTelegramBotRequest(BaseModel):
    chatbot_id: UUID4


class ChatbotConnectTelegramBot(BaseModel):
    chatbot_id: UUID4
    telegram_bot_id: UUID4
