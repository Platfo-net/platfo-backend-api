from pydantic import BaseModel


class CampaignCreate(BaseModel):
    name: str = None
    description: str = None
    facebook_page_id: str = None
