from fastapi import APIRouter

from app.api.api_v1.routers.notifier import campaign, group

router = APIRouter(prefix='/notifier', tags=['Notifier'])

router.include_router(group.router)
router.include_router(campaign.router)
