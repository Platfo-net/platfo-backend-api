from fastapi import APIRouter

from app.api.api_v1.routers.notifier import campaign

router = APIRouter(prefix='/notifier', tags=['Notifier'])

router.include_router(campaign.router)
