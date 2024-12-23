from fastapi import APIRouter

from app.llms.api import chatbot_api, chatbot_telegram_bot_api, knowledge_base_api, credit_api

routers = APIRouter()
router_list = [chatbot_api.router, knowledge_base_api.router,
               chatbot_telegram_bot_api.router, credit_api.router]

for router in router_list:
    routers.include_router(router)
