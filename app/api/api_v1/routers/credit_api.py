from fastapi import APIRouter

from app.api.api_v1.routers.credit import plan


router = APIRouter(prefix="/credit", tags=["Credit"], include_in_schema=True)

router.include_router(plan.router)
