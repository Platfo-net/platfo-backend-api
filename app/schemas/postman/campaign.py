from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.pagination import Pagination


class CampaignCreate(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: str = None


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

class CampaignListApi(BaseModel):
    pagination : Pagination
    items : List[Campaign]
    