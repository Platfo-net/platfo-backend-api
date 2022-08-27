from app.api.api_v1.routers import auth, connection, \
    instagram, trigger, chatflow, node, \
    users, accounts, constants, webhook, contact , message, notification
from fastapi import APIRouter


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(instagram.router)
api_router.include_router(accounts.router)
api_router.include_router(connection.router)
api_router.include_router(chatflow.router)
api_router.include_router(node.router)
api_router.include_router(trigger.router)
api_router.include_router(contact.router)
api_router.include_router(message.router)
api_router.include_router(constants.router)
api_router.include_router(webhook.router)
api_router.include_router(notification.router)
