from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.pagination import Pagination
from.campaign_contact import CampaignContactCreate


class CampaignCreate(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: str = None
    is_draft: bool = True
    content: dict = {}


class CampaignUpdate(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: str = None
    content: dict = None
    is_draft: bool = False


class Campaign(BaseModel):
    name: str = None
    description: str = None
    created_at: datetime = None
    status: str = None
    is_draft: bool = False
    group_name: str = None


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
    contacts: List[CampaignContactCreate]
