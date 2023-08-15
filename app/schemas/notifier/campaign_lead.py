from pydantic import BaseModel


class CampaignLeadCreate(BaseModel):
    lead_id: int = None
    lead_igs_id: str = None


class CampaignLeadUpdate(BaseModel):
    pass
