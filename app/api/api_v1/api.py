from app.api.api_v1.routers import (
    auth,
    connection,
    file,
    instagram,
    users,
    accounts,
    constants,
    webhook,
    notification,
    academy,
    websocket,
    live_chat_api,
    bot_builder_api,
    postman
)
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(websocket.router)
api_router.include_router(users.router)
api_router.include_router(instagram.router)
api_router.include_router(accounts.router)
api_router.include_router(connection.router)
api_router.include_router(bot_builder_api.router)
api_router.include_router(webhook.router)
api_router.include_router(notification.router)
api_router.include_router(live_chat_api.router)
api_router.include_router(postman.router)
api_router.include_router(academy.router)

api_router.include_router(file.router)
api_router.include_router(constants.router)
