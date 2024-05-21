from fastapi import APIRouter

from app.api.api_v1.routers import (auth, constants, credit_api, dev_utils,
                                    file, instagram, notification, shop_api,
                                    telegram_bot, users, webhook , message_builder)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(instagram.router)
api_router.include_router(credit_api.router)
api_router.include_router(webhook.router)
api_router.include_router(notification.router)
api_router.include_router(telegram_bot.router)
api_router.include_router(shop_api.router)
api_router.include_router(message_builder.router)
api_router.include_router(dev_utils.router)

api_router.include_router(file.router)
api_router.include_router(constants.router)
