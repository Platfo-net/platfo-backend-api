from fastapi import APIRouter
from app.api.api_v1.routers.postman import campaign_contact, campaign, group


router = APIRouter(prefix="/postman", tags=["Postman"])

router.include_router(group.router)
router.include_router(campaign.router)
router.include_router(campaign_contact.router)
