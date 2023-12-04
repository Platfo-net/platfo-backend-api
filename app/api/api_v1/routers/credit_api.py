from fastapi import APIRouter

from app.api.api_v1.routers.credit import invoice, plan , credit

router = APIRouter(prefix='/credit', tags=['Credit'], include_in_schema=True)

router.include_router(credit.router)
router.include_router(plan.router)
router.include_router(invoice.router)
