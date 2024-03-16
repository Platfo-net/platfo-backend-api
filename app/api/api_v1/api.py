from fastapi import APIRouter

from app.api.api_v1.routers import (accounts, auth, bot_builder_api,
                                    connection, constants, credit_api,
                                    databoard, dev_utils, file, instagram,
                                    live_chat_api, notification, notifier_api,
                                    shop_api, telegram_bot, users, webhook)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(instagram.router)
api_router.include_router(accounts.router)
api_router.include_router(credit_api.router)
api_router.include_router(connection.router)
api_router.include_router(bot_builder_api.router)
api_router.include_router(webhook.router)
api_router.include_router(notification.router)
api_router.include_router(live_chat_api.router)
api_router.include_router(notifier_api.router)
api_router.include_router(databoard.router)
api_router.include_router(telegram_bot.router)
api_router.include_router(shop_api.router)
api_router.include_router(dev_utils.router)

api_router.include_router(file.router)
api_router.include_router(constants.router)
