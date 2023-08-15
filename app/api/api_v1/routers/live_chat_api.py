from fastapi import APIRouter

from app.api.api_v1.routers.live_chat import lead, message

router = APIRouter(prefix='/live-chat', tags=['Live Chat'])

router.include_router(lead.router)
router.include_router(message.router)
