from fastapi import APIRouter

from app.api.api_v1.routers.bot_builder import chatflow, chatflow_ui, node

router = APIRouter(prefix="/bot-builder", tags=["Bot Builder"], include_in_schema=False)

router.include_router(chatflow.router)
router.include_router(chatflow_ui.router)
router.include_router(node.router)
