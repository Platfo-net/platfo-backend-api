from datetime import datetime
from typing import List
from pydantic import BaseModel, UUID4

from app.schemas.pagination import Pagination
from app.schemas.account import Account


class CampaignCreate(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: str = None
    is_draft: bool = True
    content: dict = None


class CampaignUpdate(BaseModel):
    name: str = None
    description: str = None
    content: dict = None
    is_draft: bool = False


class Campaign(BaseModel):
    name: str = None
    description: str = None
    created_at: datetime = None
    status: str = None
    is_draft: bool = False
    group_name: str = None


class CampaignDetail(Campaign):
    id: UUID4
    facebook_page_id: str = None
    account: Account
    content: dict = None
    user_id: UUID4
    contacts: List = None
    sent_count: int = 0
    seen_count: int = 0
    total_contact_count: int = 0


class CampaignListApi(BaseModel):
    pagination: Pagination
    items: List[Campaign]


class CampaignCreateApiSchema(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: str = None
    group_id: str = None
    content: dict = None
    is_draft: bool = True
