from pydantic import UUID4, BaseModel


class ChatbotConnectTelegramBotRequest(BaseModel):
    chatbot_id: UUID4
