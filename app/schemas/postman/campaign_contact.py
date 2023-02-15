from pydantic import BaseModel, UUID4


class CampaignContactCreate(BaseModel):
    contact_id: int = None
    contact_igs_id: str = None


class CampaignContactUpdate(BaseModel):
    pass
