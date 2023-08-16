from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.account import Account
from app.schemas.media import Image
from app.schemas.pagination import Pagination
from datetime import date


class CampaignLeadsCriteria(BaseModel):
    is_user_follow_business: Optional[bool] = None
    from_date: Optional[date] = None


class CampaignCreate(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: str = None
    is_draft: bool = True
    content: dict = None
    image: str = None
    leads_criteria: CampaignLeadsCriteria


class CampaignUpdate(BaseModel):
    name: str = None
    description: str = None
    content: dict = None
    is_draft: bool = False
    image: str = None
    leads_criteria: CampaignLeadsCriteria


class Campaign(BaseModel):
    id: UUID4
    name: str = None
    description: str = None
    created_at: datetime = None
    status: str = None
    is_draft: bool = False
    image: Optional[Image] = None
    leads_criteria: CampaignLeadsCriteria


class CampaignDetail(Campaign):
    id: UUID4
    facebook_page_id: str = None
    account: Account
    content: dict = None
    user_id: UUID4
    sent_count: int = 0
    seen_count: int = 0
    total_lead_count: int = 0


class CampaignListApi(BaseModel):
    items: List[Campaign]
    pagination: Pagination


class CampaignCreateApiSchema(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: int = None
    content: dict = None
    is_draft: bool = True
    image: str = None
    leads_criteria: CampaignLeadsCriteria
