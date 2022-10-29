from typing import Any

from pydantic import BaseModel, UUID4


class CampaignContactCreate(BaseModel):
    contact_id: UUID4 = None
    contact_igs_id: str = None


class CampaignContactUpdate(BaseModel):
    pass
