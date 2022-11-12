from fastapi import APIRouter

from app.api.api_v1.routers.live_chat import contact, message


router = APIRouter(prefix="/live-chat", tags=["Live Chat"])

router.include_router(contact.router)
router.include_router(message.router)
