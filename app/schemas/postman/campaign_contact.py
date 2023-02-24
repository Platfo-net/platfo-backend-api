from pydantic import BaseModel


class CampaignContactCreate(BaseModel):
    contact_id: int = None
    contact_igs_id: str = None


class CampaignContactUpdate(BaseModel):
    pass
